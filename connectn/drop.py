"""
A quick and dirty drop-down menu

We wanted to add a color selector the Connect-N UI. That lead to this class. This is not
a general purpose drop-down menu, but it is good enough for Connect-N.

Author: Walker M. White (wmw2)
Date:   October 22, 2023
"""
from game2d import *
from consts import *
from kivy.metrics import *
from kivy.graphics import *
from kivy.graphics.vertex_instructions import *
from kivy.graphics.instructions import *
import introcs
import math

def is_color(value):
    """
    Returns true if value is a color string
    
    :param value: the color string to test
    :type value:  ANY (value can be anything)(
    """
    if not type(value) == str:
        return False
    return introcs.is_tkcolor(value) or introcs.is_webcolor(value)

def makeKivyColor(value):
    """
    Returns a Kivy color object for the given color name
    
    :param value: the color string
    :type value:  is a string with a valid color name
    """
    assert is_color(value)
    if introcs.is_tkcolor(value):
        rgb = introcs.RGB.CreateName(value)
    else:
        rgb = introcs.RGB.CreateWebColor(value)
    return Color(*rgb.glColor())

class ColorDrop(GObject):
    """
    An instance is a simple drop-down menu for color selection.
    
    The menu starts off as a rectangle with the current color. When pressed, it displays
    all colors and allows the use to pick between them.  The color selected is the
    current on highlighted on release.
    """
    
    # MUTABLE PROPERTIES    
    @property
    def colors(self):
        """
        The list of colors in this drop down menu.
        
        **invariant**: Value must be a list or tuple of unique color strings
        """
        return self._colors
    
    @colors.setter
    def colors(self,value):
        assert type(value) in [list,tuple], '%s is not iterable' % repr(value)
        assert len(value) > 0, '%s is empty' % repr(value)
        for item in value:
            assert is_color(item), '%s is not a valid color' % repr(item)
            assert value.count(item) == 1, '%s is not unique' % repr(item)
        
        self._colors = value
        if self._defined:
            self._reset()
    
    @property
    def selected(self):
        """
        The selected color in this drop down
        
        **invariant**: Value must a color string in the drop down
        """
        return self._colors[self._choice]
    
    @selected.setter
    def selected(self,value):
        assert value in self._colors, '%s is not in the list of colors' % repr(value)
        self._choice = self._colors.index(value)
        if self._defined:
            self._reset()
    
    @property
    def linewidth(self):
        """
        The width of the exterior line of this drop down box.
        
        Setting this to 0 means that the drop down box has no border.
        
        **invariant**: Value must be an ``int`` or ``float`` >= 0.
        """
        return self._linewidth
    
    @linewidth.setter
    def linewidth(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        assert value >= 0, '%s is negative' % repr(value)
        self._linewidth = value
        if self._defined:
            self._reset()
            
    @property
    def on_change(self):
        """
        A listener to call when the selected color changes
        
        **invariant**: Value must be None or a callable with params (gobject,color)
        """
        return self._on_change
    
    @on_change.setter
    def on_change(self,value):
        # No precondition enforcement
        self._on_change = value
    
    def __init__(self,**keywords):
        """
        Creates a new drop down menu
        
        To use the constructor for this class, you should provide it with a list of 
        keyword arguments that initialize various attributes. The required attribute
        is `colors`, which lists the colors in this drop down. By default, the first
        color in this list is selected.  The other attributes are inherited from 
        :class:`GObject`.
        
        :param keywords: dictionary of keyword arguments
        :type keywords:  keys are attribute names
        """
        self._defined = False
        if 'colors' in keywords:
            self.colors = keywords['colors']
        else:
            raise ValueError("ColorDrop missing a 'colors' attribute")
        
        if 'selected' in keywords:
            self.selected = keywords['selected']
        else:
            self._choice = 0
        
        if 'linewidth' in keywords:
            self.linewidth = keywords['linewidth']
        else:
            self.linewidth = 1.1
        
        if 'on_change' in keywords:
            self._on_change = keywords['on_change']
        else:
            self._on_change = None
        
        super().__init__(**keywords)
        self._temp = None
        self._reset()
        self._defined = True
    
    def notify_change(self):
        """
        Notifies the any listeners of state change.
        
        This method does nothing if there is no listener for a change event.
        """
        if not self._on_change is None:
            self._on_change(self,self.selected)
    
    def update(self,touch):
        """
        Updates this button with the current touch status.
        
        If the touch is not None, is inside the button, AND the menu is not
        currently selected, this will register as a press. Once pressed all 
        colors will be shown. The highlight will reflect the current position
        of the mouse/touch. On a release, the highlighted color will become
        the new selection.
        
        :param touch: the touch event for this press
        :type touch:  is None or a Point2 object
        """
        if touch is None:
            if not self._temp is None:
                if self._temp != -1:
                    self._choice = self._temp
                    self.notify_change()
                self._temp = None
                self._reset()
        elif self._temp != -1:
            point = tuple(self.matrix.inverse()._transform(touch.x,touch.y))
            if self._temp is None:
                if abs(point[0]) < self.width/2.0 and abs(point[1]) < self.height/2.0:
                    self._temp = self._choice
                    self._reset()
                else:
                    self._temp = -1
            else:
                dist = math.floor(-point[1]/self.height+0.5)
                val = self._choice+dist
                val = min(max(val,0),len(self.colors)-1)
                self._temp = val
                self._reset()

    
    # HIDDEN METHODS
    def _reset(self):
        """
        Resets the drawing cache.
        """
        GObject._reset(self)
        x = -self.width/2.0
        y = -self.height/2.0
        
        if self._temp is None or self._temp == -1:
            fill = Rectangle(pos=(x,y), size=(self.width, self.height))
            self._cache.add(makeKivyColor(self.selected))
            self._cache.add(fill)
        
            if not self._linecolor is None and self.linewidth > 0:
                line = Line(rectangle=(x,y,self.width,self.height),joint='miter',
                            close=True,width=self.linewidth)
                self._cache.add(Color(0,0,0,1))
                self._cache.add(line)
        else:
            # Make a bunch of rectangles
            if self._choice == 0:
                top = y
            else:
                top = y+self._choice*self.height
            
            for c in range(len(self.colors)):
                dy = top-c*self.height
                fill = Rectangle(pos=(x,dy), size=(self.width, self.height))
                self._cache.add(makeKivyColor(self.colors[c]))
                self._cache.add(fill)
            
            y -= (self._temp-self._choice)*self.height
            if not self._linecolor is None and self.linewidth > 0:
                line = Line(rectangle=(x,y,self.width,self.height),joint='miter',
                            close=True,width=self.linewidth)
                self._cache.add(Color(0,0,0,1))
                self._cache.add(line)
        
        self._cache.add(PopMatrix())
