import turtle
import random
from functools import partial
import time

g_screen = None
g_snake = None     # snake's head
g_monsters = []
g_paused = 0
g_snake_sz = 5     # size of the snake's tail
g_intro = None
g_key_pressed = None
g_status = None
g_time = 0 
g_motion = 'Paused'
g_block = 0 # If the snake's movement is blocked.
g_contacts = 0 # Contacts with monsters.

g_bodyInfo = []

g_food = [] # Food list
g_foodPos = [] # Positions


COLOR_BODY = ("blue", "black")
COLOR_HEAD = "red"
COLOR_MONSTER = "purple"
FONT_INTRO = ("Arial",16,"normal")
FONT_STATUS = ("Arial",20,"normal")
TIMER_SNAKE = 250   # refresh rate for snake
SZ_SQUARE = 20      # square size in pixels

DIM_PLAY_AREA = 500
DIM_STAT_AREA = 60
DIM_MARGIN = 30

KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SPACE = \
       "Up", "Down", "Left", "Right", "space"

HEADING_BY_KEY = {KEY_UP:90, KEY_DOWN:270, KEY_LEFT:180, KEY_RIGHT:0}

def create_turtle(x, y, color="red", border="black"):
    """
    Creates a new turtle object with the specified position, color, and border.
    
    Args:
        x (int): The x-coordinate of the turtle's initial position.
        y (int): The y-coordinate of the turtle's initial position.
        color (str, optional): The color of the turtle's body. Defaults to "red".
        border (str, optional): The color of the turtle's border. Defaults to "black".
    
    Returns:
        turtle.Turtle: The newly created turtle object.
    """
    t = turtle.Turtle("square")
    t.color(border, color)
    t.up()
    t.goto(x,y)
    return t

