from datetime import datetime
from game import ONITAMA_CARDS, Game, OnitamaAI, Point

human = 1 # blue
g = Game()

ai = OnitamaAI(g, -human)

print("Human is", "red" if human < 0 else "blue")


def run_game(max_turns=100):
    for i in range(max_turns):
        print("Turn", i // 2 + 1, "red" if g.current_player < 0 else "blue")
        print(g.visualize())

        if g.current_player == human:
            human_move = None

            while human_move is None:
                legal_moves = list(g.legal_moves())
                move_str = input("Enter your move. Format: card start end (e.g. tiger c1 c3). Type 'quit' to quit.\n> ")
                if move_str == "quit":
                    return
                params = move_str.split(" ")
                if len(params) == 3:
                    card = params[0]
                    start = Point.from_algebraic_notation(params[1])
                    end = Point.from_algebraic_notation(params[2])
                    
                    for move in legal_moves:
                        if move.card == card and move.start == start and move.end == end:
                            human_move = move
                            break
                    if human_move:
                        break
                print("Invalid move. Valid moves:", ", ".join(map(str, legal_moves)))
            
            g.apply_move(human_move)

            if g.determine_winner() == human:
                print(g.visualize())
                print("Human wins!")
                return
        elif g.current_player == -human:
            print("AI is thinking...")
            now = datetime.now()
            ai.decide_move()
            print("AI took", (datetime.now() - now).total_seconds(), "s")

            if g.determine_winner() == -human:
                print(g.visualize())
                print("AI wins!")
                return
    print(g.visualize())
    print("Draw due to round limit")

run_game()