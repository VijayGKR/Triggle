from game import HexGame

class MinimaxAgent:
    def __init__(self, player_number):
        self.player_number = player_number
        self.max_depth = 3  # Adjust this based on performance needs
        
    def get_move(self, game):
        """Returns the best move according to the minimax algorithm"""
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        valid_moves = game.get_valid_moves()
        print(valid_moves)
        
        for move in valid_moves:
            # Create a copy of the game state
            game_copy = game.copy()
            
            # Make the move
            point1, point2 = move
            result = game_copy.make_move(point1, point2)
            
            if result['valid']:
                score = self._minimax(game_copy, self.max_depth - 1, False, alpha, beta)
                
                if score > best_score:
                    best_score = score
                    best_move = move
                
                alpha = max(alpha, best_score)
        print(best_score)
        return best_move
    
    def _minimax(self, game, depth, is_maximizing, alpha, beta):
        """Recursive minimax implementation with alpha-beta pruning"""
        # Base cases
        if game.game_over:
            return float('inf') if game.winner == self.player_number else float('-inf')
        
        if depth == 0:
            return self._evaluate_position(game)
            
        valid_moves = game.get_valid_moves()
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                # Create a copy of the game state
                game_copy = game.copy()
                
                point1, point2 = move
                result = game_copy.make_move(point1, point2)
                
                if result['valid']:
                    eval = self._minimax(game_copy, depth - 1, False, alpha, beta)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                # Create a copy of the game state
                game_copy = game.copy()
                
                point1, point2 = move
                result = game_copy.make_move(point1, point2)
                
                if result['valid']:
                    eval = self._minimax(game_copy, depth - 1, True, alpha, beta)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval
    
    def _evaluate_position(self, game):
        """
        Evaluates the current game position from the perspective of the agent's player
        Returns a numerical score where higher is better for the agent
        """
        scores = game.get_scores()
        if(game.winner == self.player_number):
            return float('inf')
        elif(game.winner == 3 - self.player_number):
            return float('-inf')
        else:
            return scores[self.player_number] - scores[3 - self.player_number]