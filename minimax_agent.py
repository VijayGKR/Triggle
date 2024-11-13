from game import HexGame
import random
class MinimaxAgent:
    def __init__(self, player_number):
        self.player_number = player_number
        self.max_depth = 2  # Adjust this based on performance needs

    def get_move(self, game):
        """Returns the best move according to the minimax algorithm"""
        best_score = float('-inf')
        best_move = None

        valid_moves = game.get_valid_moves()
        #print(f"Valid moves: {valid_moves}")

        for move in valid_moves:
            # Create a copy of the game state
            game_copy = game.copy()

            point1, point2 = move
            # Make the move
            result = game_copy.make_move(point1, point2)

            if result['valid']:

                score = self._minimax(game_copy, self.max_depth - 1, False)

                if score > best_score:
                    best_score = score
                    best_move = move

                if score == best_score:
                    if random.choice([True, False]):
                        best_move = move

        if(best_move is None and len(valid_moves) > 0):
            best_move = random.choice(list(valid_moves))

        #print(f"Best move: {best_move} with score: {best_score}")
        return best_move

    def _minimax(self, game, depth, is_maximizing):
        """Recursive minimax implementation"""
        # Base cases
        if game.game_over:
            if game.winner == self.player_number:
                return float('inf')
            elif game.winner == 3 - self.player_number:
                return float('-inf')
            else:
                return 0 

        if depth == 0:
            return self._evaluate_position(game)

        valid_moves = game.get_valid_moves()

        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                game_copy = game.copy()
                point1, point2 = move
                result = game_copy.make_move(point1, point2)

                if result['valid']:
                    eval = self._minimax(game_copy, depth - 1, False)
                    max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                game_copy = game.copy()
                point1, point2 = move
                result = game_copy.make_move(point1, point2)

                if result['valid']:
                    eval = self._minimax(game_copy, depth - 1, True)
                    min_eval = min(min_eval, eval)
            return min_eval

    def _evaluate_position(self, game):
        """
        Evaluates the current game position from the perspective of the agent's player.
        Returns a numerical score where higher is better for the agent.
        """
        scores = game.get_scores()
        if game.winner == self.player_number:
            return float('inf')
        elif game.winner == 3 - self.player_number:
            return float('-inf')
        else:
            # Heuristic: difference in scores
            return scores[self.player_number] - scores[3 - self.player_number]
