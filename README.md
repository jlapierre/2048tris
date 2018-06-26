# 2048tris

Todo:
- if a piece merges, blocks to the sides prevent cells from shifting down
- if a piece merges, sometimes 2 cells in the active piece will combine
- i should really write some tests for these instead of just hackin it
- add end screen instead of exiting the program
- why do pieces leave ghost trails in the buffer?
- shifting does not do combos among existing pieces (it should)
- in some other cases, it just keeps incrementing the same piece/s for an auto-win after shifting (usually to the left)