import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
HEX_SIZE = 40  # Distance from center to corner
HEX_SPACING = HEX_SIZE * 2  # Distance between hex centers
GRID_ROWS = 8
GRID_COLS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
PLAYER1_COLOR = (0, 0, 255)    # Blue
PLAYER2_COLOR = (255, 0, 0)    # Red

# Setup display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Hexagonal Grid")

# Add these variables after the screen setup
selected_points = []
lines = []
adjacency_list = {}  # Store connections between points
all_triangles = set()  # Store all found triangles
current_player = 1  # 1 or 2
line_owners = {}  # Store which player owns each line
triangle_owners = {}  # Store which player owns each triangle

def get_hex_center(row, col):
    # Calculate the center position of each hexagon
    x = col * (HEX_SIZE * 1.5)
    y = row * (HEX_SIZE * math.sqrt(3)) + (HEX_SIZE * math.sqrt(3) / 2) - col * (HEX_SIZE * math.sqrt(3) / 2)
    return (x + 200 , y + 200)  # Offset from screen edge

def draw_hex_grid():
    # List of coordinates to display (row, col)
    coordinates = [(0, 0), (1, 0), (2,0), (0,1), (1,1), (2,1),(3,1), (0,2), (1,2), (2,2), (3,2), (4,2),(1,3), (2,3), (3,3), (4,3), (2,4), (3,4), (4,4)]  # Example coordinates
    
    for row, col in coordinates:
        center = get_hex_center(row, col)
        pygame.draw.circle(screen, WHITE, (int(center[0]), int(center[1])), 3)
        
        # Calculate the correct coordinate label
        coord_text = f"{row},{col}"
        font = pygame.font.Font(None, 20)
        text_surface = font.render(coord_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(center[0], center[1] + 15))
        screen.blit(text_surface, text_rect)
    
    # Draw existing lines
    for start, end in lines:
        pygame.draw.line(screen, WHITE, start, end, 2)
    
    # Draw currently selected point
    if len(selected_points) == 1:
        pygame.draw.circle(screen, (255, 0, 0), selected_points[0], 5)
    
    # Draw dots at the center of each triangle
    for triangle in all_triangles:
        center = get_triangle_center(triangle)
        pygame.draw.circle(screen, (255, 0, 0), center, 4)  # Red dot with radius 4
    
    # Draw lines with player colors
    for (start, end), player in line_owners.items():
        color = PLAYER1_COLOR if player == 1 else PLAYER2_COLOR
        pygame.draw.line(screen, color, get_hex_center(*start), get_hex_center(*end), 2)
    
    # Draw dots at the center of each triangle with player colors
    for triangle in all_triangles:
        center = get_triangle_center(triangle)
        color = PLAYER1_COLOR if triangle_owners[triangle] == 1 else PLAYER2_COLOR
        pygame.draw.circle(screen, color, center, 4)

def get_nearest_hex_point(mouse_pos):
    # List of valid coordinates
    coordinates = [(0, 0), (1, 0), (2,0), (0,1), (1,1), (2,1), (3,1), (0,2), (1,2), 
                  (2,2), (3,2), (4,2), (1,3), (2,3), (3,3), (4,3), (2,4), (3,4), (4,4)]
    
    min_dist = float('inf')
    nearest_point = None
    
    for row, col in coordinates:
        center = get_hex_center(row, col)
        dist = math.sqrt((mouse_pos[0] - center[0])**2 + (mouse_pos[1] - center[1])**2)
        if dist < min_dist:
            min_dist = dist
            nearest_point = center
    
    return nearest_point if min_dist < HEX_SIZE else None

def is_valid_connection(point1, point2):
    row1, col1 = point1
    row2, col2 = point2
    
    # Sort points so row1 <= row2
    if row1 > row2:
        row1, row2 = row2, row1
        col1, col2 = col2, col1
    
    row_diff = row2 - row1
    col_diff = col2 - col1
    
    # Only row changing
    if col1 == col2:
        return True
    # Only column changing
    elif row1 == row2:
        return True
    
    # Both changing by 1
    elif row_diff == col_diff:
        return True
    return False

