from game import ONITAMA_CARDS, Game, Move, OnitamaAI, Point, visualize_bitboard, count_trailing_zeroes, CARD_INDEX, INDEX_CARD
import numpy as np

v = np.vectorize(visualize_bitboard)

monkey = ONITAMA_CARDS["monkey"]

frog = ONITAMA_CARDS["frog"]

move = Move(Point(0, 0), Point(1, 1), "monkey")

g = Game()
h = Game.from_string("""rrRr.\n...r.\n.....\n..B..\nbb.bb""",
                     red_cards=["frog", "mantis"],
                     neutral_card="crane",
                     blue_cards=["rabbit", "dragon"],
                     starting_player=0)