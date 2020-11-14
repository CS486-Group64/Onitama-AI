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

def count_trailing_zeroes(num):
    # adapted from https://stackoverflow.com/a/56320918
    if not num:
        return 32
    num &= -num # keep only right-most 1
    count = 0
    if num & 0xAAAAAAAA:
        count |= 1 # binary 10..1010
    if num & 0xCCCCCCCC:
        count |= 2 # binary 1100..11001100
    if num & 0xF0F0F0F0:
        count |= 4
    if num & 0xFF00FF00:
        count |= 8
    if num & 0xFFFF0000:
        count |= 16 
    return count

def count_bits(n):
    # adapted from https://stackoverflow.com/a/9830282 for 32 bits
    n = (n & 0x55555555) + ((n & 0xAAAAAAAA) >> 1)
    n = (n & 0x33333333) + ((n & 0xCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F) + ((n & 0xF0F0F0F0) >> 4)
    n = (n & 0x00FF00FF) + ((n & 0xFF00FF00) >> 8)
    n = (n & 0x0000FFFF) + ((n & 0xFFFF0000) >> 16)
    return n

class Move(NamedTuple):
    start: int
    end: int
    card: str

    def __str__(self):
        return f"{self.card} {Point.from_index(self.start).to_algebraic_notation()} {Point.from_index(self.end).to_algebraic_notation()}"
    
    def serialize(self):
        result = self.start
        result <<= BOARD_HEIGHT
        result |= self.end
        result <<= 4 # 16 cards = 4 bits
        result |= INDEX_CARD[self.card]
        return result
    
    @classmethod
    def from_serialized(cls, representation):
        card_index = representation & ((1 << 4) - 1)
        representation >>= 4
        end_index = representation & ((1 << BOARD_HEIGHT) - 1)
        representation >>= BOARD_HEIGHT
        start_index = representation
        return cls(start_index, end_index, CARD_INDEX[card_index])

class Game:
    WIN_SCORE = 50
    WIN_BITMASK = [0b00000_00000_00000_00000_00100, 0b00100_00000_00000_00000_00000]
    CENTRE_PRIORITY_BITMASKS = [
        0b01010_10001_00000_10001_01010,
        0b00100_01010_10001_01010_00100,
        0b00000_00100_01010_00100_00000,
        0b00000_00000_00100_00000_00000
    ]

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
        if starting_player is None:
            starting_player = neutral_card.starting_player
        
        self.red_cards = red_cards
        self.blue_cards = blue_cards
        self.neutral_card = neutral_card
        self.current_player = starting_player
        # board
        self.bitboard_king = bitboard_king or [0b00100_00000_00000_00000_00000, 0b00000_00000_00000_00000_00100]
        self.bitboard_pawns = bitboard_pawns or [0b11011_00000_00000_00000_00000, 0b00000_00000_00000_00000_11011]

    @classmethod
    def from_string(cls, board, red_cards, blue_cards, neutral_card, starting_player=None):
        red_cards = [ONITAMA_CARDS.get(card) for card in red_cards]
        blue_cards = [ONITAMA_CARDS.get(card) for card in blue_cards]
        neutral_card = ONITAMA_CARDS.get(neutral_card)

        bitboard_king = [0, 0]
        bitboard_pawns = [0, 0]

        for y, row in enumerate(board.split("\n")):
            for x, char in enumerate(row):
                pos = Point(x, y).to_index()
                if char == "R":
                    bitboard_king[0] |= 1 << pos
                elif char == "B":
                    bitboard_king[1] |= 1 << pos
                elif char == "r":
                    bitboard_pawns[0] |= 1 << pos
                elif char == "b":
                    bitboard_pawns[1] |= 1 << pos
        return cls(red_cards=red_cards, blue_cards=blue_cards, neutral_card=neutral_card,
                   bitboard_king=bitboard_king, bitboard_pawns=bitboard_pawns,
                   starting_player=starting_player)
    
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
        return (f"serialized: {self.serialize()}\n"
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
        return Game(red_cards=self.red_cards.copy(), blue_cards=self.blue_cards.copy(), neutral_card=self.neutral_card,
                    starting_player=self.current_player,
                    bitboard_king=self.bitboard_king.copy(), bitboard_pawns=self.bitboard_pawns.copy())
    
    def __str__(self):
        return f"Game(\n{self.visualize()}\n)"

    def __repr__(self):
        return (f"Game(red_cards={self.red_cards[0].name, self.red_cards[1].name!r}, blue_cards={self.blue_cards[0].name, self.blue_cards[1].name!r}, "
                f"neutral_card={self.neutral_card.name!r}, current_player={self.current_player!r}, "
                f"bitboard_king={self.bitboard_king!r}, bitboard_pawns={self.bitboard_pawns!r})")
    
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
    
    @classmethod
    def from_serialized(cls, serialized):
        neutral_card = ONITAMA_CARDS.get(CARD_INDEX[serialized & ((1 << 4) - 1)])
        serialized >>= 4
        blue_2 = ONITAMA_CARDS.get(CARD_INDEX[serialized & ((1 << 4) - 1)])
        serialized >>= 4
        blue_1 = ONITAMA_CARDS.get(CARD_INDEX[serialized & ((1 << 4) - 1)])
        serialized >>= 4
        blue_cards = [blue_1, blue_2]
        red_2 = ONITAMA_CARDS.get(CARD_INDEX[serialized & ((1 << 4) - 1)])
        serialized >>= 4
        red_1 = ONITAMA_CARDS.get(CARD_INDEX[serialized & ((1 << 4) - 1)])
        serialized >>= 4
        red_cards = [red_1, red_2]
        bitboard_king = [0, 0]
        bitboard_pawns = [0, 0]
        for i in (1, 0):
            bitboard_pawns[i] = serialized & ((1 << BOARD_WIDTH * BOARD_HEIGHT) - 1)
            serialized >>= BOARD_WIDTH * BOARD_HEIGHT
            bitboard_king[i] = serialized & ((1 << BOARD_WIDTH * BOARD_HEIGHT) - 1)
            serialized >>= BOARD_WIDTH * BOARD_HEIGHT
        starting_player = serialized
        return cls(red_cards=red_cards, blue_cards=blue_cards, neutral_card=neutral_card,
                   starting_player=starting_player,
                   bitboard_king=bitboard_king, bitboard_pawns=bitboard_pawns)

    def legal_moves(self):
        # adapted from https://github.com/maxbennedich/onitama/blob/master/src/main/java/onitama/ai/MoveGenerator.java
        cards = self.red_cards if self.current_player == 0 else self.blue_cards
        has_valid_move = False

        player_bitboard = self.bitboard_king[self.current_player] | self.bitboard_pawns[self.current_player]
        start_pos = -1
        start_trailing_zeroes = -1

        # Loop over current player's pieces
        while True:
            # pop last piece
            player_bitboard >>= start_trailing_zeroes + 1
            start_trailing_zeroes = count_trailing_zeroes(player_bitboard)
            if start_trailing_zeroes == 32:
                break
            start_pos += start_trailing_zeroes + 1

            for card in cards:
                move_bitmask = card.move_table[self.current_player][start_pos]
                # prevent moving onto own pieces
                move_bitmask &= ~self.bitboard_pawns[self.current_player]
                move_bitmask &= ~self.bitboard_king[self.current_player]

                end_pos = -1
                end_trailing_zeroes = -1

                while True:
                    # pop move
                    move_bitmask >>= end_trailing_zeroes + 1
                    end_trailing_zeroes = count_trailing_zeroes(move_bitmask)
                    if end_trailing_zeroes == 32:
                        break
                    end_pos += end_trailing_zeroes + 1

                    has_valid_move = True

                    yield Move(start_pos, end_pos, card.name)

        if not has_valid_move:
            # pass due to no piece moves, but have to swap a card
            for card in cards:
                yield Move(0, 0, card.name)
    
    def apply_move(self, move: Move):
        start_mask = 1 << move.start
        end_mask = 1 << move.end
        card = move.card

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
        elif self.bitboard_king[self.current_player] & start_mask:
            # moved own king
            self.bitboard_king[self.current_player] &= ~start_mask
            self.bitboard_king[self.current_player] |= end_mask
        else: # TODO: remove since could have no "valid" move
            raise AssertionError("invalid move", str(move), self)

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

    def piece_evaluate(self):
        """Evaluates a given board position. Very arbitrary.
        Assigns a win to +/-50.
        Each piece is worth 2, king is worth 4.
        """
        winner = self.determine_winner()
        if winner:
            return winner * self.WIN_SCORE
        evaluation = 0
        for player in range(2):
            player_sign = player * 2 - 1
            evaluation += player_sign * 4 * count_bits(self.bitboard_king[player])
            evaluation += player_sign * 2 * count_bits(self.bitboard_pawns[player])

        return evaluation

    def centre_priority_evaluate(self):
        """Evaluates a given board position
        Assings a win to +/-50
        More points are given to pieces closer to the centre of the board
        """
        winner = self.determine_winner()
        if winner:
            return winner * self.WIN_SCORE
        evaluation = 0
        for player in range(2):
            player_sign = player * 2 - 1
            for i in range(4):
                score = i + 1
                evaluation += player_sign * score * count_bits(self.bitboard_king[player] &
                                                               self.CENTRE_PRIORITY_BITMASKS[i])
                evaluation += player_sign * score * count_bits(self.bitboard_pawns[player] &
                                                               self.CENTRE_PRIORITY_BITMASKS[i])
        return evaluation
    
    def evaluate(self, mode=0):
        if mode == 1:
            return self.centre_priority_evaluate()
        else:
            return self.piece_evaluate()

ONITAMA_CARDS = {
    # symmetrical
    "tiger": Card("tiger", 1, Point(0, -2), Point(0, 1)),
    "dragon": Card("dragon", 0, Point(-2, -1), Point(2, -1), Point(-1, 1), Point(1, 1)),
    "crab": Card("crab", 1, Point(0, -1), Point(-2, 0), Point(2, 0)),
    "elephant": Card("elephant", 0, Point(-1, -1), Point(1, -1), Point(-1, 0), Point(1, 0)),
    "monkey": Card("monkey", 1, Point(-1, -1), Point(1, -1), Point(-1, 1), Point(1, 1)),
    "mantis": Card("mantis", 0, Point(-1, -1), Point(1, -1), Point(0, 1)),
    "crane": Card("crane", 1, Point(0, -1), Point(-1, 1), Point(1, 1)),
    "boar": Card("boar", 0, Point(0, -1), Point(-1, 0), Point(1, 0)),
    # left-leaning
    "frog": Card("frog", 0, Point(-1, -1), Point(-2, 0), Point(1, 1)),
    "goose": Card("goose", 1, Point(-1, -1), Point(-1, 0), Point(1, 0), Point(1, 1)),
    "horse": Card("horse", 0, Point(0, -1), Point(-1, 0), Point(0, 1)),
    "eel": Card("eel", 1, Point(-1, -1), Point(1, 0), Point(-1, 1)),
    # right-leaning
    "rabbit": Card("rabbit", 1, Point(1, -1), Point(2, 0), Point(-1, 1)),
    "rooster": Card("rooster", 0, Point(1, -1), Point(-1, 0), Point(1, 0), Point(-1, 1)),
    "ox": Card("ox", 1, Point(0, -1), Point(1, 0), Point(0, 1)),
    "cobra": Card("cobra", 0, Point(1, -1), Point(-1, 0), Point(1, 1)),
}

CARD_INDEX = list(ONITAMA_CARDS)
INDEX_CARD = {card: i for i, card in enumerate(CARD_INDEX)}