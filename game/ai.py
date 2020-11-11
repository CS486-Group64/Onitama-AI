from datetime import datetime, timedelta
import random

from . import Game

INF = 1000

class OnitamaAI:
    def __init__(self, game, ai_player=0):
        self.game = game
        self.ai_player = ai_player * 2 - 1
        self.state_cache = {}
    
    def minimax(self, game: Game, depth, alpha, beta, time_limit=None):
        cached = self.state_cache.get((depth, game.serialize()))
        if cached:
            return cached
        if depth <= 0 or game.determine_winner():
            evaluation = game.evaluate()
            self.state_cache[depth, game.serialize()] = evaluation
            return evaluation
        if game.current_player > 0:
            best_score = -INF
            for move in game.legal_moves():
                new_game = game.copy()
                new_game.apply_move(move)

                game_score = self.minimax(new_game, depth - 1, alpha, beta, time_limit)
                self.state_cache[depth - 1, new_game.serialize()] = game_score

                best_score = max(best_score, game_score)
                alpha = max(alpha, best_score)
                if beta <= alpha or new_game.determine_winner():
                    break
                if time_limit and datetime.now() > time_limit:
                    break
            return best_score
        else:
            best_score = INF
            for move in game.legal_moves():
                new_game = game.copy()
                new_game.apply_move(move)

                game_score = self.minimax(new_game, depth - 1, alpha, beta, time_limit)
                self.state_cache[depth - 1, new_game.serialize()] = game_score

                best_score = min(best_score, game_score)
                beta = min(beta, best_score)
                if beta <= alpha or new_game.determine_winner():
                    break
                if time_limit and datetime.now() > time_limit:
                    break
            return best_score
    
    def decide_move(self, depth_limit=1000, think_time=500):
        time_limit = datetime.now() + timedelta(milliseconds=think_time)
        current_player = self.game.current_player * 2 - 1
        best_move = []
        best_score = -INF * current_player
        
        # Perform iterative deepening search
        depth = 0
        while datetime.now() < time_limit and depth < depth_limit:
            depth += 1
            for move in self.game.legal_moves():
                new_game = self.game.copy()
                new_game.apply_move(move)

                game_score = self.minimax(new_game, depth, -INF, INF, time_limit)
                self.state_cache[depth, new_game.serialize()] = game_score


                if current_player * game_score > current_player * best_score:
                    best_score = game_score
                    best_move = [move]
                elif game_score == best_score:
                    best_move.append(move)

                print(f"Move {move} evaluation {game_score} at depth {depth} (new_game: {new_game.serialize()})")
        ai_move = random.choice(best_move)
        return ai_move, best_score, depth
