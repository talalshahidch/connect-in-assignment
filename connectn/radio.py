"""
A quick and dirty radio button class

We wanted to add some radio buttons to the Connect-N UI. The result is this class. This 
is not a general purpose radio button class, but it is good enough for Connect-N.

Author: Walker M. White (wmw2)
Date:   October 22, 2023
"""
from game2d import *
from consts import *
from kivy.metrics import *
from kivy.graphics import *
from kivy.graphics.vertex_instructions import *
from kivy.graphics.instructions import *
import numpy as np

class Radio(GLabel):
    """
    An instance is a simple radio button.
    
    A radio button is a simply a label with a filled/hollow circle to the left of 
    it. Our properties define the size and position of this circle.  The position
    of the radio button is the position of the label (which is not ideal, but it works).
    This means that the true left edge of a radio button is left, plus the padding, plus
    twice the radius (the diameter).
    """
    
    # MUTABLE PROPERTIES
    @property
    def state(self):
        """
        The current radio button state.
        
        If the state is active (selected), this returns True.  Otherwise, it 
        returns False.
        
        **invariant**: Value must be a bool
        """
        return self._state
    
    @state.setter
    def state(self,value):
        assert type(value) == bool, '%s is not a bool' % repr(value)
        self._state = value
        if self._defined:
            self._reset()
    
    @property
    def padding(self):
        """
        The horizontal padding between the circle and the text.
        
        **invariant**: Value must be an ``int`` or ``float`` > 0
        """
        return self._padding
    
    @padding.setter
    def padding(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        self._padding = value
        if self._defined:
            self._reset()
    
    @property
    def radius(self):
        """
        The radius of the radio button.
        
        **invariant**: Value must be an ``int`` or ``float`` > 0
        """
        return self._radius
    
    @radius.setter
    def radius(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        self._radius = value
        if self._defined:
            self._reset()
    
    @property
    def on_toggle(self):
        """
        A listener to call when the radio button changes state.
        
        Listeners are only called when state changes via the update method. They do
        not fire if the property is changed. 
        
        **invariant**: Value must be None or a callable with params (gobject,state)
        """
        return self._on_toggle
    
    @on_toggle.setter
    def on_toggle(self,value):
        # No precondition enforcement
        self._on_toggle = value
    
    def __init__(self,**keywords):
        """
        Creates a new button object
        
        To use the constructor for this class, you should provide it with a list of 
        keyword arguments that initialize various attributes.  For example, to create a 
        button containing the word 'Hello', use the constructor call::
            
            Radio(text='Hello')
        
        This class supports the all same keywords as :class:`GLabel`, as well as 
        additional attributes for the button properties (e.g. padding and listeners).
        
        :param keywords: dictionary of keyword arguments
        :type keywords:  keys are attribute names
        """
        self._state = False
        self._press = None
        
        if 'on_toggle' in keywords:
            self._on_toggle = keywords['on_toggle']
        else:
            self._on_toggle = None
        
        if 'padding' in keywords:
            self._padding = keywords['padding']
            del keywords['padding']
        else:
            self._padding = 0.5*UI_SIZE
        
        if 'radius' in keywords:
            self._radius = keywords['radius']
            del keywords['radius']
        else:
            self._radius = 0.35*UI_SIZE
        
        if not 'linecolor' in keywords:
            keywords['linecolor'] = 'black'
        
        
        if not 'font_name' in keywords:
            keywords['font_name'] = GAME_FONT
        
        if not 'font_size' in keywords:
            keywords['font_size'] = UI_SIZE
        
        super().__init__(**keywords)
        self._circle = None
    
    def notify_toggle(self):
        """
        Notifies the any listeners of a change in state.
        
        This method does nothing if there is no listener for a toggle event.
        """
        if not self._on_toggle is None:
            self._on_toggle(self,self._state)
    
    def update(self,touch):
        """
        Updates this radio with the current touch status.
        
        This will toggle the radio button if the press is inside the circle 
        radius. It requires a PRESS, which means that touch was previously
        None, but is now not None.
        
        :param touch: the touch event for this press
        :type touch:  is None or a Point2 object
        """
        if not self._press is None and not touch is None:
            return
        elif not self._press is None and touch is None:
            self._press = None
            return
        elif touch is None:
            return
        
        self._press = touch
        point = tuple(self.matrix.inverse()._transform(touch.x,touch.y))
        x = -self.width/2.0-self._padding-self._radius
        y = self._label.center_y
        
        toggle = abs(point[0]-x) < self._radius and abs(point[1]-y) < self._radius
        if toggle:
            self._state = not self._state
            self.notify_toggle()
            self._reset()
    
    # HIDDEN METHODS
    def _reset(self):
        """
        Resets the drawing cache.
        """
        # Set up the label at the center.
        self._label.size = self._label.texture_size
        self._label.center = (0,0)
        if self.linecolor:
            self._label.color = self.linecolor
        
        # Resize the outside if necessary
        self._defined = False
        self.width  = max(self.width, self._label.width)
        self.height = max(self.height,self._label.height)
        self._defined = True
        
        # Reset the absolute anchor
        if self._hanchor == 'left':
            self._trans.x = self._ha+self.width/2.0
        elif self._hanchor == 'right':
            self._trans.x = self._ha-self.width/2.0
        
        # Reset the absolute anchor
        if self._vanchor == 'top':
            self._trans.y = self._hv-self.height/2.0
        elif self._vanchor == 'bottom':
            self._trans.y = self._hv+self.height/2.0
        
        # Reset the label anchor.
        if self.halign == 'left':
            self._label.x = -self.width/2.0
        elif self.halign == 'right':
            self._label.right = self.width/2.0
        
        # Reset the label anchor.
        if self.valign == 'top':
            self._label.top = self.height/2.0
        elif self.valign == 'bottom':
            self._label.bottom = -self.height/2.0
        
        GObject._reset(self)
        x = -self.width/2.0
        y = -self.height/2.0
        
        if self.fillcolor:
            fill = Rectangle(pos=(x,y), size=(self.width,self.height))
            self._cache.add(self._fillcolor)
            self._cache.add(fill)
        
        self._cache.add(self._label.canvas)
        
        if self._linewidth > 0:
            line = Line(rectangle=(x,y,self.width,self.height),joint='miter',close=True,width=self.linewidth)
            self._cache.add(self._linecolor)
            self._cache.add(line)
        
        x -= self._padding+2*self._radius
        y = self._label.center_y-self._radius-2
        d = 2*self._radius
        if self._state:
            circle = Ellipse(pos=(x,y),size=(d,d))
        else:
            circle = Line(ellipse=(x,y,d,d), close=True,width=1.1)
        self._cache.add(Color(0,0,0,1))
        self._cache.add(circle)
       
        self._cache.add(PopMatrix())
        