def configure_play_area():
    """
    Configures the play area for the snake game, 
    including the motion border, status border, 
    introduction text, and status text.
    The motion border and status border are based on square shape
    resized according to the specified dimensions.

    Returns:
        tuples: A tuple containing the introduction text turtle and 
        the status text turtle.
    """
    # motion border
    m = create_turtle(0,0,"","black")
    sz = DIM_PLAY_AREA//SZ_SQUARE
    m.shapesize(sz, sz, 3)
    m.goto(0,-DIM_STAT_AREA//2)  # shift down half the status

    # status border
    s = create_turtle(0,0,"","black")
    sz_w, sz_h = DIM_STAT_AREA//SZ_SQUARE, DIM_PLAY_AREA//SZ_SQUARE
    s.shapesize(sz_w, sz_h, 3)
    s.goto(0,DIM_PLAY_AREA//2)  # shift up half the motion

    # turtle to write introduction
    intro = create_turtle(0,100)
    intro.hideturtle()
    intro.write("Snake by Ziqi\n\n" + \
                "Click anywhere to start the game!\n\n", 
                font=FONT_INTRO, align= 'center')

    # turtle to write status
    status = create_turtle(0,0,"","black")
    status.hideturtle()
    status.goto(-200,s.ycor()-10)

    return intro, status

def configure_screen():
    """
    Configures the Turtle screen for the snake game,
    the screen width and height are calculated based 
    on the play area, status bar and margin.
    
    Returns:
        turtle.Screen: The configured Turtle screen.
    """
    s = turtle.Screen()
    s.tracer(0)    # disable auto screen refresh, 0=disable, 1=enable
    s.title("Snake by Ziqi")
    w = DIM_PLAY_AREA + DIM_MARGIN*2
    h = DIM_PLAY_AREA + DIM_MARGIN*2 + DIM_STAT_AREA
    s.setup(w, h)
    s.mode("standard")
    return s

def update_time():
    """
    Continuously updates and displays the elapsed game time.

    Computes the time elapsed since game start, updates the global time, and schedules itself
    to update every second until the game ends.

    Effects:
    - Adjusts global game time and refreshes the game status display.
    """
    global g_time
    if not game_over(): 
        g_time = int(time.time() - g_start_time)
        g_screen.ontimer(update_time, 1000)
        update_status()

def update_status():
    """
    Refreshes the game's status display with current metrics.

    Updates display for contacts, time, and motion status.
    Adjusts for game state (paused/active).

    Effects:
    - Clears and updates the status on the screen.
    """
    if g_paused == 1 or g_key_pressed is None:
        g_motion = 'Paused'
    else:
        g_motion = g_key_pressed
    g_status.clear()
    status = f'Contacts-{g_contacts}    Time-{g_time}    Motion-{g_motion} '
    g_status.write(status, font=FONT_STATUS)
    g_screen.update()

def on_arrow_key_pressed(key):
    """
    Handles the user's arrow key press event and 
    updates the global `g_key_pressed` variable with the pressed key. 
    It then calls the `update_status()` function to update 
    the status display on the screen.
    
    Args:
        key (str): The key that was pressed, one of 'Up', 'Down', 'Left', or 'Right'.
    """
    global g_key_pressed, g_paused
    g_key_pressed = key
    g_paused = 0
    update_status()
    
    
def move_snake():
    """
    Controls and updates the movement of the snake on a regular interval.

    This function is executed repeatedly by the Turtle screen's `ontimer` method. It advances the snake
    if a key has been pressed, otherwise, it reschedules itself. Movement includes creating a new body
    segment, advancing the head, and potentially removing the oldest body segment if the snake exceeds
    its allowed size. It also handles pausing, blocking by obstacles, and food consumption.

    Effects:
    - Moves the snake based on the current direction key.
    - Manages the addition and removal of body segments.
    - Consumes food and adjusts speed as necessary.
    - Updates the screen and reschedules itself for the next move.
    """
    global g_bodyInfo
    if game_over() or g_paused or g_key_pressed is None:
        g_screen.ontimer(move_snake, TIMER_SNAKE)
        return
    block()
    if g_block == 1:
        g_screen.ontimer(move_snake, TIMER_SNAKE)
        return
    
    # Clone the head as a body segment and perform movement
    g_snake.color(*COLOR_BODY)
    stamp_id = g_snake.stamp()
    g_snake.color(COLOR_HEAD)
    g_snake.setheading(HEADING_BY_KEY[g_key_pressed])
    g_snake.forward(SZ_SQUARE)
    g_bodyInfo.append((g_snake.xcor(), g_snake.ycor(), stamp_id))
    
    # Remove the last segment if snake is longer than its size
    if len(g_snake.stampItems) > g_snake_sz:
        g_snake.clearstamps(1)
        g_bodyInfo.pop(0)
        
    consume_food()
    adjust_snake_speed(g_snake_sz) #snake speed need to be refreshed
    
    g_screen.update()
    g_screen.ontimer(move_snake, TIMER_SNAKE)
    

def consume_food():
    """
    Checks and processes the consumption of food by the snake.

    Evaluates if the snake's head is close enough to any food item to consume it. 
    If so, increases the snake's size, clears the food item from the display, 
    and updates the relevant lists. Also adjusts the snake's speed based on the new size. 
    Only one food item can be consumedat a time.

    Global Variables:
    - g_snake_sz: The current size of the snake, which is incremented upon consuming food.
    - g_food: A list of food items, each represented as a tuple with the turtle object 
              and its attributes.
    - g_foodPos: A list of coordinates for all food items.

    Effects:
    - Removes consumed food from the display and updates the snake's size and speed.
    """
    # Check for food consumption
    global g_snake_sz, g_food, g_foodPos
    head_x, head_y = int(g_snake.xcor()), int(g_snake.ycor())
    head_y -= 10
    for idx, (food_turtle, x, y, val) in enumerate(g_food):
        
        if abs(head_x - x) < 1.5 and abs(head_y - y) < 1.5:
            #print('True')
            g_snake_sz += val  # Increase the snake size
            food_turtle.clear()  # Remove the number from the screen
            g_foodPos.remove((x, y))  # Remove the food position from the list
            g_food.pop(idx)  # Remove the food from the list
            adjust_snake_speed(g_snake_sz) # Slow the snake
            break  # Only consume one food item per move
        
       
def adjust_snake_speed(target_size):
    """
    Adjusts the speed of the snake based on its size relative to a target size.

    Parameters:
    - target_size (int): The desired length of the snake in terms of the number of stamp items.

    Global Variables:
    - TIMER_SNAKE: Controls the time interval (in milliseconds) between the snake's movements.

    Effects:
    - Modifies TIMER_SNAKE based on the snake's current size relative to the target size.
    """
    global TIMER_SNAKE
    if len(g_snake.stampItems) < target_size:
        # When the snake needs to grow, slow down
        TIMER_SNAKE = 450
    else:
        # When reaches the target length, returns to normal speed
        TIMER_SNAKE = 250


def food():
    """
    Generates and positions new food items on the game board.

    Creates five food items represented by turtles. Places them at random locations 
    not currently occupied. Each food item is marked with a number for identification.

    Global Variables:
    - g_food: List of food items, each stored as a tuple with the turtle object and its position.
    - g_foodPos: List of coordinates marking the positions of all food items to prevent overlap.

    Effects:
    - Five new food items are added to the game board, displayed and tracked in global lists.
    """
    global g_food, g_foodPos
    i = 0
    while i < 5:
        # Create a turtle to represent food but do not show it yet
        new_food = turtle.Turtle(visible=False)
        new_food.penup()

        # Find a location for the food that is not occupied
        x, y = 0, 0
        while (x, y) in g_foodPos or (x == 0 and y == 0):
            x = random.randrange(-240, 240, 20)
            y = random.randrange(-280, 220, 20)

        # Set the position of the food and write the number on the screen
        new_food.setpos(x, y)
        new_food.write(i + 1, align="center", font=("Arial", 18, "bold"))
        
        # Store the food turtle and its position
        g_food.append((new_food, x, y, i + 1))
        g_foodPos.append((x, y))
        
        i += 1
        g_screen.update()


def move_food():
    """
    Randomly moves a subset of food items on the game board.

    Selects a random number of food items and attempts to move each selected item to a new, 
    unoccupied position within game bounds. Updates the positions and redraws the items. 
    If a move isn't possible, the food item remains in its original location. 
    Schedules the next food movement after a random delay.

    Global Variables:
    - g_food: List of tuples representing each food item and its properties.
    - g_foodPos: List of current positions of all food items.

    Effects:
    - Updates the positions of randomly selected food items.
    - Reschedules the movement of food items at a random interval 
      between 5000 and 10000 milliseconds.
    """
    global g_food, g_foodPos
    if (not game_over()) and len(g_food) != 0:
        
        # Decide how many food items to move
        num_items_to_move = random.randint(1, len(g_food))  # Pick a random number to move
        
        # Randomly choose which food items to move
        food_items_to_move = random.sample(g_food, num_items_to_move)
        
        # New lists to hold updated food and positions
        new_g_food = []
        new_g_foodPos = []
        
        for food_turtle, x, y, val in g_food:
            if (food_turtle, x, y, val) in food_items_to_move:
                # Randomly choose a direction to move the food
                dx, dy = random.choice([(40, 0), (-40, 0), (0, 40), (0, -40)])
                new_x, new_y = x + dx, y + dy
                # Check if the new position is within bounds and not already occupied
                if (-240 < new_x < 240) and (-280 < new_y < 220) \
                    and (new_x, new_y) not in g_foodPos:
                    food_turtle.clear()
                    food_turtle.goto(new_x, new_y)
                    food_turtle.write(val, align="center", font=("Arial", 18, "bold"))
                    new_g_food.append((food_turtle, new_x, new_y, val))
                    new_g_foodPos.append((new_x, new_y))
                else:
                    new_g_food.append((food_turtle, x, y, val))
                    new_g_foodPos.append((x, y))
            else:
                new_g_food.append((food_turtle, x, y, val))
                new_g_foodPos.append((x, y))
        
        # Update the global food list and positions with the new values
        g_food = new_g_food
        g_foodPos = new_g_foodPos
        
        # Set the timer to move the food again
        g_screen.ontimer(move_food, random.randint(5000, 8000))
  
        
def adjust_snake_speed(target_size):
    """
    Adjusts the speed of the snake based on its size relative to a target size.

    Parameters:
    - target_size (int): The desired length of the snake in terms of the number of stamp items.

    Global Variables:
    - TIMER_SNAKE: Controls the time interval (in milliseconds) between the snake's movements.

    Effects:
    - Modifies TIMER_SNAKE based on the snake's current size relative to the target size.
    """
    global TIMER_SNAKE
    if len(g_snake.stampItems) < target_size:
        # When the snake needs to grow, slow down
        TIMER_SNAKE = 450
    else:
        # When reaches the target length, returns to normal speed
        TIMER_SNAKE = 250


def create_monster(existing_monsters):
    """
    This function generates a new monster at a random location that does not overlap with 
    existing monsters, is sufficiently distant from the snake's initial position, and 
    avoids the intro area.

    Parameters:
    - existing_monsters (list): A list of current monsters to ensure new ones do not overlap.

    Returns:
    - Turtle: A Turtle object representing the newly created monster at a valid position.
    """
    min_distance = 150
    while True:
        x = random.randrange(-230, 230, 20)
        y = random.randrange(-260, 200, 20)
        # Calculate distance from the snake's initial position
        distance = ((x - 0) ** 2 + (y - 0) ** 2) ** 0.5
        # Check if it overlaps with an existing monster
        overlapping = False
        for monster in existing_monsters:
            if monster.distance(x, y) <= 0:  
                overlapping = True
                break
        # Not overlapping other monsters; distant from snake; not overlapping the intro.
        if (not overlapping) and (distance >= min_distance) \
            and (not (-120 <= x <= 120)): 
            monster = create_turtle(x, y, COLOR_MONSTER, "black")
            return monster
        
def deploy_monsters():
    """
    Creates and deploys four monster instances.

    Continuously generates and appends monsters to a list until there are four monsters,
    ensuring each monster is uniquely positioned by passing the current list to the creation function.

    Returns:
    - list: A list containing four initialized monster objects.
    """
    monsters = []
    while len(monsters) < 4:
        monster = create_monster(monsters)
        monsters.append(monster)
    return monsters

def move_monsters():
    """
    Moves all monsters towards the snake and schedules their variable speed movements.

    Each monster is directed in 45-degree steps towards the snake and moves forward.
    Their movements are rescheduled with random delays to vary their speed.

    Global Variables:
    - g_monsters: List of monsters.
    - SZ_SQUARE: Movement step size.
    - TIMER_SNAKE: Base timing interval, adjusted randomly for movement scheduling.
    """
    for monster in g_monsters:
        if not game_over():
            angle = monster.towards(g_snake)
            qtr = angle//45 
            heading = qtr * 45 if qtr % 2 == 0 else (qtr+1) * 45
            monster.setheading(heading)
            monster.forward(SZ_SQUARE)
            g_screen.ontimer(lambda m=monster: move_monster(m), TIMER_SNAKE + random.randint(-50,1200))
            
def move_monster(monster):
    """
    Logic of a single monster moving.
    
    Calculates the monster's heading, moves it forward, 
    and checks for contact with the snake based on it's movement. 
    If the game continues, schedules the next movement with a variable delay.

    Global Variables:
    - SZ_SQUARE: Movement distance per step.
    - TIMER_SNAKE: Base timing for movements, adjusted randomly.

    Effects:
    - Moves one monster.
    """
    if not game_over():
        angle = monster.towards(g_snake)
        qtr = angle//45 
        heading = qtr * 45 if qtr % 2 == 0 else (qtr+1) * 45
        monster.setheading(heading)
        monster.forward(SZ_SQUARE)
        
        check_contact_with_snake(monster)
                
        g_screen.update()
        g_screen.ontimer(lambda: move_monster(monster), TIMER_SNAKE + random.randint(-50,1200))
        
def check_contact_with_snake(monster):
    """
    Checks if a monster is in contact with the snake's body.

    Iterates through the snake's body positions to determine if any part
    is within a critical distance from the monster, indicating contact.

    Global Variables:
    - g_contacts: Counter for the number of times a monster contacts the snake.
    - g_bodyInfo: List of tuples representing the snake's body part positions.
    - SZ_SQUARE: Critical distance defining contact.

    Effects:
    - Increments `g_contacts` if contact is detected and stops further checks.
    """
    global g_contacts
    for pos in g_bodyInfo:
        if monster.distance(pos[0], pos[1]) <= SZ_SQUARE:
            g_contacts += 1
            break
            
def block():   
    """
    Determines if the snake's next move is blocked by boundaries or obstacles.

    Simulates the snake's movement based on the last key pressed to check if the new position
    is within game limits. Sets the block state accordingly.

    Global Variables:
    - g_block: Indicates block status (1 if blocked, 0 if not).
    - g_snake: The snake object.
    - g_key_pressed: Key determining movement direction.

    Effects:
    - Updates `g_block` to reflect whether movement is blocked.
    """
    global g_block
    clone = g_snake.clone()
    clone.hideturtle()
    clone.setheading(HEADING_BY_KEY[g_key_pressed])
    clone.forward(20)
    x = clone.pos()[0]
    y = clone.pos()[1]
    # if the snake is blocked by the body or the barrier, don't move
    if (abs(x)>250 or abs(y + 30)>250): 
        g_block = 1
    else: g_block = 0
    

def toggle_pause():
    """
    Toggles the paused state of the game.

    This function changes the game's paused state between active and paused. 
    When the game state is toggled, it updates the status display to reflect the current state. 

    Global Variables:
    - g_paused: A boolean that represents whether the game is currently paused or active.

    Effects:
    - The game pauses or resumes based on the previous state.
    - The game status display is updated to show the current mode (paused or active).
    """
    global g_paused
    g_paused = not g_paused
    update_status()
    
    
def cb_start_game(x, y):
    """
    Starts the game by setting up the initial game state and event handlers.
    
    This function is triggered by a mouse click on the game screen. It prepares the game for
    playing by initializing game elements and setting up necessary event handlers.
    
    Parameters:
    - x (int): The x-coordinate of the click. Not used in the function.
    - y (int): The y-coordinate of the click. Not used in the function.
    
    Steps:
    1. Disables further screen clicks to prevent restarting the game inadvertently.
    2. Clears the introductory text from the game screen.
    3. Spawns the initial food item.
    4. Records the start time of the game for timing features.
    5. Updates the game timer display at the start.
    6. Sets up keyboard bindings for snake movement based on arrow keys.
    7. Starts the automatic movement of the snake and monsters.
    8. Allows the game to be paused and resumed with the 'space' bar.
    9. Initiates periodic movement of food items across the game area.
    10. Listens to the keyboard inputs.
    
    The function uses several global variables to manage the game state, including game status flags
    and references to game elements like the snake, monsters, and the game screen.
    """
    global g_intro, g_status, g_start_time
    g_screen.onscreenclick(None)  # Disable screen click to start the game
    g_intro.clear()  # Clear introduction text
    food()
    g_start_time = time.time()
    update_time()
    # Set up key bindings for snake control
    for key in (KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_LEFT):
        g_screen.onkey(partial(on_arrow_key_pressed, key), key)

    # Start the snake and monster movement timers
    move_snake()
    move_monsters()
    
    g_screen.onkey(toggle_pause, "space")

    # Start food item movement
    g_screen.ontimer(move_food, 5000)
    
    g_screen.listen()
    
    
def display_game_over(message):
    """
    Displays a game over message at the center of the play area.
    
    Args:
        message (str): The message to display ("Winner !!" or "Game Over !!").
    """
    # Clear any existing game status messages
    # Position the game over message in the center of the play area
    game_over_display = create_turtle(0, 0, "", "red")
    game_over_display.hideturtle()
    game_over_display.goto(0, 0)
    game_over_display.write(message, align="center", font=("Arial", 22, "bold"))
    

def game_over():
    """
    Evaluates the conditions that determine the end of the game.
    
    Win condition:
    - All food has been consumed: 
      If there are no food items left in the game (g_food is empty),
      the function will display a winning message 
      and terminate the game by returning True.
    
    Lose condition:
    - The snake is caught by a monster: 
      If any monster is within a SZ_SQUARE of snake's current position, 
      the function will display a game over message 
      and terminate the game by returning True.

    Returns:
    - bool: True if the game should end (either win or lose), 
            False otherwise, allowing the game to continue.
    """
    # Check for win condition: all food consumed
    if len(g_snake.stampItems) == 20:
        display_game_over("Winner !!")
        return True

    # Check for lose condition: snake contacts a monster
    for monster in g_monsters:
        if monster.distance(g_snake.xcor(), g_snake.ycor()) < SZ_SQUARE:
            display_game_over("Game Over !!")
            return True

    return False
    
def game():
    """
    Initializes and starts the main game environment and loop.

    This function sets up the game screen, play area, and game entities like
    monsters and the snake. It also configures the mouse-click event handler
    to start the game and enters the main loop to keep the game responsive.

    Steps:
    1. Configures the screen and play area.
    2. Deploys monsters and creates the snake.
    3. Sets up a callback for starting the game via mouse click.
    4. Enters the main game loop to process events and updates.

    Global Variables:
    - g_screen, g_intro, g_status: Used for display and UI.
    - g_monsters, g_snake: Game entities.
    - g_start_time: Marks the start of the game for timing events.
    """
    global g_screen, g_intro, g_status, g_monsters, g_snake, g_start_time
    g_screen = configure_screen()
    g_intro, g_status = configure_play_area()
    update_status() 

    g_snake = create_turtle(0,-10, COLOR_HEAD, "black")
    g_monsters = deploy_monsters()
    g_screen.onscreenclick(cb_start_game) # set up a mouse-click call back

    g_screen.update()
    g_screen.listen()
    g_screen.mainloop()

if __name__ == "__main__":
    """
    The main processing logic 
    for a Snake game using Python Turtle graphics.
    """
    game()
