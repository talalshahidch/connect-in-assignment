"""
Constants for Connect-N

This module contains global constants for the game Connect-N. These constants need to be 
used in the model, the view, and the controller. As these are spread across multiple 
modules, we separate the constants into their own module. This allows all modules to 
access them.

Author: Walker M. White (wmw2)
Date:   September 27, 2023
"""
import introcs
import sys

### WINDOW CONSTANTS (all coordinates are in pixels) ###

# The initial width of the game display
GAME_WIDTH  = 824
# The initial height of the game display
GAME_HEIGHT = 720 #896
# The (default) size of the grid tiles
TILE_SIZE = 256

# The image file for the red piece
RED_PIECE  = 'red.png'
# The image file for the blue piece
BLUE_PIECE  = 'blue.png'
# The image file for a tintable white piece
WHITE_PIECE  = 'white.png'

# The maximum number of pixels to bounce
OVERAGE_AMOUNT = 20
# The height necessary for a full bounce
OVERAGE_THRESH = 4

# The max amount of fake-out choices for the AI
FAKE_OUTS = 2

# The length of time of a fade-out timed animation
FADE_TIME = 1
# The length of time of a hover timed animation
HOVER_TIME = 0.2


### BOARD TILES ###

BOARD_CENTER = 'center.png'
BOARD_LEFT   = 'edge1.png'
BOARD_BOTTOM = 'edge2.png'
BOARD_RIGHT  = 'edge3.png'
BOARD_TOP    = 'edge4.png'
BOARD_TOP_LEFT   = 'corner1.png'
BOARD_BOT_LEFT   = 'corner2.png'
BOARD_BOT_RIGHT  = 'corner3.png'
BOARD_TOP_RIGHT  = 'corner4.png'


### WIN EFFECTS ###
WIN_STAR_FILE   = 'sparkle.png'
WIN_STAR_COLOR  = 'yellow'
WIN_STAR_FRAMES = 5
WIN_STAR_SIZE = (2,3)
WIN_STAR_TIME = 2

### DISPLAY_FONT ###
# The current font choice
GAME_FONT = 'RobotoCondensed-Bold.ttf'
# The current font size
FONT_SIZE = 70
# The font offset, measured from the top left corner
FONT_OFFSET = (8,0)
# The UI font size
UI_SIZE = 22
# The reset button size
RESET_SIZE = 34
# The reset button offset
RESET_OFFSET = (8,24)


### GAME STATE ###

# state when the game is waiting
STATE_WAITING = 0
# state when a human player must select a move
STATE_SELECT  = 1
# state when the AI player must make a choice
STATE_DELAY   = 2
# state when a piece is dropping
STATE_ANIMATE  = 3
# state when the game has completed
STATE_COMPLETE = 4
# state when we are preparing a reset
STATE_RESET    = 5


### BOARD SIZE ###
# Number of rows in the board
BOARD_ROWS   = 6
# Number of columns in the board
BOARD_COLS   = 7
# Number of pieces needed to win
BOARD_STREAK = 4


### USE COMMAND LINE ARGUMENTS TO CHANGE DEFAULT BOARD SIZE
"""
sys.argv is a list of the command line arguments when you run python. These arguments are
everything after the word python. So if you start the game typing

    python connectn rows cols streak

The first two values determine the board size. The maximum for each is 20.  The last is
the number needed for a winning streak. It cannot be larger than the min of rows and
columns.
"""
try:
    value = int(sys.argv[1])
    if value > 0 and value <= 20:
        BOARD_ROWS = value
except:
    pass # Use original value

try:
    value = int(sys.argv[2])
    if value > 0 and value <= 20:
        BOARD_COLS = value
except:
    pass # Use original value

try:
    value = int(sys.argv[3])
    if value > 0 and value <= min(BOARD_ROWS,BOARD_COLS):
        BOARD_STREAK = value
    elif BOARD_STREAK > min(BOARD_ROWS,BOARD_COLS):
        BOARD_STREAK = min(BOARD_ROWS,BOARD_COLS)
except:
    if BOARD_STREAK >  min(BOARD_ROWS,BOARD_COLS):
        BOARD_STREAK = min(BOARD_ROWS,BOARD_COLS)
    # Else use original value
