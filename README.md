# 2048tris

A combination of 2048 and Tetris

Game rules:
- each tile has a power of 2 numeric value, as in 2048
- manipulate falling tetris pieces with the arrow keys
- change the board direction using WASD
- changing the direction will shift all tiles to that side
- falling tiles will merge with like values upon impact
- static tiles with like values can merge iff the relative lower tile is in a completed row

Todo:
- if a piece merges, blocks to the sides prevent cells from shifting down
- if a piece merges, sometimes 2 cells in the active piece will combine
- maybe i should change the logic so cells only merge if the whole piece can shift down (all cells move or no cells move)
- in static merge, sometimes cells will disappear entirely after a few merges
- i should really write some tests for these instead of just hackin it
- add end screen instead of exiting the program
- why do pieces leave ghost trails in the buffer?