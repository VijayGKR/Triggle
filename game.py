class HexGame:
    def __init__(self):
        self.current_player = 1
        self.adjacency_list = {}
        self.line_owners = {}
        self.triangle_owners = {}
        self.all_triangles = set()
        self.game_over = False
        self.winner = None
        self.hex_size = 3
        self.valid_points = self.init_valid_points()
        self.valid_moves = self.init_valid_moves()
        
    def init_valid_points(self):
        """Returns list of all valid (row, col) coordinates on the hex grid"""
        valid_points = []
        # First half - increasing columns (including middle row)

        for col in range(self.hex_size):
            for row in range(col + self.hex_size):
                valid_points.append((row, col))
        
        max_col = self.hex_size * 2 - 2

        count = 1
        for col in range(self.hex_size, max_col + 1):
            for row in range(count, max_col + 1):
                valid_points.append((row, col))
            count += 1
                
        return valid_points
    
    def init_valid_moves(self):
        """Returns list of all valid moves (point1, point2) that can be made"""
        valid_moves = set()
        points = self.valid_points
        
        for p1 in points:
            for p2 in points:  
                row1, col1 = p1
                row2, col2 = p2

                if p1 == p2:
                    continue
                
                # Sort points so row1 <= row2
                if row1 > row2:
                    row1, row2 = row2, row1
                    col1, col2 = col2, col1
                
                row_diff = row2 - row1
                col_diff = col2 - col1
                
                # Only row changing
                if col1 == col2:
                    valid_moves.add(tuple(sorted([p1, p2])))
                # Only column changing
                elif row1 == row2:
                    valid_moves.add(tuple(sorted([p1, p2])))
                
                # Both changing equally
                elif row_diff == col_diff:
                    valid_moves.add(tuple(sorted([p1, p2])))

        return valid_moves
    
    def make_move(self, point1, point2):
        """
        Attempts to make a move. Returns a dict with move results.
        Returns:
            {
                'valid': bool,  # Whether move was valid and executed
                'triangles_formed': set(),  # New triangles formed by this move
                'game_over': bool,  # Whether game is now over
                'winner': int or None,  # Winner if game is over
                'current_player': int  # Next player's turn
            }
        """
        if not self.is_valid_connection(point1, point2):
            return {'valid': False}
            
        new_triangles = self.add_connection(point1, point2)

        if(self.get_scores()[1] > (3 * self.hex_size - 3) * (self.hex_size - 1) or self.get_scores()[2] > (3 * self.hex_size - 3) * (self.hex_size - 1)):
            self.game_over = True
            self.winner = 3 - self.current_player

        if(self.get_scores()[1] == (3 * self.hex_size - 3) * (self.hex_size - 1) and self.get_scores()[2] == (3 * self.hex_size - 3) * (self.hex_size - 1)):
            self.game_over = True
            self.winner = 0
        
        return {
            'valid': True,
            'game_over': self.game_over,
            'triangles_formed': new_triangles,
            'winner': self.winner,
            'current_player': self.current_player
        }
    
    def get_state(self):
        """
        Returns complete game state for rendering or analysis
        """
        return {
            'current_player': self.current_player,
            'line_owners': self.line_owners,  # {(point1, point2): player_num}
            'triangle_owners': self.triangle_owners,  # {(p1,p2,p3): player_num}
            'game_over': self.game_over,
            'winner': self.winner,
            'scores': self.get_scores(),
            'adjacency_list': self.adjacency_list,
            'hex_size': self.hex_size,
            'all_triangles': self.all_triangles
        }
    
    def get_scores(self):
        """Returns current score for each player"""
        p1_triangles = sum(1 for owner in self.triangle_owners.values() if owner == 1)
        p2_triangles = sum(1 for owner in self.triangle_owners.values() if owner == 2)
        return {1: p1_triangles, 2: p2_triangles}
    
    def reset(self):
        """Resets game to initial state"""
        self.__init__()

    def is_valid_connection(self,point1, point2):
        return tuple(sorted([point1, point2])) in self.valid_moves
    
    def find_triangles_for_line(self,points):
        triangles = set()
        # Only check points that are part of the new line
        for point in points:
            # Get neighbors of current point
            neighbors = self.adjacency_list.get(point, set())
            
            # Check pairs of neighbors for triangles
            for neighbor1 in neighbors:
                for neighbor2 in neighbors:
                    # Skip if same neighbor
                    if neighbor1 >= neighbor2:
                        continue
                        
                    # Check if these neighbors are connected to each other
                    if neighbor2 in self.adjacency_list.get(neighbor1, set()):
                        # Sort points to ensure unique triangle representation
                        triangle = tuple(sorted([point, neighbor1, neighbor2]))
                        triangles.add(triangle)  

        return triangles

    def add_connection(self,point1, point2):
        global current_player
        
        # Order points in ascending order
        if point1 > point2:
            point1, point2 = point2, point1
            
        p1 = point1
        p2 = point2

        # Add points to adjacency list
        if p1 not in self.adjacency_list:
            self.adjacency_list[p1] = set()
        if p2 not in self.adjacency_list:
            self.adjacency_list[p2] = set()
        
        # Add connections
        row1, col1 = p1
        row2, col2 = p2

        points = [p1]
        
        # If only row is changing, connect all intermediate points
        if col1 == col2:
            for row in range(min(row1, row2), max(row1, row2) + 1):
                curr_point = (row, col1)
                next_point = (row + 1, col1)
                if row < max(row1, row2):
                    points.append(next_point)
                    if curr_point not in self.adjacency_list:
                        self.adjacency_list[curr_point] = set()
                    if next_point not in self.adjacency_list:
                        self.adjacency_list[next_point] = set()
                    self.adjacency_list[curr_point].add(next_point)
                    self.adjacency_list[next_point].add(curr_point)
                
            for row in range(min(row1, row2), max(row1, row2) + 1):
                for row_2 in range(row, max(row1, row2) + 1):
                    self.valid_moves.discard(tuple(sorted([(row, col1), (row_2, col1)])))   

        
        # If only column is changing, connect all intermediate points
        elif row1 == row2:
            for col in range(min(col1, col2), max(col1, col2) + 1):
                curr_point = (row1, col)
                next_point = (row1, col + 1)
                if col < max(col1, col2):
                    points.append(next_point)
                    if curr_point not in self.adjacency_list:
                        self.adjacency_list[curr_point] = set()
                    if next_point not in self.adjacency_list:
                        self.adjacency_list[next_point] = set()
                    self.adjacency_list[curr_point].add(next_point)
                    self.adjacency_list[next_point].add(curr_point)
            
            for col in range(min(col1, col2), max(col1, col2) + 1):
                for col_2 in range(col, max(col1, col2) + 1):
                    self.valid_moves.discard(tuple(sorted([(row1, col), (row1, col_2)])))   

        # If both row and column are changing, connect all intermediate points diagonally
        else:
            for i in range(abs(row2 - row1)):
                curr_point = (min(row1, row2) + i, min(col1, col2) + i)
                next_point = (min(row1, row2) + i + 1, min(col1, col2) + i + 1)
                points.append(next_point)
                if curr_point not in self.adjacency_list:
                    self.adjacency_list[curr_point] = set()
                if next_point not in self.adjacency_list:
                    self.adjacency_list[next_point] = set()
                self.adjacency_list[curr_point].add(next_point)
                self.adjacency_list[next_point].add(curr_point)
            
            for i in range(abs(row2 - row1)):
                for i_2 in range(i, abs(row2 - row1) + 1):
                    self.valid_moves.discard(tuple(sorted([(min(row1, row2) + i, min(col1, col2) + i), (min(row1, row2) + i_2, min(col1, col2) + i_2)])))

        # Store the line owner
        line = tuple(sorted([p1, p2]))
        self.line_owners[line] = self.current_player
        
        # After adding connections, check for new triangles
        triangles = self.find_triangles_for_line(points)
        new_triangles = set()
        for triangle in triangles:
            if triangle not in self.all_triangles:
                new_triangles.add(triangle)
                self.all_triangles.add(triangle)
                self.triangle_owners[triangle] = self.current_player
        
        # Switch players
        self.current_player = 3 - self.current_player  # Toggles between 1 and 2
        
        return new_triangles
    
    def copy(self):
        """Returns a deep copy of the current game state"""
        import copy
        new_game = HexGame()
        new_game.current_player = self.current_player
        new_game.adjacency_list = copy.deepcopy(self.adjacency_list)
        new_game.line_owners = copy.deepcopy(self.line_owners)
        new_game.triangle_owners = copy.deepcopy(self.triangle_owners)
        new_game.all_triangles = copy.deepcopy(self.all_triangles)
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        new_game.hex_size = self.hex_size
        new_game.valid_points = copy.deepcopy(self.valid_points)
        return new_game

if __name__ == "__main__":
    game = HexGame()
    print(game.valid_points)