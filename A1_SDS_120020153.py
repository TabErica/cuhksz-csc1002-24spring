import random

def display_introduction():
    """Display a brief introduction about the 8-tile sliding puzzle game."""
    print("Welcome to the 8-tile sliding puzzle game!")
    print("The objective is to arrange the tiles in sequential order from 1 to 8.")
    print("You will control the game by sliding tiles into the empty space using your chosen keys for left, right, up, and down movements.\n")

def validate_and_get_movement_keys():
    """Prompt for 4 unique letters for movement keys and validate them."""
    # Returns a dictionary mapping of the movement keys to the directions.
    while True:
        user_input = input("Enter 4 letters for left, right, up, and down movements (e.g., lrud): ").lower().strip()
        user_input = ''.join(user_input.split())  # Remove all whitespaces
        if len(user_input) != 4 or not user_input.isalpha() or len(set(user_input)) != 4:
            print("Invalid input. Please enter 4 unique letters without repetition or non-letter characters.")
            continue
        break

    return {'left': user_input[0], 'right': user_input[1], 'up': user_input[2], 'down': user_input[3]}

def is_solvable(puzzle):
    """Check if the puzzle configuration is solvable."""
    inversion_count = 0
    flat_puzzle = [tile for row in puzzle for tile in row if tile != 0]
    for i in range(len(flat_puzzle)):
        for j in range(i + 1, len(flat_puzzle)):
            if flat_puzzle[i] > flat_puzzle[j]:
                inversion_count += 1
    return inversion_count % 2 == 0

def generate_solvable_puzzle():
    """Generate a solvable puzzle configuration."""
    while True:
        puzzle = random.sample(range(9), 9)  # Generate a shuffled list of numbers 0-8
        puzzle = [puzzle[i:i+3] for i in range(0, 9, 3)]  # Convert the flat list to a 3x3 list
        if is_solvable(puzzle):
            return puzzle
        
def print_puzzle(puzzle):
    """Print the current puzzle state."""
    for row in puzzle:
        row_display = ' '.join(str(tile) if tile != 0 else ' ' for tile in row)
        print(f"{row_display}")
        
def find_empty_space(puzzle):
    """Find the empty space in the puzzle."""
    for i, row in enumerate(puzzle):
        for j, tile in enumerate(row):
            if tile == 0:
                return i, j
    return None  # This should never happen if the puzzle is correctly initialized.

def move_tile(puzzle, direction, movement_keys):
    """Move a tile in the specified direction."""
    # Returns True if the move was made, False otherwise.
    empty_i, empty_j = find_empty_space(puzzle)
    target_i, target_j = empty_i, empty_j  # Initialize target position with the current empty space position.

    if direction == movement_keys['left'] and empty_j < 2:
        target_j += 1
    elif direction == movement_keys['right'] and empty_j > 0:
        target_j -= 1
    elif direction == movement_keys['up'] and empty_i < 2:
        target_i += 1
    elif direction == movement_keys['down'] and empty_i > 0:
        target_i -= 1
    else:
        return False  # Invalid move.

    # Swap the empty space with the target tile.
    puzzle[empty_i][empty_j], puzzle[target_i][target_j] = puzzle[target_i][target_j], puzzle[empty_i][empty_j]
    return True

def get_valid_moves(puzzle, movement_keys):
    """Describe valid moves based on the current state."""
    empty_i, empty_j = find_empty_space(puzzle)
    moves = []
    if empty_j < 2: moves.append(f"left-{movement_keys['left']}")
    if empty_j > 0: moves.append(f"right-{movement_keys['right']}")
    if empty_i < 2: moves.append(f"up-{movement_keys['up']}")
    if empty_i > 0: moves.append(f"down-{movement_keys['down']}")
    return ', '.join(moves)

def is_solved(puzzle):
    """Check if the puzzle is solved."""
    target = list(range(1, 9)) + [0]  # The target sequence for a solved puzzle.
    flat_puzzle = [tile for row in puzzle for tile in row]
    return flat_puzzle == target

def main():
    display_introduction()
    movement_keys = validate_and_get_movement_keys()
    puzzle = generate_solvable_puzzle()
    move_count = 0

    while not is_solved(puzzle):
        print_puzzle(puzzle)
        print(f"Enter your move ({get_valid_moves(puzzle, movement_keys)})> ", end='')
        move = input().lower().strip()
        if move not in movement_keys.values():
            print("Invalid move. Please enter a valid move key.")
            continue
        if not move_tile(puzzle, move, movement_keys):
            print("Move not possible. Try a different direction.")
            continue
        move_count += 1

    print_puzzle(puzzle)
    print(f"Congratulations! You've solved the puzzle in {move_count} moves.")

    if input("Play again? (y/n): ").lower().startswith('y'):
        main()
    else:
        print("Thank you for playing. Goodbye!")

if __name__ == "__main__":
    main()

