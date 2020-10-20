from game import ONITAMA_CARDS, Game, OnitamaAI

human = 1 # blue
g = Game()

ai = OnitamaAI(g, -human)

print("Human is", "red" if human < 0 else "blue")


for i in range(100):
    print("Turn", i // 2 + 1, "red" if g.current_player < 0 else "blue")
    print(g)

    if g.current_player == human:
        human_move = None

        while human_move is None:
            move_str = input("Enter your move. Format: card startx starty endx endy\n> ")
            params = move_str.split(" ")
            card = params[0]
            startx = int(params[1])
            starty = int(params[2])
            endx = int(params[3])
            endy = int(params[4])
            
            legal_moves = g.legal_moves()
            for move in legal_moves:
                if move.card == card and move.start.x == startx and move.start.y == starty and move.end.x == endx and move.end.y == endy:
                    human_move = move
                    break
            else:
                print("Invalid move. Valid moves:", legal_moves)
        
        g.apply_move(human_move)

        if g.determine_winner() == human:
            print("Human wins!")
            break
    elif g.current_player == -human:
        ai.decide_move()

        if g.determine_winner() == -human:
            print("AI wins!")
            break
