"""
Module representing the board view for Connect-N

This class is the view of the board, not the board's state.  The state is stored in
a separate model class created by the students.

Author: Walker M. White (wmw2)
Date:   September 27, 2023
"""
from consts import *
from game2d import *
from winstars import *
import traceback

class Container(object):
    """
    A class representing the visualization of a Connect-N board.
    
    This class primarily holds game2d objects for drawing and animation. It does not
    store the state of the game. It only keep information about the coordinate systems
    to simplify user input.
    """
    # HIDDEN ATTRIBUTES
    # Attribute _grid: The grids size in pixels
    # Invariant: _grid is a float > 0
    #
    # Attribute _scale: The scaling factor to fit the tiles on screen
    # Invariant: _scale is a float > 0
    #
    # Attribute _tiles: The tile objects representing the board frame
    # Invariant: _tiles is a list of GTile objects
    #
    # Attribute _pieces: The pieces currently stored in the board
    # Invariant: _pieces is a list of Piece objects
    #
    # Attribute _animators: The active animations for this board
    # Invariant: _animators is a list of coroutines
    
    # This method prevents a latency delay the first time we create a piece
    @classmethod
    def loadAudio(cls):
        """
        Loads the audio files associated with this class
        """
        cls._winsnd = Sound('win.wav')
    
    def getGridSize(self):
        """
        Returns the width and height of a grid position in pixels
        """
        return self._grid
    
    def getScale(self):
        """
        Returns the scaling factor of this container
        
        The container is scaled to fit in the window.  The value returned is that amount
        """
        return self._scale
    
    def __init__(self, width, height):
        """
        Initializes the container
        
        Parameter width: The width of the game window
        Precondition: width a float > 0
        
        Parameter height: The height of the game window
        Precondition: height a float > 0
        """
        
        # Construct a grid with room at the top for pieces to drop
        rows = BOARD_ROWS+2
        cols = BOARD_COLS
        
        # Compute the grid size
        gridw = width/cols
        gridh = height/rows
        grid = int(min(gridw,gridh))
        self._grid = grid-(grid % 2)
        
        self._scale = self._grid/TILE_SIZE
        
        # Compute the bounds
        left = width-(BOARD_COLS+1)*self._grid
        left /= 2
        self._bounds = (left,0,(BOARD_COLS+1)*self._grid,(BOARD_ROWS+1)*self._grid)
        self._stars = None
        
        self._initTiles()
        self.clear()
    
    def _initTiles(self):
        """
        Initializes the tiles for this board
        """
        self._tiles = []
        if (BOARD_ROWS > 1 and BOARD_COLS > 1):
            tile = GTile(source=BOARD_CENTER,
                         width=(BOARD_COLS-1)*TILE_SIZE,
                         height=(BOARD_ROWS-1)*TILE_SIZE)
            tile.scale = self._scale
            tile.left  = self._bounds[0]+self._grid
            tile.bottom= self._bounds[1]+self._grid
            self._tiles.append(tile)
        
        if (BOARD_ROWS > 1):
            tile = GTile(source=BOARD_LEFT,
                         width =TILE_SIZE,
                         height=(BOARD_ROWS-1)*TILE_SIZE)
            tile.scale = self._scale
            tile.left  = self._bounds[0]
            tile.bottom= self._bounds[1]+self._grid
            self._tiles.append(tile)

            tile = GTile(source=BOARD_RIGHT,
                         width =TILE_SIZE,
                         height=(BOARD_ROWS-1)*TILE_SIZE)
            tile.scale = self._scale
            tile.left  = self._bounds[0]+BOARD_COLS*self._grid
            tile.bottom= self._bounds[1]+self._grid
            self._tiles.append(tile)
        
        if (BOARD_COLS > 1):
            tile = GTile(source=BOARD_BOTTOM,
                         width =(BOARD_COLS-1)*TILE_SIZE,
                         height= TILE_SIZE)
            tile.scale = self._scale
            tile.left  = self._bounds[0]+self._grid
            tile.bottom= self._bounds[1]
            self._tiles.append(tile)
        
            tile = GTile(source=BOARD_TOP,
                         width =(BOARD_COLS-1)*TILE_SIZE,
                         height= TILE_SIZE)
            tile.scale = self._scale
            tile.left  = self._bounds[0]+self._grid
            tile.bottom= self._bounds[1]+BOARD_ROWS*self._grid
            self._tiles.append(tile)
        
        tile = GImage(source=BOARD_TOP_LEFT,width=TILE_SIZE,height=TILE_SIZE)
        tile.scale = self._scale
        tile.left  = self._bounds[0]
        tile.bottom = self._bounds[1]+BOARD_ROWS*self._grid
        self._tiles.append(tile)

        tile = GImage(source=BOARD_BOT_LEFT,width=TILE_SIZE,height=TILE_SIZE)
        tile.scale = self._scale
        tile.left  = self._bounds[0]
        tile.bottom = self._bounds[1]
        self._tiles.append(tile)

        tile = GImage(source=BOARD_BOT_RIGHT,width=TILE_SIZE,height=TILE_SIZE)
        tile.scale = self._scale
        tile.left  = self._bounds[0]+BOARD_COLS*self._grid
        tile.bottom = self._bounds[1]
        self._tiles.append(tile)

        tile = GImage(source=BOARD_TOP_RIGHT,width=TILE_SIZE,height=TILE_SIZE)
        tile.scale = self._scale
        tile.left  = self._bounds[0]+BOARD_COLS*self._grid
        tile.bottom = self._bounds[1]+BOARD_ROWS*self._grid
        self._tiles.append(tile)
    
    def update(self,dt):
        """
        Manages any active animations on this board.
        
        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        # Manage the animators
        pos = 0
        while pos < len(self._animators):
            try:
                self._animators[pos].send(dt)
                pos += 1
            except:
                #traceback.print_exc()
                del self._animators[pos]
        
        # Piece garbage collection
        pos = 0
        while pos < len(self._pieces):
            if self._pieces[pos].isDeleted():
                del self._pieces[pos]
            else:
                pos += 1
        
        if not self._stars is None:
            if not self._stars.update(dt):
                self._stars = None
    
    def worldToBoard(self,x,y):
        """
        Returns the grid position for the given pixel coordinates.
        
        The value returned is (row,col).
        """
        if x < self._bounds[0]+self._grid/2:
            col = 0
        elif x > self._bounds[0]+self._bounds[2]-self._grid/2:
            col = BOARD_COLS-1
        else:
            x -= self._bounds[0]+self._grid/2
            col = int(x//self._grid)
        
        if y < self._bounds[1]+self._grid/2:
            row = 0
        elif y > self._bounds[1]+self._bounds[3]-self._grid/2:
            row = BOARD_ROWS-1
        else:
            y -= self._bounds[1]+self._grid/2
            row = int(y//self._grid)
        
        return (row,col)
    
    def boardToWorld(self,row,col):
        """
        Returns the pixel coordinates of the given board position
        
        The value returned is the center of the given grid position in the format (x,y)
        """
        return (self._grid*(col+1)+self._bounds[0],self._grid*(row+1)+self._bounds[1])
    
    def addPiece(self,piece,row):
        """
        Adds a piece to the board dropping it in place
        """
        self._pieces.append(piece)
        
        animator = piece.dropAnimation(self._grid*(row+1))
        next(animator)
        self._animators.append(animator)

    def choosePiece(self,piece,allcols):
        """
        Waggles a piece back and forth, as if a choice was being made
        """
        # This does not add the piece to the board yet
        animator = piece.choiceAnimation(allcols,(self._bounds[0],self._grid),HOVER_TIME)
        next(animator)
        self._animators.append(animator)

    def destroyPiece(self,piece):
        """
        Disposes a piece that could not be added to the board
        """
        self._pieces.append(piece)
        
        animator = piece.failAnimation(FADE_TIME)
        next(animator)
        self._animators.append(animator)
    
    def markWin(self,streak):
        """
        Creates win stars at the given list of (r,c) values
        """
        # Expand to a list of positions
        positions = []
        r1 = streak[0]
        c1 = streak[1]
        r2 = streak[2]
        c2 = streak[3]
        
        while (r1 != r2 or c1 != c2):
            positions.append((r1,c1))
            if c1 != c2:
                c1 += 1
            if r1 < r2:
                r1 += 1
            elif r1 > r2:
                r1 -= 1
        positions.append((r2,c2))
        
        # Now convert to actual locations
        for x in range(len(positions)):
            (r,c) = positions[x]
            positions[x] = self.boardToWorld(r,c)
        
        self._stars = WinStars(positions,self._scale,WIN_STAR_TIME)
        self._winsnd.play()
    
    def draw(self,view):
        """
        Draws the contents of this container
        """
        for item in self._pieces:
            item.draw(view)
        
        for item in self._tiles:
            item.draw(view)
        
        if not self._stars is None:
            self._stars.draw(view)
    
    def clear(self):
        """
        Clears the board contents
        """
        self._pieces = []
        self._animators = []
