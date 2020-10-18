"""Onitama game engine. Note that (x, y) goes right and down."""

import random
from typing import List, NamedTuple, Optional

BOARD_WIDTH = 5
BOARD_HEIGHT = 5

class Point(NamedTuple):
    x: int
    y: int

class Card:
    def __init__(self, name, starting_player, *moves: List[Point]):
        """Moves are represented as a list of Points representing movement relative to (0, 0)"""
        self.name = name
        self.starting_player = starting_player
        self.moves = moves
    
    def visualize(self):
        # Cards are displayed with board centre (2, 2) at (0, 0)
        output = [["."] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        output[BOARD_HEIGHT // 2][BOARD_WIDTH // 2] = "O"
        for move in self.moves:
            output[move.y + BOARD_HEIGHT // 2][move.x + BOARD_WIDTH // 2] = "X"
        return "\n".join("".join(row) for row in output)

    def __repr__(self):
        return f"Card({self.name!r},\n{self.visualize()})"

class Game:
    def __init__(self, *, red_cards: Optional[List[str]] = None, blue_cards: Optional[List[str]] = None,
                 neutral_card: Optional[List[str]] = None, board=None, starting_player=None):
        """Represents an Onitama game. Generates random cards to fill in missing red_cards, blue_cards,
        or neutral_card. If starting_player is not specified, uses neutral_card.starting_player."""
        cards = set(ONITAMA_CARDS)
        if red_cards:
            cards -= set(red_cards)
            red_cards = [ONITAMA_CARDS[card] for card in red_cards]
        if blue_cards:
            cards -= set(blue_cards)
            blue_cards = [ONITAMA_CARDS[card] for card in red_cards]
        if neutral_card:
            cards.remove(neutral_card)
            neutral_card = ONITAMA_CARDS[neutral_card]
        if not red_cards:
            card1, card2 = random.sample(cards, k=2)
            red_cards = [ONITAMA_CARDS.get(card1), ONITAMA_CARDS.get(card2)]
            cards -= {card1, card2}
        if not blue_cards:
            card1, card2 = random.sample(cards, k=2)
            blue_cards = [ONITAMA_CARDS.get(card1), ONITAMA_CARDS.get(card2)]
            cards -= {card1, card2}
        if not neutral_card:
            card = random.sample(cards, k=1)[0]
            neutral_card = ONITAMA_CARDS.get(card)
            cards.remove(card)
        if not starting_player:
            starting_player = neutral_card.starting_player
        if not board:
            board = [["r", "r", "R", "r", "r"],
                     [".", ".", ".", ".", "."],
                     [".", ".", ".", ".", "."],
                     [".", ".", ".", ".", "."],
                     ["b", "b", "B", "b", "b"]]
        
        self.board = board
        self.red_cards = red_cards
        self.blue_cards = blue_cards
        self.neutral_card = neutral_card
        self.current_player = starting_player
    
    def visualize_board(self):
        return "\n".join("".join(self.board[y][x] for x in range(BOARD_WIDTH)) for y in range(BOARD_HEIGHT))
    
    def __repr__(self):
        return (f"Game(\n{self.visualize_board()}\n"
                f"current_player: {self.current_player}\n"
                f"red_cards: {' '.join(card.name for card in self.red_cards)}\n"
                f"blue_cards: {' '.join(card.name for card in self.blue_cards)}\n"
                f"neutral_card: {self.neutral_card.name})")
    
    def determine_winner(self):
        # Way of the Stone (capture opponent master)
        red_alive = False
        blue_alive = False
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x] == "R":
                    red_alive = True
                if self.board[y][x] == "B":
                    blue_alive = True
        if not red_alive:
            return "blue"
        if not blue_alive:
            return "red"
        # Way of the Stream (move master to opposite square)
        if self.board[0][BOARD_WIDTH // 2] == "B":
            return "blue"
        if self.board[-1][BOARD_WIDTH // 2] == "R":
            return "red"
        return None
    


ONITAMA_CARDS = {
    # symmetrical
    "tiger": Card("tiger", "blue", Point(0, -2), Point(0, 1)),
    "dragon": Card("dragon", "red", Point(-2, -1), Point(2, -1), Point(-1, 1), Point(1, 1)),
    "crab": Card("crab", "blue", Point(0, -1), Point(-2, 0), Point(2, 0)),
    "elephant": Card("elephant", "red", Point(-1, -1), Point(1, -1), Point(-1, 0), Point(1, 0)),
    "monkey": Card("monkey", "blue", Point(-1, -1), Point(1, -1), Point(-1, 1), Point(1, 1)),
    "mantis": Card("mantis", "red", Point(-1, -1), Point(1, -1), Point(0, 1)),
    "crane": Card("crane", "blue", Point(0, -1), Point(-1, 1), Point(1, 1)),
    "boar": Card("boar", "red", Point(0, -1), Point(-1, 0), Point(1, 0)),
    # left-leaning
    "frog": Card("frog", "red", Point(-1, -1), Point(-2, 0), Point(1, 1)),
    "goose": Card("goose", "blue", Point(-1, -1), Point(-1, 0), Point(1, 0), Point(1, 1)),
    "horse": Card("horse", "red", Point(0, -1), Point(-1, 0), Point(0, 1)),
    "eel": Card("eel", "blue", Point(-1, -1), Point(1, 0), Point(-1, 1)),
    # right-leaning
    "rabbit": Card("rabbit", "blue", Point(1, -1), Point(2, 0), Point(-1, 1)),
    "rooster": Card("rooster", "red", Point(1, -1), Point(-1, 0), Point(1, 0), Point(-1, 1)),
    "ox": Card("ox", "blue", Point(0, -1), Point(1, 0), Point(0, 1)),
    "cobra": Card("cobra", "red", Point(1, -1), Point(-1, 0), Point(1, 1)),
}