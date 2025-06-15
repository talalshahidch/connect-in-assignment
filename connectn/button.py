"""
A quick and dirty button class

We wanted to add some buttons to the Connect-N UI. That result is this class. This is not
a general purpose button class, but it is good enough for Connect-N.

Author: Walker M. White (wmw2)
Date:   October 22, 2023
"""
from game2d import *
from consts import *
from kivy.metrics import *
from kivy.graphics import *
from kivy.graphics.vertex_instructions import *
from kivy.graphics.instructions import *

class Button(GLabel):
    """
    An instance is a simple text button.
    
    The button is presented as a rounded rectangle with an offset line edge.  When 
    pressed, the edge disappears and the color is made darker.
    """
    
    # MUTABLE PROPERTIES    
    @property
    def pad_x(self):
        """
        The horizontal padding between the edge and the text.
        
        This padding is ignored if the button is sufficiently wide.
        
        **invariant**: Value must be an ``int`` or ``float`` > 0
        """
        return self._pad_x
    
    @pad_x.setter
    def pad_x(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        self._pad_x = value
        if self._defined:
            self._reset()
    
    @property
    def pad_y(self):
        """
        The vertical padding between the edge and the text.
        
        This padding is ignored if the button is sufficiently tall.
        
        **invariant**: Value must be an ``int`` or ``float`` > 0
        """
        return self._pad_y
    
    @pad_y.setter
    def pad_y(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        self._pad_y = value
        if self._defined:
            self._reset()
    
    @property
    def on_press(self):
        """
        A listener to call when the button is pressed.
        
        **invariant**: Value must be None or a callable with params (gobject,touch)
        """
        return self._on_press
    
    @on_press.setter
    def on_press(self,value):
        # No precondition enforcement
        self._on_press = value
    
    @property
    def on_release(self):
        """
        A listener to call when the button is released.
        
        **invariant**: Value must be None or a callable with params (gobject,touch)
        """
        return self._on_release
    
    @on_press.setter
    def on_release(self,value):
        # No precondition enforcement
        self._on_release = value
    
    
    # IMMUTABLE PROPERTIES
    @property
    def down(self):
        """
        Whether the button is currently pressed down.
        
        **invariant**: Value must be None or a callable with params (gobject,touch)
        """
        return self._down
    
    def __init__(self,**keywords):
        """
        Creates a new button object
        
        To use the constructor for this class, you should provide it with a list of 
        keyword arguments that initialize various attributes.  For example, to create a 
        button containing the word 'Hello', use the constructor call::
            
            Button(text='Hello')
        
        This class supports the all same keywords as :class:`GLabel`, as well as 
        additional attributes for the button properties (e.g. padding and listeners).
        
        :param keywords: dictionary of keyword arguments
        :type keywords:  keys are attribute names
        """
        self._down  = False
        self._press = None
        
        if 'on_press' in keywords:
            self._on_press = keywords['on_press']
            del keywords['on_press']
        else:
            self._on_press = None
        
        if 'on_release' in keywords:
            self._on_release = keywords['on_release']
            del keywords['on_release']
        else:
            self._on_release = None
            
        if 'pad_x' in keywords:
            self._pad_x = keywords['pad_x']
            del keywords['pad_x']
        else:
            self._pad_x = 5
        
        if 'pad_y' in keywords:
            self._pad_y = keywords['pad_y']
            del keywords['pad_y']
        else:
            self._pad_y = 5
        
        if not 'linewidth' in keywords:
            keywords['linewidth'] = 1.1
        
        if not 'linecolor' in keywords:
            keywords['linecolor'] = 'black'
        
        if not 'fillcolor' in keywords:
            keywords['fillcolor'] = '#EEEEEE'
        
        if not 'font_name' in keywords:
            keywords['font_name'] = GAME_FONT
        
        if not 'font_size' in keywords:
            keywords['font_size'] = UI_SIZE
        
        super().__init__(**keywords)
        if self._fillcolor is None: 
            self._downcolor = Color(0.75,0.75,0.75,1)
        else:
            vals = self._fillcolor.rgba[:]
            for p in range(3):
                vals[p] *= 0.75
            self._downcolor = Color(*vals)
    
    def notify_press(self,touch):
        """
        Notifies the any listeners of a press.
        
        This method does nothing if there is no listener for a press event.
        
        :param touch: the touch event for this press
        :type touch:  is a Point2 object
        """
        if not self._on_press is None:
            self._on_press(self,touch)
    
    def notify_release(self,touch):
        """
        Notifies the any listeners of a release.
        
        This method does nothing if there is no listener for areleasepress event.
        
        :param touch: the touch event for the initial press
        :type touch:  is a Point2 object
        """
        if not self._on_release is None:
            self._on_release(self,touch)
    
    def update(self,touch):
        """
        Updates this button with the current touch status.
        
        If the touch is not None, is inside the button, AND the button is not
        currently down, this will register as a press. If it is None and the
        button is currently down, it will register as a release.  Otherwise, 
        nothing will happen.
        
        :param touch: the touch event for this press
        :type touch:  is None or a Point2 object
        """
        if self._press is None and not touch is None:
            if self.contains(touch):
                self._press = touch
                self._down = True
                self.notify_press(touch)
                self._reset()
        elif not self._press is None and touch is None:
            self._down = False
            self.notify_release(self._press)
            self._press = None
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
        self.width  = max(self.width, self._label.width+2*self._pad_x)
        self.height = max(self.height,self._label.height+2*self._pad_y)
        self._radius = min(self.width,self.height)/6
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
            self._label.x = -self.width/2.0+self._pad_x
        elif self.halign == 'right':
            self._label.right = self.width/2.0+self._pad_x
        
        # Reset the label anchor.
        if self.valign == 'top':
            self._label.top = self.height/2.0+self._pad_y
        elif self.valign == 'bottom':
            self._label.bottom = -self.height/2.0+self._pad_y
        
        GObject._reset(self)
        x = -self.width/2.0
        y = -self.height/2.0
        
        if self.fillcolor:
            fill = RoundedRectangle(pos=(x,y), size=(self.width,self.height), 
                                    radius=[(self._radius, self._radius)]*4)
            if self._press:
                self._cache.add(self._downcolor)
            else:
                self._cache.add(self._fillcolor)
            self._cache.add(fill)
        
        self._cache.add(self._label.canvas)
        
        if not self._press and self._linewidth > 0:
            line = Line(rounded_rectangle=(x-2*self._linewidth,y-2*self._linewidth,
                                           self.width+4*self._linewidth,self.height+4*self._linewidth,
                                           self._radius),
                        joint='round',close=True,width=self.linewidth)
            self._cache.add(self._linecolor)
            self._cache.add(line)
        
        self._cache.add(PopMatrix())
