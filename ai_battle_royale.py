import argparse
from datetime import datetime, timedelta
from game import ONITAMA_CARDS, Game, OnitamaAI, Point


def run_game(args):
    max_turns = args.max_turns
    time_limit_ms = args.time_limit_ms

    if args.load_state:
        g = Game.from_serialized(args.load_state)
    else:
        g = Game()

    red_ai = OnitamaAI(g, 0, args.red)
    blue_ai = OnitamaAI(g, 1, args.blue)

    print("Red is", args.red, "Blue is", args.blue)

    for i in range(max_turns):
        if args.verbose:
            print("Turn", i // 2 + 1, "red" if g.current_player == 0 else "blue")
            print(g.visualize())

        if g.current_player == 0:
            if args.verbose:
                print("Red AI is thinking...")
            now = datetime.now()
            ai_move, best_score, depth = red_ai.decide_move(think_time=time_limit_ms, verbose=args.verbose)
            g.apply_move(ai_move)
            if args.verbose:
                print("AI plays", ai_move, f"(Evaluation: {best_score} at depth {depth})")
                print("AI took", (datetime.now() - now).total_seconds(), "s")

            if g.determine_winner() == -1:
                print(g.visualize())
                print("Red wins!")
                return i
        else:
            if args.verbose:
                print("Blue AI is thinking...")
            now = datetime.now()
            ai_move, best_score, depth = blue_ai.decide_move(think_time=time_limit_ms, verbose=args.verbose)
            g.apply_move(ai_move)
            if args.verbose:
                print("AI plays", ai_move, f"(Evaluation: {best_score} at depth {depth})")
                print("AI took", (datetime.now() - now).total_seconds(), "s")

            if g.determine_winner() == 1:
                print(g.visualize())
                print("Blue wins!")
                return i
    print(g.visualize())
    print("Draw due to round limit")
    return i

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--load_state", default=None, type=int)
    parser.add_argument("--red", default=0, help="0 for piece evaluation, 2 for combined", type=int)
    parser.add_argument("--blue", default=0, help="0 for piece evaluation, 2 for combined", type=int)
    parser.add_argument("-t", "--time_limit_ms", default=10000, type=int)
    parser.add_argument("-m", "--max_turns", default=50, type=int)
    parser.add_argument("-v", "--verbose", default=False, action="store_true")

    args = parser.parse_args()

    start = datetime.now()
    num_moves = run_game(args)
    print("Game took", (datetime.now() - start).total_seconds(), "s and", num_moves, "moves")