# Onitama-AI
An AI for the board game [Onitama](https://boardgamegeek.com/boardgame/160477/onitama).

The AI uses minimax search with alpha-beta pruning to decide moves. There are two difficulty levels.

To play against the AI (easy): `python3 main.py`

To play against the AI (hard): `python3 main.py -e 2`

To load a previous game state: `python3 main.py -l 1495381528682411417722191102608565721`

```
Turn 16 blue
serialized: 1334420292643488479464200513771655830
current_player: blue
red_cards: mantis rooster
.....	.....
..X..	...X.
..O..	.XOX.
.X.X.	.X...
.....	.....
  abcde
5 ..... 5
4 ..R.. 4
3 ..... 3
2 ....r 2
1 ..... 1
  abcde
neutral_card: crane
.....
..X..
..O..
.X.X.
.....
blue_cards: goose crab
.....	.....
.X...	..X..
.XOX.	X.O.X
...X.	.....
.....	.....
AI wins!
```