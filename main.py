from datetime import datetime, timedelta
from game import ONITAMA_CARDS, Game, OnitamaAI, Point


def run_game(human, max_turns=100):
    # TODO figure out why ai doesn't recognize mate in one
    human_id = human * 2 - 1
    for i in range(max_turns):
        print("Turn", i // 2 + 1, "red" if g.current_player == 0 else "blue")
        print(g.visualize())

        if g.current_player == human:
            human_move = None

            while human_move is None:
                legal_moves = list(g.legal_moves())
                move_str = input("Enter your move. Format: card start end (e.g. tiger c1 c3). "
                                 "Type 'quit' to quit. Type 'hint' for the ai's suggestion. "
                                 "Type 'debug' to open an interactive console.\n> ")
                if move_str == "quit":
                    return
                elif move_str == "hint":
                    print("AI is thinking...")
                    ai_move, best_score, depth = ai.decide_move()
                    print("AI recommends", ai_move, f"(Evaluation: {best_score} at depth {depth})")
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
            ai_move, best_score, depth = ai.decide_move()
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
    time_limit = 0
    while not time_limit:
        try:
            time_limit_str = input("Enter AI time limit in milliseconds (default 200ms): ")
            if time_limit_str:
                time_limit = int(time_limit_str)
            else:
                time_limit = 200
        except ValueError:
            print("Time limit must be an integer.")

    human = 1 # blue
    g = Game()

    ai = OnitamaAI(g, 1 - human, timedelta(milliseconds=time_limit))

    print("Human is", "red" if human == 0 else "blue")

    run_game(human)