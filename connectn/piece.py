"""
Module representing a single piece on the board

Most of the work is done by GImage, so the only reason we need this class is for the cool
animation features.

Author: Walker M. White (wmw2)
Date:   September 27, 2023
"""
from consts import *
from game2d import *
import introcs
import traceback



def easeOutExpo(x):
    """
    Exponential ease out an interpolation parameter.
    
    Code taken from easings.net
    
    Parameter x: The interpolation parameter
    Precondition: x a float 0..1
    """
    if x >= 1:
        return 1
    elif x <= 0:
        return 0
    return 1 - (2 ** (-10*x))


class Piece(GImage):
    """
    A class to represent a colored game piece.
    
    The purpose of this class is to manage its own animation via coroutines
    """
    # HIDDEN ATTRIBUTES
    # Attribute _delete: Whether the piece should be deleted
    # Invariant: _delete is a bool
    #
    # Attribute _inplace: Whether the piece has snapped in-place
    # Invariant: _inplace is a bool
    #
    # Attribute _tiles: The tile objects representing the board frame
    # Invariant: _tiles is a list of GTile objects
    #
    # Attribute _clack: The sound effect for a valid move
    # Invariant: _clack is a Sound object
    #
    # Attribute _poof: The sound effect for an invalid move
    # Invariant: _poof is a Sound object
    
    # This method prevents a latency delay the first time we create a piece
    @classmethod
    def loadAudio(cls):
        """
        Loads the audio files associated with this class
        """
        cls._clack = Sound('clack.wav')
        cls._poof  = Sound('poof.wav')
    
    def isDeleted(self):
        """
        Returns whether this piece should be deleted.
        """
        return self._delete
    
    def isInPlace(self):
        """
        Returns whether this piece has snapped in-place.
        """
        return self._inplace
    
    def setInPlace(self,value):
        """
        Sets whether this piece has snapped in-place.
        
        Parameter value: The in-place value
        Precondition: value is a bool
        """
        assert type(value) == bool
        self._inplace = value
    
    def __init__(self,**kw):
        """
        Initializes a piece.
        
        This initializer uses the standard keyword objects for GImage, but adds another
        one for 'color'.  That indicates the color of the piece, not the fill color of
        the whole image.
        
        Parameter kw: The keyword arguments
        Precondition: kw is a dict
        """
        # Intercept the custom keyword arguments
        if 'color' in kw:
            source = WHITE_PIECE
            if kw['color'] == 'red':
                kw['fillcolor'] = '#9F2923'
            elif kw['color'] == 'blue':
                kw['fillcolor'] = '#6600cc'
            else:
                kw['fillcolor'] = kw['color']
            del kw['color']
            kw['source'] = source
        else:
            kw['source'] = RED_PIECE    # Red is default
        
        kw['width']  = TILE_SIZE
        kw['height'] = TILE_SIZE
        super().__init__(**kw)
        self._delete  = False
        self._inplace = False
    
    
    def dropAnimation(self,y):
        """
        Coroutine to smoothly animate a piece drop
        
        Parameter y: The number of pixels to drop
        Precondition: y is an int or float
        """
        # Acceleration is adjusted by the scale
        accel = TILE_SIZE*self.scale[0]
        speed = 0
        
        dy  = self.y - y
        limit = OVERAGE_AMOUNT*self.scale[0]
        over  = limit*dy/(TILE_SIZE*self.scale[0]*OVERAGE_THRESH)
        over  = min(over,limit)
        
        orig = self.y
        curr = 0
        while (curr < dy+over):
            dt = (yield)
            speed += accel*dt
            curr  += speed
            self.y = orig - curr
        
        self._clack.play()
        
        # Incorporate the overshoot into a nice little bounce
        if (self.y < y):
            dy = y-self.y
            dy = min(dy,limit)
            self.y = y-dy
            
            orig = self.y
            curr = 0
            speed = 0
            while (curr < dy):
                dt = (yield)
                speed += accel*dt
                curr  += speed
                self.y = orig + curr
        
        self.y = y
        self._inplace = True
    
    def failAnimation(self,sec):
        """
        Couroutine to fade out after so many seconds.
        
        Parameter sec: The number of seconds to fade out
        Precondition: sec is a float >= 0
        """
        curr = 0
        step = 1/sec
        alpha = 1

        tint = self.fillcolor[:]
        if tint is None:
            tint = [1.0,1.0,1.0,1.0]
        
        self._poof.play()
        while (curr < sec):
            dt = (yield)
            curr += dt
            value = easeOutExpo(curr*step)
            alpha = 1-value
            tint[3] = alpha
            self.fillcolor = tint
        
        self._delete = True
    
    def choiceAnimation(self,options,bounds,sec):
        """
        Couroutine to make it look like the AI is thinking.
        
        This coroutine will switch back-and-forth between several options. If an option
        is repeated, the animation will just hover in place.
        
        Parameter options: The columns to "try out"
        Precondition: options is a list of ints in range 0..BOARD_COLS-1
        
        Parameter bounds: The horizontal bounds of the board (left edge, grid size)
        Precondition: bounds is a two element tuple of floats
        
        Parameter sec: The number of seconds for each choice in options
        Precondition: sec is a float >= 0
        """
        part = len(options)-1
        step = 1/sec
        
        for pos in range(part):
            curr = 0
            while (curr < sec):
                dt = (yield)
                curr += dt
                param = min(1.0,curr/sec)
                
                interp = param*options[pos+1]+(1-param)*options[pos]
                interp = round(interp)
                
                self.x = bounds[0]+bounds[1]*(interp+1)
        
        self.x = bounds[0]+bounds[1]*(options[-1]+1)
        self._inplace = True
