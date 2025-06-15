"""
Player selection scene for Connect-N

The game Connect-N has exactly two scenes: one to select the players and
the other to play the game. This is the gameplay scene.

Author: Walker M. White (wmw2)
Date:   October 22, 2023
"""
from consts import *
from game2d import *
from exporter import *      # ORDER MATTERS!
from importer import *
from container import *
from piece import *
from button import *
from kivy.logger import Logger

import introcs
import random


def main_loop(game):
    """
    Executes the student game in a separate thread.
    
    Parameter game: The student game
    Precondition: game is a Game object
    """
    game.run()


def possessify(word):
    """
    Returns the possessive form of the word.
    
    Parameter word: The word to make possessive
    Precondition: word is a nonempty string
    """
    if not word or type(word) != str:
        return word
    if word[-1] in 'sS':
        return word+"'"
    return word+"'s"


class GameScene(object):
    """
    The gameplay controller class for the Connect-N application
    
    This is a subcontroller for ConnectN. As such, it shares a lot of the same
    structure.  In particular, it has an update and draw that are invoked by
    the main game.
    
    This class works using a producer-consumer pattern (covered in CS 4410). It
    waits on the student code to either (1) request a move or (2) communicate an
    AI chosen move. It then animates the game in response. To achieve this, the
    student code is executed in a separate thread.
    """
    # HIDDEN ATTRIBUTES
    # Attribute _width: The scene width
    # Invariant: _width is float > 0
    #
    # Attribute _height: The scene _height
    # Invariant: _height is float > 0
    #
    # Attribute _state: The current state of the game (taken from const.py)
    # Invariant: _state is one of STATE_WAITING, STATE_SELECT, STATE_DELAY,
    #            STATE_ANIMATE, STATE_COMPLETE, STATE_RESET
    #
    # Attribute _game: The instance of the student's game class
    # Invariant: _game is an instance of Game
    #
    # Attribute _board: The board view
    # Invariant: _board is an instance of Container
    #
    # Attribute _players: The players (at the time of game initialization)
    # Invariant: _players is a dict from color strings to Player objects
    #
    # Attribute _thread: The execution thread
    # Invariant: _thread is an instance of SafeThread
    #
    # Attribute _color: The color of the current player
    # Invariant: _color is a string representing a valid color
    #
    # Attribute _piece: The piece currently being animated
    # Invariant: _piece is a Piece object
    #
    # Attribute _label: The information text
    # Invariant: _label is a GLabel object
    #
    # Attribute _reset: The reset button
    # Invariant: _reset is a Button object
    
    def __init__(self,width,height,players):
        """
        Creates the gameplay scene
        
        This method launches the thread with the players code, using that thread
        to drive the animation.
        
        Parameter width: The scene width
        Precondition: width is a number (int or float) > 0
        
        Parameter height: The scene height
        Precondition: height is a number (int or float) > 0
        
        Parameter players: The list of players
        Precondition: players is a list of tuples of the form (color,type) where
        color is a color string and type is a int indicating if the player type
        (0=human,1=ai,2=better ai).
        """
        self._width  = width
        self._height = height
        
        # Need attribute at all times for cleanup
        self._thread = None
        
        # Make a display message
        self._label = None
        # Make a reset button
        self._reset = Button(text='Reset',font_size=RESET_SIZE)
        self._reset.right = self._width-RESET_OFFSET[0]
        self._reset.top = self._height-RESET_OFFSET[1]
        self._reset.on_press   = self._reset_press
        self._reset.on_release = self._reset_release
        
        # Create the student code and add some players
        self._game = a6game.Game(BOARD_COLS,BOARD_ROWS,BOARD_STREAK)
        players = self._makePlayers(players)
        for p in players:
            self._game.addPlayer(p)
        
        self._validateGame()
        
        # Initialize the board graphics
        self._board = Container(self._width,self._height-TILE_SIZE/2)
        
        # The current active piece
        self._color = None
        self._piece = None
        
        # Load the audio assets
        Piece.loadAudio()
        Container.loadAudio()
        
        # Put game in a thread and start up student code
        self._thread = SafeThread(target=main_loop, args=(self._game,))
        self._thread.silent = False
        self._thread.start()
        self._state = STATE_WAITING

    def update(self,inpt,dt):
        """
        It is the method that does most of the work. It is NOT in charge of animating
        anything. That is the purpose of the classes Container and Piece. But it does
        manage player input and determine the current state.
        
        This particular application supports five player states
        
        STATE_WAITING: This is the state when the application first opens. It is also
        the state when we are waiting to the student code to take a turn in the game.
        No input (other than closing the window) is recognized during this state.
        
        STATE_SELECT: This is the state when the human player wants to select a piece.
        It responds to mouse input to place the piece. This state persists until the
        player makes a valid move.
        
        STATE_DELAY: This is a state for when the AI is making a decision. We add a small
        delay so that the AI does not move too fast.
        
        STATE_ANIMATE: This is the state after a column is chosen (by either the human
        player or an AI). It animates the falling of the piece.
        
        STATE_COMPLETE: This is the state when the game is over, and either a player
        has won or the board is full.
        
        Parameter inpt: The player input
        Precondition: inpt is a GInput object
        
        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        # FIRST thing we do is check the rest button
        self._reset.update(inpt.touch)
        
        # Determine the state
        if self._state == STATE_WAITING:
            self._checkForPlayer()
        elif self._state == STATE_SELECT:
            self._getPlayerChoice(inpt)
        elif self._state == STATE_DELAY:
            self._waitOnChoice()
        elif self._state == STATE_ANIMATE:
            self._waitOnDrop()
        
        # Update any board animations
        self._board.update(dt)

    def draw(self,view):
        """
        Draws the game objects to the view.
        
        Every single thing you want to draw in this game is a GObject. To draw a
        GObject g, simply use the method g.draw(self.view). It is that easy!
        
        Parameter view: The window to draw to
        Precondition: view is a GView object
        """
        if not self._label is None:
            self._label.draw(view)
        self._reset.draw(view)
        
        self._board.draw(view)
        
        if not self._piece is None:
            self._piece.draw(view)


    def cleanup(self):
        """
        Performs any necessary clean-up before the application stops.
        
        This is an obscure function that is only necessary if the application has some
        active resource (like a thread) that needs to be shutdown.
        """
        if not self._thread is None and self._thread.is_alive():
            self._thread.silent = True
            self._thread.kill()
        buffer = SharedBuffer()
        buffer.invalidate()
        buffer.reset()

    def _makeLabel(self,text,size):
        """
        Creates a label for the given text and size.
        
        The label will be displayed in the top left corner of the window.
        
        Parameter text: The text to display
        Precondition: text is a string
        
        Parameter size: The font size of the text
        Precondition: size is an int > 0
        """
        label = GLabel(text=text,font_name=GAME_FONT,font_size=size)
        label.linecolor = '#000000'
        label.left = FONT_OFFSET[0]
        label.top  = self._height-FONT_OFFSET[1]
        return label

    def _checkForPlayer(self):
        """
        Checks the execution thread to identify the current player (if any)
        """
        if self._thread.is_alive():
            buffer = SharedBuffer()
            if buffer.isBlocked():
                tag,push,value = buffer.poll()
                p = self._getPlayer(tag)
                name = possessify(p.getName())
                self._label = self._makeLabel(name+" turn",FONT_SIZE)
                self._color = tag
                
                if push:
                    self._processAI(tag,value)
                else:
                    self._state = STATE_SELECT
        
        elif self._thread.crashed:
            # Thread is dead, stop the game
            raise SystemExit()
        
        elif not self._game.getWinner() is None:
            p = self._getPlayer(self._game.getWinner())
            name = p.getName()
            self._label = self._makeLabel('Winner: '+name,FONT_SIZE)
            self._state = STATE_COMPLETE
            self._findStreak()
        elif self._game.getBoard().isFullBoard():
            self._label = self._makeLabel('Game Over: Draw',FONT_SIZE)
            self._state = STATE_COMPLETE
        else:
            self._label = self._makeLabel('Game Over',FONT_SIZE)

    def _getPlayerChoice(self,inpt):
        """
        Respond to input to get a choice from a human player
        
        Parameter inpt: The player input
        Precondition: inpt is a GInput object
        """
        if inpt.touch:
            # Find the grid position
            (row,col) = self._board.worldToBoard(inpt.touch.x,inpt.touch.y)
            grid = self._board.getGridSize()

            # Validate column input
            if col < 0 or col >= BOARD_COLS:
                self._label = self._makeLabel("Invalid column. Please choose a column between 0 and " + str(BOARD_COLS - 1), FONT_SIZE)
                if not self._piece is None:
                    self._board.destroyPiece(self._piece)
                    self._piece = None
                return

            if self._piece is None:
                self._makePiece(self._color,col)
            self._piece.x = self._board.boardToWorld(row,col)[0]
        else:
            if not self._piece is None:
                # Figure out the column
                (row,col) = self._board.worldToBoard(self._piece.x,self._piece.y)

                # Validate column is not full
                if self._game.getBoard().isFullColumn(col):
                    self._label = self._makeLabel("Column " + str(col) + " is full. Please choose another column.", FONT_SIZE)
                    self._board.destroyPiece(self._piece)
                    self._piece = None
                else:
                    row = self._game.getBoard().findAvailableRow(col) # findAvailableRow now returns -1 if full
                    if row != -1: # This check is technically redundant due to isFullColumn check, but good for clarity
                        self._board.addPiece(self._piece,row)
                        self._state = STATE_ANIMATE
                    else:
                         # This case should not be reached if isFullColumn is correct, but as a fallback
                        self._label = self._makeLabel("Error finding available row in column " + str(col), FONT_SIZE)
                        self._board.destroyPiece(self._piece)
                        self._piece = None
    
    def _waitOnDrop(self):
        """
        Do nothing until the drop animation has completed.
        """
        if self._piece.isInPlace():
            (row,col) = self._board.worldToBoard(self._piece.x,self._piece.y)
            self._piece = None
            buffer = SharedBuffer()
            buffer.post((self._color,True,col))
            buffer.unblock()
            self._state = STATE_WAITING
    
    def _waitOnChoice(self):
        """
        Do a fake animation of the AI choosing
        """
        if self._piece.isInPlace():
            (row,col) = self._board.worldToBoard(self._piece.x,self._piece.y)
            row = int(self._game.getBoard().findAvailableRow(col))
            self._piece.setInPlace(False)
            self._board.addPiece(self._piece,row)
            self._state = STATE_ANIMATE
    
    def _makePiece(self,color,col):
        """
        Creates a piece ABOVE the board at the given column.
        
        The piece is read to drop but has not been dropped into the board.
        
        Parameter color: The piece color
        Precondition: color is a string representing a valid color
        
        Parameter col: The drop column
        Precondition: col is an int in 0..BOARD_COLS-1
        """
        self._piece = Piece(color=color)
        self._piece.scale = self._board.getScale()
        grid = self._board.getGridSize()
        self._piece.y = (BOARD_ROWS+1)*grid+grid/2
        self._piece.x = self._board.boardToWorld(0,col)[0]
    
    def _processAI(self,color,col):
        """
        Process the information sent by the AI
        
        This creates a piece, but jiggles it about as a fake-out before dropping it
        
        Parameter color: The piece color
        Precondition: color is a string representing a valid color
        
        Parameter col: The drop column
        Precondition: col is an int in 0..BOARD_COLS-1
        """
        state = self._game.getBoard()
        if state.isFullColumn(col):
            raise RuntimeError('AI player sent an invalid column: '+repr(col))
        self._color = color
        
        # Make a list of fakeouts
        fakes = random.randint(0,FAKE_OUTS)
        
        allcols = self._chooseFakes(fakes,col)
        
        self._makePiece(self._color,BOARD_COLS/2)
        self._board.choosePiece(self._piece,allcols)
        self._state = STATE_DELAY
    
    def _validateGame(self):
        """
        Validate that the student has set up the game correctly.
        
        If the game is no properly configured, this will raise a RuntimeError, shutting
        everything down.
        """
        state = self._game.getBoard()
        if state.getWidth() != BOARD_COLS:
            raise RuntimeError('Game board does not have %s columns (%s)' % (repr(BOARD_COLS),repr(state.getWidth())))
        if state.getHeight() != BOARD_ROWS:
            raise RuntimeError('Game board does not have %s rows (%s)' % (repr(BOARD_ROWS),repr(state.getHeight())))
        players = self._game.getPlayers()
        if players is None or len(players) == 0:
            raise RuntimeError('Game has no players')
        
        lookup = {}
        for p in players:
            lookup[p.getColor()] = p
        
        if len(lookup) != len(players):
            # Find the shared color
            for c in lookup:
                total = 0
                for p in players:
                    if p.getColor() == c:
                        total += 1
                if total > 1:
                    raise RuntimeError('Mulitple players have color '+repr(c))
        
        self._players = lookup
    
    def _getPlayer(self,color):
        """
        Return the player object for the given color
        
        Parameter color: The player color
        Precondition: color is a string representing a valid color
        """
        if not color in self._players:
            raise RuntimeError('The '+color+' player was not initialized properly')
        return self._players[color]
    
    def _chooseFakes(self,n,col):
        """
        Choose a list of fake column choices to simulate thinking.
        
        The last two elements of this list will always be col, so that it hovers over
        the correct choice before making it.
        
        Parameter n: The number of fake choices to make
        Precondition: n is an int >= 0
        
        Parameter col: The correct (and final) choice
        Precondition: col is an int in 0..BOARD_COLS-1
        """
        result = []
        for x in range(n):
            c = random.randint(0,BOARD_COLS-1)
            while self._game.getBoard().isFullColumn(c):
            #while self._game.getBoard().available(c) == -1:
                c = (c+1) % BOARD_COLS
            if c != col and not c in result:
                result.append(c)
                result.append(c)
        result.append(col)
        result.append(col)
        return result
    
    def _makePlayers(self,players):
        """
        Returns a list of player objects for a new game
        
        Parameter players: The list of players
        Precondition: players is a list of tuples of the form (color,type) where
        color is a color string and type is a int indicating if the player type
        (0=human,1=ai,2=better ai).
        """
        # Count the number of humans
        humans = 0
        for item in players:
            if item[1] == 0:
                humans += 1
        
        # Count the number of computers
        computs = 0
        for item in players:
            if item[1] in [1,2]:
                computs += 1
        
        # Now create some players
        result = []
        for item in players:
            if item[1] in [1,2]:
                if computs > 1:
                    name = item[0].capitalize()+' AI player'
                else:
                    name = 'AI player'
                if item[1] == 1:
                    p = a6player.AIPlayer(item[0],name)
                else:
                    p = a6player.BetterAIPlayer(item[0],name)
                result.append(p)
            else:
                if humans == len(players):
                    name = ''
                elif computs > 1:
                    name = item[0].capitalize()+' human player'
                else:
                    name = 'Human player'
                p = a6player.Player(item[0],name)
                result.append(p)
        return result
    
    def _findStreak(self):
        """
        Extracts the winning streak for animation
        """
        (r,c) = self._game.getBoard().getLastMove()
        streak = self._game.getBoard().findWins(r,c)
        self._board.markWin(streak)
    
    def _reset_press(self,obj,touch):
        """
        Registers that Reset has been pressed, but not released
        
        This will deactivate any active animations.
        """
        self._state = STATE_RESET
    
    def _reset_release(self,obj,touch):
        """
        Registers that Reset has been released
        
        This completely resets the game, including the creation of a new thread.
        """
        self.cleanup()
        
        # Recreate the game
        players = self._game.getPlayers()
        self._game = a6game.Game(BOARD_COLS,BOARD_ROWS,BOARD_STREAK)
        for p in players:
            self._game.addPlayer(p)
        
        self._validateGame()
        self._board = Container(self._width,self._height-TILE_SIZE/2)
        
        # The current active piece
        self._color = None
        self._piece = None
        
        # Put game in a thread and start up student code
        self._thread = SafeThread(target=main_loop, args=(self._game,))
        self._thread.silent = False
        self._thread.start()
        self._state = STATE_WAITING
