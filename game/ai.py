from datetime import datetime, timedelta
import random

from . import Game

INF = 1000

class OnitamaAI:
    def __init__(self, game, ai_player=-1, time_limit=timedelta(milliseconds=500)):
        self.game = game
        self.ai_player = ai_player
        self.state_cache = {}
        self.time_limit = time_limit
        self.start_time = None
    
    def minimax(self, game: Game, depth, alpha, beta):
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

                game_score = self.minimax(new_game, depth - 1, alpha, beta)
                self.state_cache[depth - 1, new_game.serialize()] = game_score

                best_score = max(best_score, game_score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
                if datetime.now() - self.start_time > self.time_limit:
                    break
            return best_score
        else:
            best_score = INF
            for move in game.legal_moves():
                new_game = game.copy()
                new_game.apply_move(move)

                game_score = self.minimax(new_game, depth - 1, alpha, beta)
                self.state_cache[depth - 1, new_game.serialize()] = game_score

                best_score = min(best_score, game_score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
                if datetime.now() - self.start_time > self.time_limit:
                    break
            return best_score
    
    def decide_move(self):
        self.start_time = datetime.now()
        assert self.game.current_player == self.ai_player
        best_move = []
        best_score = -INF * self.ai_player
        
        # Perform iterative deepening search
        depth = 0
        while datetime.now() - self.start_time < self.time_limit:
            depth += 1
            for move in self.game.legal_moves():
                new_game = self.game.copy()
                new_game.apply_move(move)

                game_score = self.minimax(new_game, depth, -INF, INF)
                self.state_cache[1, new_game.serialize()] = game_score

                if self.ai_player * game_score > self.ai_player * best_score:
                    best_score = game_score
                    best_move = [move]
                elif game_score == best_score:
                    best_move.append(move)
        ai_move = random.choice(best_move)
        print("AI plays", ai_move, f"(Evaluation: {best_score} at depth {depth})")
        self.game.apply_move(ai_move)
