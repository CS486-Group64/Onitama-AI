"""Onitama game engine. Note that (x, y) goes right and down. Blue uses positive numbers, red uses negative numbers.
Bitboard has red on the most significant side"""

import numpy as np
import random
from typing import List, NamedTuple, Optional

BOARD_WIDTH = 5
BOARD_HEIGHT = 5

class Point(NamedTuple):
    x: int
    y: int

    def to_algebraic_notation(self):
        return chr(ord("a") + self.x) + str(5 - self.y)
    
    @classmethod
    def from_algebraic_notation(cls, location):
        x = ord(location[0]) - ord("a")
        y = BOARD_HEIGHT - int(location[1])
        return cls(x, y)
    
    def to_index(self):
        """Indices go from bottom right to top left due to bit ordering"""
        return (BOARD_HEIGHT - 1 - self.y) * BOARD_HEIGHT + (BOARD_WIDTH - 1 - self.x)
    
    @classmethod
    def from_index(cls, index):
        x = BOARD_WIDTH - 1 - index % BOARD_WIDTH
        y = BOARD_HEIGHT - 1 - index // BOARD_HEIGHT
        return cls(x, y)

class Card:
    def __init__(self, name, starting_player, *moves: List[Point]):
        """Moves are represented as a table of destination squares reachable from each origin square"""
        self.name = name
        self.starting_player = starting_player
        self.moves = moves
        self.move_table = np.zeros((2, BOARD_HEIGHT * BOARD_WIDTH), dtype=np.int64) # player, square
        self.precompute_move_table()
    
    def precompute_move_table(self):
        # player 0 is red, player 1 is blue
        for player_index in range(2):
            # a bit confusing since index goes left and up
            for point_index in range(BOARD_WIDTH * BOARD_HEIGHT):
                board = 0
                for move in self.moves:
                    player = player_index * 2 - 1
                    point = Point.from_index(point_index)
                    new_x = point.x + player * move.x
                    new_y = point.y + player * move.y
                    dest = Point(new_x, new_y)
                    if new_x in range(BOARD_WIDTH) and new_y in range(BOARD_HEIGHT):
                        board |= 1 << dest.to_index()
                self.move_table[player_index][point_index] = board

    def visualize(self, reverse=False):
        # Cards are displayed with board centre (2, 2) at (0, 0)
        output = [["."] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        output[BOARD_HEIGHT // 2][BOARD_WIDTH // 2] = "O"
        for move in self.moves:
            if reverse:
                output[BOARD_HEIGHT // 2 - move.y][BOARD_WIDTH // 2 - move.x] = "X"
            else:
                output[move.y + BOARD_HEIGHT // 2][move.x + BOARD_WIDTH // 2] = "X"
        return "\n".join("".join(row) for row in output)

    def __repr__(self):
        return f"Card({self.name!r},\n{self.visualize()})"

def visualize_bitboard(bitboard):
    s = f"{bitboard:0{BOARD_HEIGHT * BOARD_WIDTH}b}"
    output = [s[i:i+BOARD_WIDTH] for i in range(0, BOARD_HEIGHT * BOARD_WIDTH, BOARD_HEIGHT)]
    return "\n".join(output)

class Move(NamedTuple):
    start: Point
    end: Point
    card: str

    def __str__(self):
        return f"{self.card} {self.start.to_algebraic_notation()} {self.end.to_algebraic_notation()}"
    
    def to_compact_repr(self):
        result = self.start.to_index()
        result <<= BOARD_HEIGHT
        result |= self.end.to_index()
        result <<= 4 # 16 cards = 4 bits
        result |= INDEX_CARD[self.card]
        return result
    
    @classmethod
    def from_compact_repr(cls, representation):
        card_index = representation & ((1 << 4) - 1)
        representation >>= 4
        end_index = representation & ((1 << BOARD_HEIGHT) - 1)
        representation >>= BOARD_HEIGHT
        start_index = representation
        return cls(Point.from_index(start_index), Point.from_index(end_index), CARD_INDEX[card_index])

class Game:
    WIN_BITMASK = [0b00000_00000_00000_00000_00100, 0b00100_00000_00000_00000_00000]

    def __init__(self, *, red_cards: Optional[List[Card]] = None, blue_cards: Optional[List[Card]] = None,
                 neutral_card: Optional[Card] = None, starting_player=None,
                 bitboard_king: Optional[List[int]] = None, bitboard_pawns: Optional[List[int]] = None):
        """Represents an Onitama game. Generates random cards if missing red_cards, blue_cards,
        or neutral_card. If starting_player is not specified, uses neutral_card.starting_player."""
        if not (red_cards and blue_cards and neutral_card):
            cards = set(ONITAMA_CARDS)
            card1, card2 = random.sample(cards, k=2)
            red_cards = [ONITAMA_CARDS.get(card1), ONITAMA_CARDS.get(card2)]
            cards -= {card1, card2}

            card1, card2 = random.sample(cards, k=2)
            blue_cards = [ONITAMA_CARDS.get(card1), ONITAMA_CARDS.get(card2)]
            cards -= {card1, card2}

            card = random.sample(cards, k=1)[0]
            neutral_card = ONITAMA_CARDS.get(card)
            cards.remove(card)
        if not starting_player:
            starting_player = neutral_card.starting_player
        
        self.red_cards = red_cards
        self.blue_cards = blue_cards
        self.neutral_card = neutral_card
        # -1, 1 -> 0, 1 (red, blue)
        self.current_player = (starting_player + 1) // 2
        # board
        self.bitboard_king = bitboard_king or [0b00100_00000_00000_00000_00000, 0b00000_00000_00000_00000_00100]
        self.bitboard_pawns = bitboard_pawns or [0b11011_00000_00000_00000_00000, 0b00000_00000_00000_00000_11011]
    
    def get_piece_char_mapping(self):
        return {
            "R": self.bitboard_king[0],
            "r": self.bitboard_pawns[0],
            "b": self.bitboard_pawns[1],
            "B": self.bitboard_king[1],
        }
    
    def visualize_board(self):
        output = [["."] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        for char, bitfield in self.get_piece_char_mapping().items():
            for i, c in enumerate(f"{bitfield:0{BOARD_WIDTH * BOARD_HEIGHT}b}"):
                if c == "1":
                    # i should go from 24 to 0
                    point = Point.from_index(BOARD_WIDTH * BOARD_HEIGHT - 1 - i)
                    output[point.y][point.x] = char

        return "\n".join("".join(row) for row in output)
    
    def visualize(self):
        fancy_board = ["  abcde"]
        for i, line in enumerate(self.visualize_board().split("\n")):
            fancy_board.append(f"{5 - i} {line} {5 - i}")
        fancy_board.append("  abcde")
        fancy_board_str = "\n".join(fancy_board)
        return (
                f"current_player: {'blue' if self.current_player > 0 else 'red'}\n"
                f"red_cards: {' '.join(card.name for card in self.red_cards)}\n" +
                "\n".join(f"{c1}\t{c2}" for c1, c2 in zip(self.red_cards[0].visualize(reverse=True).split("\n"), self.red_cards[1].visualize(reverse=True).split("\n"))) +
                f"\n{fancy_board_str}\n"
                f"neutral_card: {self.neutral_card.name}\n"
                f"{self.neutral_card.visualize(reverse=self.current_player == 0)}\n"
                f"blue_cards: {' '.join(card.name for card in self.blue_cards)}\n" +
                "\n".join(f"{c1}\t{c2}" for c1, c2 in zip(self.blue_cards[0].visualize().split("\n"), self.blue_cards[1].visualize().split("\n")))
                )
    
    def copy(self):
        return Game(red_cards=self.red_cards, blue_cards=self.blue_cards, neutral_card=self.neutral_card,
                    starting_player=self.current_player,
                    bitboard_king=self.bitboard_king.copy(), bitboard_pawns=self.bitboard_pawns.copy())
    
    def __repr__(self):
        return f"Game(\n{self.visualize()}\n)"
    
    def serialize(self):
        serialized = self.current_player
        for i in range(2):
            serialized <<= BOARD_WIDTH * BOARD_HEIGHT
            serialized |= self.bitboard_king[i]
            serialized <<= BOARD_WIDTH * BOARD_HEIGHT
            serialized |= self.bitboard_pawns[i]
        # sort cards
        red_1, red_2 = sorted(INDEX_CARD[card.name] for card in self.red_cards)
        serialized <<= 4
        serialized |= red_1
        serialized <<= 4
        serialized |= red_2
        blue_1, blue_2 = sorted(INDEX_CARD[card.name] for card in self.blue_cards)
        serialized <<= 4
        serialized |= blue_1
        serialized <<= 4
        serialized |= blue_2
        serialized <<= 4
        serialized |= INDEX_CARD[self.neutral_card.name]

        return serialized

    def legal_moves(self):
        cards = self.red_cards if self.current_player == 0 else self.blue_cards
        has_valid_move = False

        player_bitboard = self.bitboard_king[self.current_player] | self.bitboard_pawns[self.current_player]

        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x] * self.current_player > 0:
                    for card in cards:
                        for card_move in card.moves:
                            new_x = x + self.current_player * card_move.x
                            new_y = y + self.current_player * card_move.y
                            if new_x in range(BOARD_WIDTH) and new_y in range(BOARD_HEIGHT) and self.board[new_y][new_x] * self.current_player <= 0:
                                has_valid_move = True
                                yield Move(Point(x, y), Point(new_x, new_y), card.name)
        if not has_valid_move:
            # pass due to no piece moves, but have to swap a card
            for card in cards:
                yield Move(Point(0, 0), Point(0, 0), card)
    
    def apply_move(self, start_mask: int, end_mask: int, card: str):
        cards = self.red_cards if self.current_player == 0 else self.blue_cards
        card_idx = 0 if cards[0].name == card else 1

        if self.bitboard_pawns[1 - self.current_player] & end_mask:
            # captured opponent pawn
            self.bitboard_pawns[1 - self.current_player] &= ~end_mask
        if self.bitboard_king[1 - self.current_player] & end_mask:
            # captured opponent king
            self.bitboard_king[1 - self.current_player] &= ~end_mask
        if self.bitboard_pawns[self.current_player] & start_mask:
            # moved own pawn
            self.bitboard_pawns[self.current_player] &= ~start_mask
            self.bitboard_pawns[self.current_player] |= end_mask
        else:
            # moved own king
            self.bitboard_king[self.current_player] &= ~start_mask
            self.bitboard_king[self.current_player] |= end_mask

        self.neutral_card, cards[card_idx] = cards[card_idx], self.neutral_card
        self.current_player = 1 - self.current_player
    
    def determine_winner(self):
        """Returns -1 for red win, 1 for blue win, 0 for no win"""
        for i in range(2):
            # Way of the Stone (capture opponent master)
            if not self.bitboard_king[i]:
                return 1 - i * 2
            # Way of the Stream (move master to opposite square)
            if self.bitboard_king[i] == self.WIN_BITMASK[i]:
                return i * 2 - 1
        return 0
    
    def evaluate(self):
        """Evaluates a given board position. Very arbitrary.
        Assigns a win to +/-50.
        Each piece is worth 2, king is worth 4.
        Shortest distance (diagonals have length 1) from king to temple is subtracted."""
        winner = self.determine_winner()
        if winner:
            return winner * 50
        evaluation = 0
        blue_king_x = blue_king_y = 0
        red_king_x = red_king_y = 0
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                # Piece evaluation
                piece = self.board[y][x]
                evaluation += piece * 2
                if piece == 2:
                    blue_king_x = x
                    blue_king_y = y
                elif piece == -2:
                    red_king_x = x
                    red_king_y = y
        evaluation -= max(abs(blue_king_x - 2), abs(blue_king_y - 4))
        evaluation += max(abs(red_king_x - 2), abs(red_king_y - 0))
        return evaluation




ONITAMA_CARDS = {
    # symmetrical
    "tiger": Card("tiger", 1, Point(0, -2), Point(0, 1)),
    "dragon": Card("dragon", -1, Point(-2, -1), Point(2, -1), Point(-1, 1), Point(1, 1)),
    "crab": Card("crab", 1, Point(0, -1), Point(-2, 0), Point(2, 0)),
    "elephant": Card("elephant", -1, Point(-1, -1), Point(1, -1), Point(-1, 0), Point(1, 0)),
    "monkey": Card("monkey", 1, Point(-1, -1), Point(1, -1), Point(-1, 1), Point(1, 1)),
    "mantis": Card("mantis", -1, Point(-1, -1), Point(1, -1), Point(0, 1)),
    "crane": Card("crane", 1, Point(0, -1), Point(-1, 1), Point(1, 1)),
    "boar": Card("boar", -1, Point(0, -1), Point(-1, 0), Point(1, 0)),
    # left-leaning
    "frog": Card("frog", -1, Point(-1, -1), Point(-2, 0), Point(1, 1)),
    "goose": Card("goose", 1, Point(-1, -1), Point(-1, 0), Point(1, 0), Point(1, 1)),
    "horse": Card("horse", -1, Point(0, -1), Point(-1, 0), Point(0, 1)),
    "eel": Card("eel", 1, Point(-1, -1), Point(1, 0), Point(-1, 1)),
    # right-leaning
    "rabbit": Card("rabbit", 1, Point(1, -1), Point(2, 0), Point(-1, 1)),
    "rooster": Card("rooster", -1, Point(1, -1), Point(-1, 0), Point(1, 0), Point(-1, 1)),
    "ox": Card("ox", 1, Point(0, -1), Point(1, 0), Point(0, 1)),
    "cobra": Card("cobra", -1, Point(1, -1), Point(-1, 0), Point(1, 1)),
}

CARD_INDEX = list(ONITAMA_CARDS)
INDEX_CARD = {card: i for i, card in enumerate(CARD_INDEX)}