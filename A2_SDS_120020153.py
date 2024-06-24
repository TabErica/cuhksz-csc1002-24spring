import turtle
import random

# Global Variables
puzzle_size = 0  # This will be set based on user input
puzzle = []
tiles = []
tiles_num = []
puzzle_solved = False  # Track if the puzzle is solved
empty_position = (0, 0)

#Constants
EMPTY_SPACE = 0
tile_size = 80

def generate_solvable_puzzle():
    """Generate a solvable puzzle configuration."""
    global puzzle
    while True:
        flat_puzzle = random.sample(range(puzzle_size ** 2), puzzle_size ** 2)
        puzzle = [flat_puzzle[i * puzzle_size:(i + 1) * puzzle_size] \
            for i in range(puzzle_size)]
        if is_solvable(puzzle):
            return puzzle

def is_solvable(puzzle):
    """Determine if a puzzle is solvable."""
    inversion_count = 0
    flat_puzzle = [num for row in puzzle for num in row]
    blank_row = 0  # The row where the blank tile (0) is found, counting from the bottom

    # Find the row position of the blank space from the bottom
    for i in range(len(puzzle)):
        if EMPTY_SPACE in puzzle[i]:
            # Assuming bottom row is 1, adjust accordingly
            blank_row = len(puzzle) - i
            break

    # Compute inversions for all numbers except the blank
    for i in range(len(flat_puzzle)):
        for j in range(i + 1, len(flat_puzzle)):
            if flat_puzzle[i] != EMPTY_SPACE and flat_puzzle[j] != EMPTY_SPACE and flat_puzzle[i] > flat_puzzle[j]:
                inversion_count += 1

    # For odd-size grids, solvability is determined by whether the inversion count is even
    if len(puzzle) % 2 != 0:
        return inversion_count % 2 == 0
    else:
        # For even-size grids, add the inversion count and the blank's row. If the sum is even, the puzzle is solvable
        return (inversion_count + blank_row) % 2 == 0


def find_empty_space():
    """Find the row and column of the empty space."""
    for i, row in enumerate(puzzle):
        for j, val in enumerate(row):
            if val == EMPTY_SPACE:
                return i, j
            
def is_solved():
    """Check if the puzzle is solved."""
    global puzzle_solved, puzzle 
    target = list(range(1, puzzle_size ** 2)) + [EMPTY_SPACE]
    if [tile for row in puzzle for tile in row] == target:
        puzzle_solved = True  # Set puzzle_solved to True

class NumberedTile(turtle.Turtle):
    """A turtle graphics class for creating tiles with number attributes."""
    def __init__(self, number, sz=3, border=5):
        super().__init__(shape='square')
        self.number = number 
        self.up() 
        self.shapesize(sz, sz, border)
        

def create_tile(number, x, y, tile_size=80, fill_color="lavender"):
    """
    Create and return a tile at the specified location with a given number.
    Args:
        number (int): number to assign to the tile
        x (int): X coordinate
        y (int): Y coordinate
        tile_size (int): size of tile, default to 80
        fill_color: color of the tile
    """
    tile_turtle = turtle.Turtle()
    tile_turtle.penup()
    tile_turtle.shape('square')
    tile_turtle.color(fill_color)
    tile_turtle.shapesize(stretch_wid=tile_size/20, stretch_len=tile_size/20)
    tile_turtle.speed('fastest')
    tile_turtle.goto(x, y)
    tile_turtle.number = number
    return tile_turtle

def create_number(number, x, y, tile_size=80, color = 'midnightblue'):
    """
    write a number and return it at the specified location with a given number.
    Args:
        number (int): number to paint
        x (int): X coordinate
        y (int): Y coordinate
        tile_size (int): size of tile, default to 80
        color: color of the written number
    """
    num_turtle = turtle.Turtle(visible=False)
    num_turtle.penup()
    num_turtle.color(color)
    num_turtle.speed('fastest')
    num_turtle.goto(x, y - tile_size / 8)
    num_turtle.write(number, align="center", font=("Arial", int(tile_size / 5), "bold"))
    return num_turtle

def get_screen_coordinates(row, col, tile_size=80, spacing=10):
    """
    Convert grid coordinates to screen coordinates for tile placement.
    
    Args: 
    row: row coordinate of a grid
    col: col coordinate of a grid
    
    intended as a helper function in display_tiles and sliding_hdlr 
    to calculate where on screen to put turtles.
    """
    sz = tile_size + spacing
    # Calculate the total width and height of the puzzle grid
    total_width = puzzle_size * (tile_size + spacing)
    total_height = puzzle_size * (tile_size + spacing)

    # Calculate the starting position to be centered based on the puzzle size
    start_x = -total_width / 2 + (sz / 2)
    start_y = total_height / 2 - (sz / 2)

    # Convert grid coordinates (row, col) to screen coordinates (x, y)
    x = start_x + col * (tile_size + spacing)
    y = start_y - row * (tile_size + spacing)

    return x, y


