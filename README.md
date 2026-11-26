# Nand to Tetris – I Capstone Project: Make the Computer Draw a Box

**Course:** ETCCNT301 | **School of Engineering & Technology, K.R. Mangalam University**  
**Student:** Vansh Negi | **Roll Number:** `2501730158` | **Personal Number ($K$):** `58`

---

## Project Overview

This folder contains the complete Capstone Project for **Nand to Tetris – I** customized for $K = 58$:

- **Part A – Build the Computer:** Implemented `Memory.hdl`, `CPU.hdl`, and `Computer.hdl`. Verified against all five Project 5 test suites (`Memory.tst`, `CPU.tst`, `ComputerAdd.tst`, `ComputerMax.tst`, `ComputerRect.tst`) in the official Nand2Tetris Web IDE Hardware Simulator.
- **Part B – Hack Assembler:** Python two-pass assembler (`assembler.py`) with predefined symbols, label resolution, variable allocation starting at RAM[16], and the student-specific feature ($K \bmod 3 = 1$: graceful line-number error reporting without crashing).
- **Part C – Interactive Box Program:** Hack assembly program (`Box.asm`) and assembled 16-bit binary (`Box.hack`, 53 instructions). Renders a **48px × 20px** black box starting at **row 58** on the left edge while any key is pressed, and clears the box when released.

---

## Student-Specific Parameters ($K = 58$)

- **Roll Number:** `2501730158` $\implies$ Last two digits: **$K = 58$**
- **$K \bmod 3 = 58 \bmod 3 = 1$:** For an invalid line, print a clear diagnostic with the line number (e.g., `Line 7: invalid instruction ...`) instead of crashing.
- **$K \bmod 4 = 58 \bmod 4 = 2$:** Box width $= 16 \times ((58 \bmod 4) + 1) = 16 \times 3 = \mathbf{48\text{ pixels}}$ (**3 words per row**).
- **Starting Row:** Row $K = 58$ (Screen RAM address: $\text{SCREEN} + 32 \times 58 = 16384 + 1856 = \mathbf{18240}$).
- **Box Height:** **20 rows** tall (rows `58` through `77` inclusive).
- **Memory Span:** Words `18240..18242` (row 58) down to `18848..18850` (row 77) — **60 screen words** total.

---

## Folder Structure

```text
nand2tetris_capstone_k58/
├── CPU.hdl                     # Part A: Hack CPU implementation
├── Memory.hdl                  # Part A: Memory-mapped I/O (RAM16K, Screen, Keyboard)
├── Computer.hdl                # Part A: Top-level Hack Computer chip
├── assembler.py                # Part B: Two-pass Hack assembler (K mod 3 = 1 feature)
├── test_assembler.py           # Part B & C: Automated unit & CPU simulation tests
├── Box.asm                     # Part C: Interactive K=58 box program (48x20 at row 58)
├── Box.hack                    # Part C: Assembled 16-bit machine code (53 instructions)
├── BoxTest.tst                 # Automated test script for CPUEmulator
├── BoxTest.cmp                 # Expected RAM comparison output for BoxTest.tst
├── symbols.txt                 # Exported symbol table from Box.asm
├── REPORT.md                   # Complete project report (Markdown)
├── REPORT.html                 # Printable project report (HTML - Print to PDF)
├── VIVA_PREPARATION.md         # Viva defense & live modification guide
└── screenshots/
    ├── cpu_test_pass.png
    ├── memory_test_pass.png
    ├── computer_add_pass.png
    ├── computer_max_pass.png
    ├── computer_rect_pass.png
    ├── assembler_verification.png
    └── cpu_emulator_box.png
```

---

## How to Run & Verify

### 1. Part A — Hardware Verification (Web IDE or Desktop HardwareSimulator)
Load `Memory.hdl`, `CPU.hdl`, and `Computer.hdl` into Project 5 of the [Nand2Tetris Web IDE](https://nand2tetris.github.io/web-ide/chip/) (or run `HardwareSimulator` with `Memory.tst`, `CPU.tst`, `ComputerAdd.tst`, `ComputerMax.tst`, `ComputerRect.tst`).

### 2. Part B — Assembler & Unit Tests
```zsh
# Assemble Box.asm and export symbols.txt
python3 assembler.py Box.asm Box.hack --symbols

# Run automated unit + CPU simulation test suite
python3 -m unittest discover -p "test_*.py" -v
```

### 3. Part C — Box Program in CPU Emulator
- Open the [Nand2Tetris CPU Emulator](https://nand2tetris.github.io/web-ide/cpu/), load `Box.hack`, set speed to **Fast**, click **Enable Keyboard**, and hold any key (e.g., `K`) to see the **48 × 20** black rectangle appear at row 58 on the left edge.
- Or run `CPUEmulator BoxTest.tst` for automated memory verification.