def find_triangles_for_line(points, adjacency_list):
    triangles = set()
    print(points)
    # Only check points that are part of the new line
    for point in points:
        # Get neighbors of current point
        neighbors = adjacency_list.get(point, set())
        
        # Check pairs of neighbors for triangles
        for neighbor1 in neighbors:
            for neighbor2 in neighbors:
                # Skip if same neighbor
                if neighbor1 >= neighbor2:
                    continue
                    
                # Check if these neighbors are connected to each other
                if neighbor2 in adjacency_list.get(neighbor1, set()):
                    # Sort points to ensure unique triangle representation
                    triangle = tuple(sorted([point, neighbor1, neighbor2]))
                    triangles.add(triangle)   
    
    return triangles

def add_connection(point1, point2):
    global current_player
    
    # Order points in ascending order
    if point1 > point2:
        point1, point2 = point2, point1
        
    # Convert pixel coordinates back to grid coordinates
    coordinates = [(0, 0), (1, 0), (2,0), (0,1), (1,1), (2,1), (3,1), (0,2), (1,2), 
                  (2,2), (3,2), (4,2), (1,3), (2,3), (3,3), (4,3), (2,4), (3,4), (4,4)]
    
    # Find grid coordinates for both points
    grid_points = []
    for point in [point1, point2]:
        for row, col in coordinates:
            if get_hex_center(row, col) == point:
                grid_points.append((row, col))
                break
    
    if len(grid_points) != 2:
        return False
        
    p1, p2 = grid_points
    if not is_valid_connection(p1, p2):
        return False
    
    # Add points to adjacency list
    if p1 not in adjacency_list:
        adjacency_list[p1] = set()
    if p2 not in adjacency_list:
        adjacency_list[p2] = set()
    
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
                if curr_point not in adjacency_list:
                    adjacency_list[curr_point] = set()
                if next_point not in adjacency_list:
                    adjacency_list[next_point] = set()
                adjacency_list[curr_point].add(next_point)
                adjacency_list[next_point].add(curr_point)
    
    # If only column is changing, connect all intermediate points
    elif row1 == row2:
        for col in range(min(col1, col2), max(col1, col2) + 1):
            curr_point = (row1, col)
            next_point = (row1, col + 1)
            if col < max(col1, col2):
                points.append(next_point)
                if curr_point not in adjacency_list:
                    adjacency_list[curr_point] = set()
                if next_point not in adjacency_list:
                    adjacency_list[next_point] = set()
                adjacency_list[curr_point].add(next_point)
                adjacency_list[next_point].add(curr_point)
    
    # If both row and column are changing, connect all intermediate points diagonally
    else:
        for i in range(abs(row2 - row1)):
            curr_point = (min(row1, row2) + i, min(col1, col2) + i)
            next_point = (min(row1, row2) + i + 1, min(col1, col2) + i + 1)
            points.append(next_point)
            if curr_point not in adjacency_list:
                adjacency_list[curr_point] = set()
            if next_point not in adjacency_list:
                adjacency_list[next_point] = set()
            adjacency_list[curr_point].add(next_point)
            adjacency_list[next_point].add(curr_point)

    # Store the line owner
    line = tuple(sorted([p1, p2]))
    line_owners[line] = current_player
    
    # After adding connections, check for new triangles
    new_triangles = find_triangles_for_line(points, adjacency_list)
    for triangle in new_triangles:
        if triangle not in all_triangles:
            all_triangles.add(triangle)
            triangle_owners[triangle] = current_player
    
    # Switch players
    current_player = 3 - current_player  # Toggles between 1 and 2
    
    return True

def get_triangle_center(triangle_points):
    # Calculate centroid (average of all points)
    centers = [get_hex_center(*p) for p in triangle_points]
    x = sum(c[0] for c in centers) / 3
    y = sum(c[1] for c in centers) / 3
    return (int(x), int(y))

# Optional: Add current player indicator
def draw_current_player():
    font = pygame.font.Font(None, 36)
    text = f"Player {current_player}'s turn"
    color = PLAYER1_COLOR if current_player == 1 else PLAYER2_COLOR
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (10, 10))

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                nearest_point = get_nearest_hex_point(pygame.mouse.get_pos())
                if nearest_point:
                    selected_points.append(nearest_point)
                    
                    # When we have two points, try to create a connection
                    if len(selected_points) == 2:
                        if add_connection(selected_points[0], selected_points[1]):
                            lines.append((selected_points[0], selected_points[1]))
                        selected_points = []
            elif event.button == 3:  # Right click
                selected_points = []  # Clear selection
    
    # Clear screen
    screen.fill(BLACK)
    
    # Draw the hexagonal grid
    draw_hex_grid()

    # Draw current player indicator
    draw_current_player()
    
    # Update display
    pygame.display.flip()

pygame.quit()
