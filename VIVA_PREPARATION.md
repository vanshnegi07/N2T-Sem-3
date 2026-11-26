# Viva Preparation Guide ($K = 58$)

**Student:** Vansh Negi | **Roll Number:** `2501730158` | **$K$:** `58`

---

## 1. Core Parameter Derivation
- **Last 2 digits of Roll No:** $K = 58$
- **Assembler Feature ($K \bmod 3$):** $58 \bmod 3 = 1 \implies$ print clear line-numbered error messages (e.g., `Line 7: invalid instruction ...`) instead of crashing.
- **Box Width ($K \bmod 4$):** $58 \bmod 4 = 2 \implies 16 \times (2 + 1) = \mathbf{48\text{ pixels}} = \mathbf{3\text{ words/row}}$.
- **Starting Row:** Row $58 \implies \text{Base Address} = 16384 + 32 \times 58 = \mathbf{18240}$.
- **Box Height:** $20$ rows (rows `58` through `77`, ending row base address `18848`, last word `18850`).

---

## 2. Live Code Modification Recipes

1. **"Move the box down by 20 rows"**
   - New starting row: $58 + 20 = 78$.
   - New address: $16384 + 32 \times 78 = 16384 + 2496 = \mathbf{18880}$.
   - Edit `Box.asm`: change `@18240` to `@18880`, then run `python3 assembler.py Box.asm Box.hack`.

2. **"Make the box 64 pixels wide (or 80 pixels wide)"**
   - 64 pixels = 4 words $\implies$ change `@3` (`col_count`) to `@4`.
   - 80 pixels = 5 words $\implies$ change `@3` to `@5`.

3. **"Make the box 30 or 40 rows tall"**
   - Change `@20` (`row_count`) to `@30` or `@40`.

4. **"Show the box normally and hide it while a key is pressed"**
   - Under `(SET_BLACK)` set `M=0`, and under `(SET_WHITE)` set `M=-1`.

5. **"Trigger your K mod 3 = 1 assembler feature"**
   - Create a `.asm` file with an invalid line like `D=FOO;JMP` on line 7 and run `python3 assembler.py test.asm`. It prints `Line 7: invalid instruction 'D=FOO;JMP' ...` to `stderr` and exits with code `1` without a traceback.

---

## 3. Architecture Questions
- **Why `32` per row?** Screen is 512 pixels wide and each RAM word holds 16 pixels: $512 / 16 = 32$ words/row.
- **Why `M=-1` for black?** `-1` in 16-bit two's complement is `1111111111111111` (`0xFFFF`), setting all 16 horizontal pixels in that word to black (`1`).
- **How does `Memory.hdl` decode RAM vs Screen vs Keyboard?** Uses `address[13..14]` (`00`/`01` = RAM16K, `10` = Screen, `11` = Keyboard).
- **Why gate `loadPC`, `loadD`, and `writeM` with `isC` (`instruction[15]`)?** So an A-instruction (`instruction[15] == 0`) only loads the A-register and increments `PC`, never writing to `D`, `Memory`, or jumping based on constant bits.
