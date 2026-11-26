#!/usr/bin/env python3
"""
Automated verification suite for assembler.py (Part B) and Box.hack (Part C) for K = 58.
"""
import os
import tempfile
import unittest
from assembler import HackAssembler


class TestHackAssemblerAndBox(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _assemble_text(self, asm_text):
        asm_path = os.path.join(self.tmpdir.name, "test.asm")
        hack_path = os.path.join(self.tmpdir.name, "test.hack")
        with open(asm_path, "w", encoding="utf-8") as f:
            f.write(asm_text)
        asm = HackAssembler(warn_duplicate_labels=False)
        ok = asm.assemble(asm_path, hack_path)
        lines = []
        if ok:
            with open(hack_path, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
        return ok, lines, asm.errors, asm.symbol_table

    def test_add_program(self):
        asm_text = """
        // Computes R0 = 2 + 3
        @2
        D=A
        @3
        D=D+A
        @0
        M=D
        """
        ok, lines, errors, _ = self._assemble_text(asm_text)
        self.assertTrue(ok, errors)
        expected = [
            "0000000000000010",  # @2
            "1110110000010000",  # D=A
            "0000000000000011",  # @3
            "1110000010010000",  # D=D+A
            "0000000000000000",  # @0
            "1110001100001000",  # M=D
        ]
        self.assertEqual(lines, expected)

    def test_max_program_symbols_and_labels(self):
        asm_text = """
            @R0
            D=M
            @R1
            D=D-M
            @OUTPUT_FIRST
            D;JGT
            @R1
            D=M
            @OUTPUT_D
            0;JMP
        (OUTPUT_FIRST)
            @R0
            D=M
        (OUTPUT_D)
            @R2
            M=D
        (INFINITE_LOOP)
            @INFINITE_LOOP
            0;JMP
        """
        ok, lines, errors, sym = self._assemble_text(asm_text)
        self.assertTrue(ok, errors)
        self.assertEqual(len(lines), 16)
        self.assertEqual(sym["OUTPUT_FIRST"], 10)
        self.assertEqual(sym["OUTPUT_D"], 12)
        self.assertEqual(sym["INFINITE_LOOP"], 14)

    def test_k_mod_3_equals_1_graceful_error_reporting(self):
        bad_asm = (
            "// Line 1 comment\n"
            "@2\n"
            "D=A\n"
            "@\n"                    # Line 4: missing symbol
            "@40000\n"               # Line 5: out of range
            "(BAD\n"                 # Line 6: malformed parentheses
            "D=INVALID+COMP;JMP\n"   # Line 7: invalid computation
            "dest_missing=\n"        # Line 8: invalid computation
            "M=D;BADJMP\n"           # Line 9: invalid jump
            "Q=D\n"                  # Line 10: invalid dest
        )
        ok, _, errors, _ = self._assemble_text(bad_asm)
        self.assertFalse(ok)
        joined = "\n".join(errors)
        for line_no in [4, 5, 6, 7, 8, 9, 10]:
            self.assertIn(f"Line {line_no}:", joined)

    def test_box_asm_assembles_and_runs_k58(self):
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        box_asm = os.path.join(repo_dir, "Box.asm")
        out_hack = os.path.join(self.tmpdir.name, "Box.hack")
        asm = HackAssembler(save_symbols=True)
        ok = asm.assemble(box_asm, out_hack)
        self.assertTrue(ok, asm.errors)
        with open(out_hack, "r", encoding="utf-8") as f:
            rom = [int(ln.strip(), 2) for ln in f if ln.strip()]

        # Verify K=58 constants embedded in ROM:
        # 18240 = 16384 + 32*58, height = 20, width = 3 words (48 px)
        self.assertIn(18240, rom)
        self.assertIn(20, rom)
        self.assertIn(3, rom)

        # Simulate Hack CPU for key pressed vs released
        def run_cpu(rom_words, kbd_val, cycles=2000):
            ram = [0] * 24577
            ram[24576] = kbd_val
            A = 0
            D = 0
            PC = 0
            for _ in range(cycles):
                inst = rom_words[PC]
                if (inst & 0x8000) == 0:
                    A = inst & 0x7FFF
                    PC += 1
                else:
                    a_bit = (inst >> 12) & 1
                    comp = (inst >> 6) & 0x3F
                    dest = (inst >> 3) & 0x7
                    jump = inst & 0x7
                    x = D
                    y = ram[A] if a_bit else A
                    if comp == 0b101010: out = 0
                    elif comp == 0b111111: out = 1
                    elif comp == 0b111010: out = -1
                    elif comp == 0b001100: out = x
                    elif comp == 0b110000: out = y
                    elif comp == 0b001101: out = ~x
                    elif comp == 0b110001: out = ~y
                    elif comp == 0b001111: out = -x
                    elif comp == 0b110011: out = -y
                    elif comp == 0b011111: out = x + 1
                    elif comp == 0b110111: out = y + 1
                    elif comp == 0b001110: out = x - 1
                    elif comp == 0b110010: out = y - 1
                    elif comp == 0b000010: out = x + y
                    elif comp == 0b010011: out = x - y
                    elif comp == 0b000111: out = y - x
                    elif comp == 0b000000: out = x & y
                    elif comp == 0b010101: out = x | y
                    else:
                        raise ValueError(f"Unknown comp: {bin(comp)}")
                    # 16-bit signed wrap
                    out = ((out + 32768) & 0xFFFF) - 32768
                    if dest & 1:
                        ram[A] = out
                    if dest & 2:
                        D = out
                    if dest & 4:
                        A = out & 0x7FFF
                    zr = (out == 0)
                    ng = (out < 0)
                    pos = (not zr and not ng)
                    do_jump = (
                        ((jump & 4) and ng)
                        or ((jump & 2) and zr)
                        or ((jump & 1) and pos)
                    )
                    PC = A if do_jump else PC + 1
            return ram

        # Key pressed (RAM[24576] = 75 'K')
        ram_pressed = run_cpu(rom, 75, cycles=2500)
        for r in range(58, 78):
            base = 16384 + 32 * r
            for c in range(3):
                self.assertEqual(ram_pressed[base + c], -1, f"Row {r} col {c} should be -1")
            self.assertEqual(ram_pressed[base + 3], 0, f"Row {r} col 3 should stay 0")
        # Row 57 (above) and Row 78 (below) must stay 0
        self.assertEqual(ram_pressed[16384 + 32 * 57], 0)
        self.assertEqual(ram_pressed[16384 + 32 * 78], 0)

        # Key released (RAM[24576] = 0)
        ram_released = run_cpu(rom, 0, cycles=2500)
        for r in range(58, 78):
            base = 16384 + 32 * r
            for c in range(3):
                self.assertEqual(ram_released[base + c], 0, f"Row {r} col {c} should reset to 0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
