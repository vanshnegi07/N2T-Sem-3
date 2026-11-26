#!/usr/bin/env python3
"""
Hack Assembler for Nand to Tetris (Part B)
Student: Vansh Negi | Roll Number: 2501730158 | K = 58
Feature (K mod 3 = 1): Graceful line-number error reporting without crashing.
"""
import sys
import os
import re

PREDEFINED_SYMBOLS = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
}
for i in range(16):
    PREDEFINED_SYMBOLS[f"R{i}"] = i

COMP_TABLE = {
    "0":   "0101010",
    "1":   "0111111",
    "-1":  "0111010",
    "D":   "0001100",
    "A":   "0110000",
    "!D":  "0001101",
    "!A":  "0110001",
    "-D":  "0001111",
    "-A":  "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M":   "1110000",
    "!M":  "1110001",
    "-M":  "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}

DEST_TABLE = {
    "":    "000",
    "M":   "001",
    "D":   "010",
    "MD":  "011",
    "DM":  "011",
    "A":   "100",
    "AM":  "101",
    "AD":  "110",
    "AMD": "111",
}

JUMP_TABLE = {
    "":    "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

SYMBOL_REGEX = re.compile(r"^[a-zA-Z_.$:][a-zA-Z0-9_.$:]*$")


class HackAssembler:
    def __init__(self, save_symbols=False, warn_duplicate_labels=True):
        self.symbol_table = dict(PREDEFINED_SYMBOLS)
        self.next_var_address = 16
        self.save_symbols = save_symbols
        self.warn_duplicate_labels = warn_duplicate_labels
        self.errors = []

    @staticmethod
    def clean_line(line: str) -> str:
        comment_idx = line.find("//")
        if comment_idx != -1:
            line = line[:comment_idx]
        return line.strip()

    def assemble(self, asm_filepath: str, output_filepath: str = None) -> bool:
        if not os.path.exists(asm_filepath):
            print(f"Error: File '{asm_filepath}' not found.", file=sys.stderr)
            return False

        if output_filepath is None:
            base, _ = os.path.splitext(asm_filepath)
            output_filepath = base + ".hack"

        with open(asm_filepath, "r", encoding="utf-8", errors="replace") as f:
            raw_lines = f.readlines()

        self.errors = []
        self.symbol_table = dict(PREDEFINED_SYMBOLS)
        self.next_var_address = 16

        rom_address = 0
        cleaned_instructions = []

        # Pass 1: Strip comments/whitespace and record label ROM addresses
        for line_num, raw_line in enumerate(raw_lines, start=1):
            cleaned = self.clean_line(raw_line)
            if not cleaned:
                continue

            if cleaned.startswith("(") or cleaned.endswith(")"):
                if not (cleaned.startswith("(") and cleaned.endswith(")")):
                    self.errors.append((line_num, f"Line {line_num}: invalid instruction '{cleaned}' (malformed label parentheses)"))
                    continue

                label = cleaned[1:-1].strip()
                if not label:
                    self.errors.append((line_num, f"Line {line_num}: invalid empty label declaration '()'"))
                    continue

                if not SYMBOL_REGEX.match(label):
                    self.errors.append((line_num, f"Line {line_num}: invalid label identifier '{label}'"))
                    continue

                if label in self.symbol_table and self.warn_duplicate_labels:
                    print(
                        f"Warning: Line {line_num}: label '({label})' already defined. Overwriting.",
                        file=sys.stderr,
                    )
                self.symbol_table[label] = rom_address
            else:
                cleaned_instructions.append((line_num, cleaned))
                rom_address += 1

        # Pass 2: Translate instructions and resolve variables
        machine_code_lines = []

        for line_num, instr in cleaned_instructions:
            if instr.startswith("@"):
                value_part = instr[1:].strip()
                if not value_part:
                    self.errors.append(
                        (line_num, f"Line {line_num}: invalid instruction '{instr}' (missing address/symbol after '@')")
                    )
                    continue

                if value_part.isdigit():
                    val = int(value_part)
                    if val < 0 or val > 32767:
                        self.errors.append(
                            (line_num, f"Line {line_num}: invalid instruction '{instr}' (constant {val} out of range 0..32767)")
                        )
                        continue
                    machine_code_lines.append(format(val, "016b"))
                else:
                    if not SYMBOL_REGEX.match(value_part):
                        self.errors.append(
                            (line_num, f"Line {line_num}: invalid instruction '{instr}' (invalid symbol name '{value_part}')")
                        )
                        continue

                    if value_part not in self.symbol_table:
                        self.symbol_table[value_part] = self.next_var_address
                        self.next_var_address += 1

                    val = self.symbol_table[value_part]
                    machine_code_lines.append(format(val, "016b"))
            else:
                dest_part = ""
                comp_part = ""
                jump_part = ""
                rest = instr

                if "=" in rest:
                    dest_part, rest = rest.split("=", 1)
                    dest_part = dest_part.strip()

                if ";" in rest:
                    comp_part, jump_part = rest.split(";", 1)
                    comp_part = comp_part.strip()
                    jump_part = jump_part.strip()
                else:
                    comp_part = rest.strip()

                if comp_part not in COMP_TABLE:
                    self.errors.append(
                        (line_num, f"Line {line_num}: invalid instruction '{instr}' (unrecognized computation '{comp_part}')")
                    )
                    continue

                if dest_part not in DEST_TABLE:
                    self.errors.append(
                        (line_num, f"Line {line_num}: invalid instruction '{instr}' (unrecognized destination '{dest_part}')")
                    )
                    continue

                if jump_part not in JUMP_TABLE:
                    self.errors.append(
                        (line_num, f"Line {line_num}: invalid instruction '{instr}' (unrecognized jump directive '{jump_part}')")
                    )
                    continue

                binary_code = "111" + COMP_TABLE[comp_part] + DEST_TABLE[dest_part] + JUMP_TABLE[jump_part]
                machine_code_lines.append(binary_code)

        if self.errors:
            self.errors.sort(key=lambda item: item[0])
            self.errors = [msg for _, msg in self.errors]
            print(f"Assembly failed with {len(self.errors)} error(s):", file=sys.stderr)
            for err in self.errors:
                print(f"  {err}", file=sys.stderr)
            return False

        with open(output_filepath, "w", encoding="utf-8") as f:
            for code in machine_code_lines:
                f.write(code + "\n")

        if self.save_symbols:
            out_dir = os.path.dirname(output_filepath) or "."
            symbols_file = os.path.join(out_dir, "symbols.txt")
            with open(symbols_file, "w", encoding="utf-8") as f:
                f.write("# Symbol\tAddress\n")
                for sym, addr in sorted(self.symbol_table.items(), key=lambda item: (item[1], item[0])):
                    f.write(f"{sym}\t{addr}\n")

        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 assembler.py <source.asm> [output.hack] [--symbols]")
        sys.exit(1)

    asm_file = sys.argv[1]
    out_file = None
    save_sym = "--symbols" in sys.argv

    if len(sys.argv) >= 3 and not sys.argv[2].startswith("--"):
        out_file = sys.argv[2]

    assembler = HackAssembler(save_symbols=save_sym)
    success = assembler.assemble(asm_file, out_file)
    if success:
        target = out_file if out_file else os.path.splitext(asm_file)[0] + ".hack"
        print(f"Success: Generated {target}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
