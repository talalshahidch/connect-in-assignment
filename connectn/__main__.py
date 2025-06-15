"""
The primary application script for Connect-N

This script defines the behavior when the folder is run as an application.

Usage: python connectn rows cols streak

Author: Walker M. White (wmw2)
Date:   September 26, 2023
"""
from consts import *
from app import *

# Application code
if __name__ == '__main__':
    ConnectN(width=GAME_WIDTH,height=GAME_HEIGHT).run()
