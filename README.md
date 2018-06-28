# 2048tris

A combination of 2048 and Tetris

Game rules:
- each tile has a power-of-2 numeric value, as in 2048
- currently, the values are not printed on the tiles, but the colors increment in rainbow order
- manipulate falling tetris pieces with the arrow keys
- change the board direction using WASD
- changing the direction will shift all tiles to that side
- falling tiles will merge with like values upon impact
- static tiles with like values can merge iff the relative lower tile is in a completed row

Todo:
- add end screen instead of exiting the programs
- factor out merge logic (double one and clear the other) into a helper
- blocks in active piece randomly disappearing/not rendering
- player suggestion: smaller board size