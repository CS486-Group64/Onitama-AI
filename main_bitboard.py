from game import ONITAMA_CARDS, Game, Move, OnitamaAI, Point, visualize_bitboard, CARD_INDEX, INDEX_CARD
import numpy as np

v = np.vectorize(visualize_bitboard)

monkey = ONITAMA_CARDS["monkey"]

frog = ONITAMA_CARDS["frog"]

move = Move(Point(0, 0), Point(1, 1), "monkey")