def display_puzzle(puzzle, tile_size=80, tile_color='lavender', num_color='midnightblue'):
    """
    Display all tiles for the puzzle on the screen.
    
    Based on the puzzle grid, calculate the x, y coordinates of the tiles and numbers,
    draw each tile and number using create_tile and create_number 
    
    Turn off animation for generating tiles 
    and reopen it after the tile generating for sliding activity.
    """
    global tiles, empty_position, puzzle_size
    tiles.clear()  # Clear the old tiles list
    turtle.tracer(0, 0)  # Turn off the animation for instant drawing

    # Create and display tiles (squares)
    for i, row in enumerate(puzzle):
        for j, number in enumerate(row):
            if number != EMPTY_SPACE:  # Only create and display non-empty tiles
                x, y = get_screen_coordinates(i, j, tile_size, spacing=10)
                tile = create_tile(number, x, y, tile_size, tile_color)
                tiles.append(tile)
            else:
                empty_position = (i, j)
    turtle.update()  # Update the screen after all drawing commands
    turtle.tracer(1,10) # Then turn on the animation

    # After all tiles are created, draw numbers on them
    for i, row in enumerate(puzzle):
        for j, number in enumerate(row):
            if number != EMPTY_SPACE:
                x, y = get_screen_coordinates(i, j, tile_size, spacing=10)
                num_turtle = create_number(number, x, y, tile_size, num_color)
                tiles_num.append(num_turtle)

    
def get_tile_index(tile):
    """
    given a specified tile,
    return the corresponding row and column index in the puzzle grid.
    """
    global tiles, puzzle
    for i, row in enumerate(puzzle):
        for j, number in enumerate(row):
            if number == tile.number:
                index = i, j
    return index
    
    
def sliding(tile, x, y):
    """
    Animate a tile sliding to a new position.
    Helper function used in sliding_hdlr
    
    Args: 
    tile: tile to move
    x: x coordinate of the destination
    y: y coordinate of the destination
    
    """
    global tiles, puzzle, empty_position
    number = tile.number
    num = tiles_num[tiles.index(tile)]
    num.clear()
    num.goto(x, y - tile_size / 8)
    tile.speed(3)
    tile.goto(x, y)
    num.write(number, align="center", font=("Arial", int(tile_size / 5), "bold"))
    

def update_puzzle(tile, empty_row, empty_col):
    """
    Update the puzzle array to reflect the moved tile.
    Helper function used in sliding hdler.
    
    Args:
    tile: the moved tile
    empty_row, empty_col: the grid coordinate of the empty space in puzzle array
    """
    global tiles, puzzle, empty_position 
    
    original_row, original_col = get_tile_index(tile)
    
    puzzle[empty_row][empty_col], puzzle[original_row][original_col] = \
    puzzle[original_row][original_col], EMPTY_SPACE
    
    empty_position = (original_row, original_col)
    
    
def is_adjacent(tile_row, tile_col):
    """
    Check if a tile is adjacent to the empty space.
    Helper function used in sliding hdler.
    """
    global empty_position
    
    empty_row, empty_col = empty_position
    if (tile_row == empty_row and abs(tile_col - empty_col) == 1) or \
       (tile_col == empty_col and abs(tile_row - empty_row) == 1):
        return True
    else:
        return False
    
    
def sliding_hdlr(tile):
    """
    Handle the tile sliding action, including checking for puzzle completion.
    Also checks whether this move leads to the puzzle being solved.
    """
    global empty_position, tiles, puzzle_solved
    empty_row, empty_col = empty_position
    if tile:
        if not puzzle_solved:
            tile_row, tile_col = get_tile_index(tile)
            x, y = get_screen_coordinates(empty_row, empty_col)
            if is_adjacent(tile_row, tile_col):
                sliding(tile, x, y)
                update_puzzle(tile, empty_row, empty_col)
    
    is_solved()
    if (puzzle_solved):
        display_puzzle(puzzle, tile_size=80, tile_color = 'red', num_color = 'pink')
        print("Congratulations! Puzzle solved!")
        return
    
        
def get_clicked_tile(x, y):
    """
    Get the tile object that was clicked by the user.
    Args:
    x, y: x and y coordinate on the screen
    """
    global tiles, puzzle_size
    for tile in tiles:
        if tile.isvisible():
            x_min, y_min = tile.xcor() - 40, tile.ycor() - 40
            x_max, y_max = tile.xcor() + 40, tile.ycor() + 40
            
            if x_min < x < x_max and y_min < y < y_max:
                return tile

def on_mouse_click(x, y):
    """Handle mouse click events on the turtle screen."""
    tile = get_clicked_tile(x, y)
    sliding_hdlr(tile)
        

if __name__ == "__main__":        
    s = turtle.Screen()
    s.setup(600,600)

    # Prompt the user to enter the puzzle size and initialize the grid puzzle
    puzzle_size = turtle.numinput("Puzzle Size", "Enter the size of the game (3-5):",\
        default=3, minval=3, maxval=5)
    puzzle_size = int(puzzle_size)
    puzzle = generate_solvable_puzzle() 
    
    # Display the puzzle after initializing
    display_puzzle(puzzle)
    
    # Enable event listening in the Turtle graphics window to respond to mouse clicks
    turtle.listen()
    turtle.onscreenclick(on_mouse_click) # Call on_mouse_click function when clicking
    turtle.Screen().mainloop()