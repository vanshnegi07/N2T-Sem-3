// Box.asm - Nand to Tetris Capstone (Part C)
// Student: Vansh Negi | Roll Number: 2501730158 | K = 58
// Starting Row: K = 58 -> SCREEN (16384) + 32 * 58 = 18240
// Width: 16 * ((58 mod 4) + 1) = 16 * (2 + 1) = 48 pixels (3 words/row)
// Height: 20 rows (Rows 58 to 77)

(MAIN_LOOP)
    @KBD
    D=M             // Read keyboard register (RAM[24576])

    @SET_WHITE
    D;JEQ           // If no key pressed (D == 0), set color to white

(SET_BLACK)
    @color
    M=-1            // color = -1 (0xFFFF, 16 black pixels)
    @DRAW
    0;JMP

(SET_WHITE)
    @color
    M=0             // color = 0 (0x0000, 16 white pixels)

(DRAW)
    @18240          // Row 58 base address: 16384 + 32 * 58 = 18240
    D=A
    @row_addr
    M=D

    @20             // Height = 20 rows
    D=A
    @row_count
    M=D

(ROW_LOOP)
    @row_count
    D=M
    @MAIN_LOOP
    D;JEQ           // Finished all 20 rows -> return to keyboard polling

    @row_addr
    D=M
    @col_addr
    M=D             // Start at left edge of current row

    @3              // Width = 3 words (48 pixels)
    D=A
    @col_count
    M=D

(COL_LOOP)
    @col_count
    D=M
    @NEXT_ROW
    D;JEQ           // Finished 3 words in row -> advance to next row

    @color
    D=M
    @col_addr
    A=M
    M=D             // RAM[col_addr] = color

    @col_addr
    M=M+1           // Move right by 1 word (16 pixels)

    @col_count
    M=M-1           // Decrement column counter

    @COL_LOOP
    0;JMP

(NEXT_ROW)
    @32
    D=A
    @row_addr
    M=D+M           // Advance row_addr by 32 words (1 row down)

    @row_count
    M=M-1           // Decrement row counter

    @ROW_LOOP
    0;JMP
