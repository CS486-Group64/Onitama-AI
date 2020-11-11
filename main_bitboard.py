from game import ONITAMA_CARDS, Game, Move, OnitamaAI, Point, visualize_bitboard, count_trailing_zeroes, CARD_INDEX, INDEX_CARD
import numpy as np

v = np.vectorize(visualize_bitboard)

monkey = ONITAMA_CARDS["monkey"]

frog = ONITAMA_CARDS["frog"]

move = Move(Point(0, 0), Point(1, 1), "monkey")

g = Game()
h = Game.from_string("""rr.rr\n.R...\n..B..\n.....\nbb.bb""",
                     red_cards=["frog", "elephant"],
                     blue_cards=["tiger", "tiger"],
                     neutral_card="tiger",
                     starting_player=0)