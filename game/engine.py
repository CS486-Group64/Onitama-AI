"""Onitama game engine. Note that (x, y) goes right and down."""

from typing import List, NamedTuple

BOARD_WIDTH = 5
BOARD_HEIGHT = 5

class Point(NamedTuple):
    x: int
    y: int

class Card:
    def __init__(self, name, *moves: List[Point]):
        """Moves are represented as a list of Points representing movement relative to (0, 0)"""
        self.name = name
        self.moves = moves
    
    def __repr__(self):
        # Cards are displayed with board centre (2, 2) at (0, 0)
        output = [["."] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        output[BOARD_HEIGHT // 2][BOARD_WIDTH // 2] = "O"
        for move in self.moves:
            output[move.y + BOARD_HEIGHT // 2][move.x + BOARD_WIDTH // 2] = "X"
        output_str = "\n".join("".join(row) for row in output)
        return f"Card({self.name!r},\n{output_str})"

ONITAMA_CARDS = {
    # symmetrical
    "tiger": Card("tiger", Point(0, -2), Point(0, 1)),
    "dragon": Card("dragon", Point(-2, -1), Point(2, -1), Point(-1, 1), Point(1, 1)),
    "crab": Card("crab", Point(0, -1), Point(-2, 0), Point(2, 0)),
    "elephant": Card("elephant", Point(-1, -1), Point(1, -1), Point(-1, 0), Point(1, 0)),
    "monkey": Card("monkey", Point(-1, -1), Point(1, -1), Point(-1, 1), Point(1, 1)),
    "mantis": Card("mantis", Point(-1, -1), Point(1, -1), Point(0, 1)),
    "crane": Card("crane", Point(0, -1), Point(-1, 1), Point(1, 1)),
    "boar": Card("boar", Point(0, -1), Point(-1, 0), Point(1, 0)),
    # left-leaning
    "frog": Card("frog", Point(-1, -1), Point(-2, 0), Point(1, 1)),
    "goose": Card("goose", Point(-1, -1), Point(-1, 0), Point(1, 0), Point(1, 1)),
    "horse": Card("horse", Point(0, -1), Point(-1, 0), Point(0, 1)),
    "eel": Card("eel", Point(-1, -1), Point(1, 0), Point(-1, 1)),
    # right-leaning
    "rabbit": Card("rabbit", Point(1, -1), Point(2, 0), Point(-1, 1)),
    "rooster": Card("rooster", Point(1, -1), Point(-1, 0), Point(1, 0), Point(-1, 1)),
    "ox": Card("ox", Point(0, -1), Point(1, 0), Point(0, 1)),
    "cobra": Card("cobra", Point(1, -1), Point(-1, 0), Point(1, 1)),
}