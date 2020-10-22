from . import Game

class OnitamaAI:
    SEARCH_DEPTH = 6

    def __init__(self, game, ai_player=-1):
        self.game = game
        self.ai_player = ai_player
        self.state_cache = {}
    
    def decide_move(self):
        best_score = -100 * self.ai_player
        best_move = None

        for move in self.game.legal_moves():
            new_game = self.game.copy()
            new_game.apply_move(move)

            game_score = self.minimax(new_game, self.SEARCH_DEPTH - 1, self.ai_player * -1, -100, 100)

            self.state_cache[(self.SEARCH_DEPTH - 1, new_game.serialize())] = game_score

            if self.ai_player > 0 and game_score > best_score or self.ai_player < 0 and game_score < best_score:
                # blue and maximizing or red and minimizing
                best_score = game_score
                best_move = move
            
            # print(move, "scores", game_score)
        
        print("AI plays", best_move)
        self.game.apply_move(best_move)

    def minimax(self, game: Game, depth, current_player, alpha, beta):
        cached = self.state_cache.get((depth, game.serialize()))
        if cached:
            return cached
        if depth == 0:
            game_score = self.state_cache[(depth, game.serialize())] = game.evaluate()
            return game_score
        best_score = -100 * current_player
        moves = game.legal_moves()

        for move in moves:
            new_game = game.copy()
            new_game.apply_move(move)

            game_score = self.minimax(new_game, depth - 1, current_player * -1, alpha, beta)

            self.state_cache[(depth - 1, new_game.serialize())] = game_score

            if current_player > 0:
                best_score = max(best_score, game_score)
                alpha = max(alpha, best_score)
            else:
                best_score = min(best_score, game_score)
                beta = min(beta, best_score)
            
            if beta <= alpha:
                break
        
        self.state_cache[(depth, game.serialize())] = best_score
        return best_score
