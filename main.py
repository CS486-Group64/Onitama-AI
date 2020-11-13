import argparse
from datetime import datetime, timedelta
from game import ONITAMA_CARDS, Game, OnitamaAI, Point


def run_game(args):
    human = args.human
    max_turns = args.max_turns
    time_limit_ms = args.time_limit_ms

    if args.load_state:
        g = Game.from_serialized(args.load_state)
    else:
        g = Game()
    
    ai = OnitamaAI(g, 1 - human)
    human_id = human * 2 - 1

    print("Human is", "red" if human == 0 else "blue")

    for i in range(max_turns):
        print("Turn", i // 2 + 1, "red" if g.current_player == 0 else "blue")
        print(g.visualize())

        if g.current_player == human:
            human_move = None

            while human_move is None:
                legal_moves = list(g.legal_moves())
                move_str = input("Enter your move. Format: card start end (e.g. tiger c1 c3). "
                                 "Type 'quit' to quit. Type 'hint [depth]' for the ai's suggestion. "
                                 "Type 'debug' to open an interactive console.\n> ")
                if move_str == "quit":
                    return
                elif move_str.startswith("hint"):
                    depth_limit = None
                    try:
                        depth_limit = int(move_str[len("hint "):])
                    except ValueError:
                        pass
                    print("AI is thinking...")
                    if depth_limit is None:
                        ai_move, best_score, depth = ai.decide_move(think_time=time_limit_ms, verbose=args.verbose)
                    else:
                        ai_move, best_score, depth = ai.decide_move(
                            think_time=1000000, depth_limit=depth_limit, verbose=args.verbose)
                    print("AI recommends", ai_move, f"(Evaluation: {best_score} at depth {depth})")
                    print(g.visualize())
                    continue
                elif move_str == "debug":
                    import pdb
                    pdb.set_trace()
                params = move_str.split(" ")
                if len(params) == 3:
                    card = params[0]
                    start = Point.from_algebraic_notation(params[1]).to_index()
                    end = Point.from_algebraic_notation(params[2]).to_index()
                    
                    for move in legal_moves:
                        if move.card == card and move.start == start and move.end == end:
                            human_move = move
                            break
                    if human_move:
                        break
                print(g.visualize())
                print("Invalid move. Valid moves:", ", ".join(map(str, legal_moves)))
            
            g.apply_move(human_move)

            if g.determine_winner() == human_id:
                print(g.visualize())
                print("Human wins!")
                return
        else:
            print("AI is thinking...")
            now = datetime.now()
            ai_move, best_score, depth = ai.decide_move(think_time=time_limit_ms, verbose=args.verbose)
            print("AI plays", ai_move, f"(Evaluation: {best_score} at depth {depth})")
            g.apply_move(ai_move)
            print("AI took", (datetime.now() - now).total_seconds(), "s")

            if g.determine_winner() == -human_id:
                print(g.visualize())
                print("AI wins!")
                return
    print(g.visualize())
    print("Draw due to round limit")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--load_state", default=None, type=int)
    parser.add_argument("--human", default=1, help="0 is red, 1 is blue", type=int)
    parser.add_argument("-t", "--time_limit_ms", default=200, type=int)
    parser.add_argument("-m", "--max_turns", default=100, type=int)
    parser.add_argument("-v", "--verbose", default=False, action="store_true")

    args = parser.parse_args()

    run_game(args)