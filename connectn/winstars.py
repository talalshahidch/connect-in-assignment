"""
Module to animate star effects on a winning streak.

This module creates and animates a sequence of stars as a timed coroutine. We are unable
to use the normal GSprite class because Kivy apparently premultiplies alpha when it loads 
an image file, but does NOT use a premultiplied blending formula.  As a result, alpha 
values other than 0 or 255 produce artifacts.  The class in this module solves that
problem.

Author: Walker M. White (wmw2)
Date:   October 22, 2023
"""

from game2d import *
from consts import *
from kivy.graphics import *
from kivy.graphics.instructions import *
from kivy.uix.image import Image
import traceback
import random
import math


def easeOutSine(x):
    """
    Sine ease out an interpolation parameter.
    
    Code taken from easings.net
    
    Parameter x: The interpolation parameter
    Precondition: x a float 0..1
    """
    return math.sin((x * math.pi) / 2)


def load_alpha_texture(name):
    """
    Loads a greyscale Image and builds an alpha mask texture for it
        
    This function will crash if name is not a valid file.
    
    :param name: The file name
    :type name:  ``str``
    """
    assert GameApp.is_image(name), '%s is not an image file' % repr(name)
    if name in GameApp.TEXTURE_CACHE:
        return GameApp.TEXTURE_CACHE[name]
    
    try:
        from kivy.core.image import Image
        image = Image(name)
        texture = image.texture
        data = list(texture.pixels)
        for x in range(0,len(data),4):
            alpha = data[x]
            if alpha == 0:
                data[x:x+3] = (0,0,0)
            else:
                data[x:x+3] = (255,255,255)
            data[x+3] = alpha
        texture.blit_buffer(bytes(data), colorfmt='rgba', bufferfmt='ubyte')
        GameApp.TEXTURE_CACHE[name] = texture
    except:
        texture = None
    
    return texture


class GAlphaSprite(GSprite):
    """
    A class representing a sprite defined from luminance map.
    
    For some reason, Kivy does not properly manage premultiplied alpha. So if we want
    subtle alpha effects, we need to make our own texture. This file loads a greyscale
    file and uses to create a proper tintable mask.
    """
    
    def _reset(self):
        """
        Resets the drawing cache.
        """
        # Texture must load FIRST
        texture = load_alpha_texture(self.source)
        if texture:
            width  = texture.width/self._format[1]
            height = texture.height/self._format[0]
            
            ty = 0
            for row in range(self._format[0]):
                tx = 0
                for col in range(self._format[1]):
                    self._images[row*self._format[1]+col] = texture.get_region(int(tx),texture.height-int(ty)-int(height),int(width),int(height))
                    tx += width
                ty += height
            if not self._set_width:
                self.width = width
            if not self._set_height:
                self.height = height
        else:
            print('Failed to load',repr(self.source))
        
        # THEN we can reset
        GObject._reset(self)
        x = -self.width/2.0
        y = -self.height/2.0
        
        self._texture = self._images[self._frame]
        self._bounds = Rectangle(pos=(x,y), size=(self.width, self.height),texture=self._texture)
        if not self._fillcolor is None:
            self._cache.add(self._fillcolor)
        else:
            self._cache.add(Color(1,1,1))
        self._cache.add(self._bounds)
        
        if not self._linecolor is None and self.linewidth > 0:
            line = Line(rectangle=(x,y,self.width,self.height),joint='miter',close=True,width=self.linewidth)
            self._cache.add(self._linecolor)
            self._cache.add(line)
        
        self._cache.add(PopMatrix())


class WinStars(object):
    """
    Displays an animates a sequence of win stars.
    
    The stars are scaled to TILE_SIZE, and the positions are relative to the coordinate
    system of the board container.
    """
    # HIDDEN ATTRIBUTES
    # Attribute _sprites: The individual alpha sprites to animate
    # Invariant: _sprites is list of GAlphaSprite objects
    #
    # Attribute _corouts: The coroutines to animate the sprites
    # Invariant: _corouts is a list of coroutines
    #
    # Attribute _secs: The number of seconds to animate these stars
    # Invariant: _secs is a float >= 0
    
    # Time (in seconds) for a single rotation
    ROTATE_TIME = 1
    
    def __init__(self,positions,scale,secs):
        """
        Creates a sequence of win stars and animates them for secs seconds.
        
        The positions are relative to the container coordinate frame.
        
        Parameter positions: The list of star positions
        Precondition: positions is a list of two-element number tuples
        
        Parameter secs: The number of seconds to animate
        Precondition: secs is a float >= 0
        """
        self._secs = secs
        self._sprites = []
        self._corouts = []
        for item in positions:
            sprite = GAlphaSprite(source=WIN_STAR_FILE,fillcolor=WIN_STAR_COLOR,format=WIN_STAR_SIZE)
            sprite.width  = TILE_SIZE
            sprite.height = TILE_SIZE
            sprite.frame = 1
            sprite.x = item[0]
            sprite.y = item[1]
            sprite.scale = scale
            self._sprites.append(sprite)
            
            animator = self.animate(sprite)
            next(animator)
            self._corouts.append(animator)
    
    def update(self,dt):
        """
        Returns True if the update was successful.
        
        This method will animate the stars for dt seconds.  If the animation is complete,
        this function will return False.
        
        Parameter dt: The number of seconds to animate
        Precondition: dt is a float >= 0
        """
        pos = 0
        while pos < len(self._corouts):
            try:
                self._corouts[pos].send(dt)
                pos += 1
            except:
                #traceback.print_exc()
                del self._corouts[pos]
        
        return len(self._corouts) > 0
    
    def draw(self,view):
        """
        Draws all of the stars to the screen.
        
        Parameter view: The window to draw to
        Precondition: view is a GView object
        """
        for sprite in self._sprites:
            sprite.draw(view)
        
    def animate(self,sprite):
        """
        Couroutine to animate a sprite.
        
        Animation both spins the star and makes it go through the frames in order.
        
        Parameter sprite: The sprite to animate
        Precondition: sprite is GAlphaSprite object
        """
        step = 1/self.ROTATE_TIME
        last = WIN_STAR_FRAMES-1
        
        curr = 0
        segm = 0
        sprite.angle = 0
        sprite.frame = last
        while (curr < self._secs):
            if (segm > self.ROTATE_TIME):
                segm -= self.ROTATE_TIME
            dt = (yield)
            curr += dt
            segm += dt
            angle = (360*(segm*step)) % 360
            frame = min(last,int((last+1)*easeOutSine(step*segm)))-1
            if frame < 0:
                frame = last
            sprite.angle = angle
            sprite.frame = frame
        
        sprite.angle = 0
        sprite.frame = last