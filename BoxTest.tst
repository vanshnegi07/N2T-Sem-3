// BoxTest.tst - Automated CPUEmulator regression test for Box.hack (K = 58)
// Row = 58 (base 18240), Width = 48px (3 words), Height = 20 rows (rows 58..77, end 18850)

load Box.hack,
output-file BoxTest.out,
compare-to BoxTest.cmp,
output-list RAM[18208]%D1.6.1 RAM[18240]%D1.6.1 RAM[18241]%D1.6.1 RAM[18242]%D1.6.1 RAM[18243]%D1.6.1 RAM[18848]%D1.6.1 RAM[18850]%D1.6.1 RAM[18880]%D1.6.1;

// 1. Key released (RAM[24576] = 0)
set RAM[24576] 0,
repeat 2500 {
    ticktock;
}
output;

// 2. Key pressed (RAM[24576] = 75 'K')
set RAM[24576] 75,
repeat 2500 {
    ticktock;
}
output;

// 3. Key released again (RAM[24576] = 0)
set RAM[24576] 0,
repeat 2500 {
    ticktock;
}
output;
