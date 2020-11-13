from datetime import datetime, timedelta
import random

from . import Game, Move

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
    
    def evaluate_moves(self, depth_limit, think_time):
        time_limit = datetime.now() + timedelta(milliseconds=think_time)
        current_player = self.game.current_player * 2 - 1
        moves = {}
        
        # Perform iterative deepening search
        depth = 0
        while datetime.now() < time_limit and depth < depth_limit:
            depth += 1
            for move in self.game.legal_moves():
                new_game = self.game.copy()
                new_game.apply_move(move)

                game_score = self.minimax(new_game, depth, -INF, INF, time_limit)
                self.state_cache[depth, new_game.serialize()] = game_score

                # Override previous evaluations of this move as we search deeper
                moves[move.serialize()] = [game_score, depth]

        return moves
    
    def decide_move(self, depth_limit=1000, think_time=500, verbose=False):
        moves = self.evaluate_moves(depth_limit, think_time)
        current_player = self.game.current_player * 2 - 1
        best_moves = []
        best_score = -INF * current_player
        for serialized_move, (game_score, depth) in moves.items():
            if current_player * game_score > current_player * best_score:
                best_score = game_score
                best_moves = [serialized_move]
            elif game_score == best_score:
                best_moves.append(serialized_move)

        if verbose:
            for serialized_move in sorted(moves, key=lambda move: moves[move][0], reverse=self.game.current_player):
                move = Move.from_serialized(serialized_move)
                new_game = self.game.copy()
                new_game.apply_move(move)
                print(f"Move {move} evaluation {moves[serialized_move][0]} at depth {moves[serialized_move][1]} (new_game {new_game.serialize()})")
        ai_move = random.choice(best_moves)
        return Move.from_serialized(ai_move), best_score, moves[ai_move][1]
