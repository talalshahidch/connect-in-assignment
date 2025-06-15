"""
Player selection scene for Connect-N

The game Connect-N has exactly two scenes: one to select the players and the other to
play the game.  This is the player selection scene.

Author: Walker M. White (wmw2)
Date:   September 27, 2023
"""

from consts import *
from game2d import *
from button import * 
from radio import *
from drop import *

# Constant for spacing UI elements
VERT_SPACE = 4


class PlayerScene(object):
    """
    A player selection screen for Connect-N
    """
    # This class is mainly a collection of UI widgets that we will not list
    # These widgets are fairly advanced but kludgy. Please do not use them in A7
    
    def getPlayers(self):
        """
        Returns a list of Player objects
        
        This method is called once the user decides to start the game. The players
        are returned as a list of tuples in the form (color,type) where color is 
        a color string and type is an int indicating the player type (0=human,1=ai,
        2=better ai).
        """
        result = []
        type1 = 0
        for pos in range(len(self._group1)):
            if self._group1[pos].state:
                type1 = pos
        type2 = 0
        for pos in range(len(self._group2)):
            if self._group2[pos].state:
                type2 = pos
        
        result.append((self._color1.selected,type1))
        result.append((self._color2.selected,type2))
        return result
    
    def isReady(self):
        """
        Returns True if the user is ready to play
        """
        return self._ready
    
    def __init__(self,width,height):
        """
        Initializes all of the UI elements for this scene
        
        Parameter width: The scene width
        Precondition: width is a number (int or float) > 0
        
        Parameter height: The scene height
        Precondition: height is a number (int or float) > 0
        """
        self._width  = width
        self._height = height
        
        self._title = GLabel(text='Connect N',font_name='Roboto-BlackItalic.ttf',font_size=FONT_SIZE)
        self._title.linecolor = '#000000'
        self._title.x = width/2
        self._title.y = 13*self._height/16
        
        self._label1 = GLabel(text='Player 1',font_name=GAME_FONT,font_size=2*UI_SIZE)
        self._label1.linecolor = '#000000'
        
        self._group1 = []
        self._group1.append(Radio(text='Human player'))
        self._group1[0].state = True
        self._group1[0].on_toggle = self.toggle_player
        
        self._group1.append(Radio(text='AI player'))
        self._group1[1].on_toggle = self.toggle_player
        
        self._group1.append(Radio(text='Better AI player'))
        self._group1[2].on_toggle = self.toggle_player
        
        colors = ['red','blue','green','orange','magenta','cyan','brown']
        self._color1 = ColorDrop(width=120,height=32,colors=colors)
        self._color1.on_change = self.change_color
        
        self._label2 = GLabel(text='Player 2',font_name=GAME_FONT,font_size=2*UI_SIZE)
        self._label2.linecolor = '#000000'
        self._arranged = False
        
        self._group2 = []
        self._group2.append(Radio(text='Human player'))
        self._group2[0].state = True
        self._group2[0].on_toggle = self.toggle_player
        
        self._group2.append(Radio(text='AI player'))
        self._group2[1].on_toggle = self.toggle_player
        
        self._group2.append(Radio(text='Better AI player'))
        self._group2[2].on_toggle = self.toggle_player
        
        self._color2 = ColorDrop(width=120,height=32,colors=colors)
        self._color2.selected = 'blue'
        self._color2.on_change = self.change_color
        
        self._start = Button(text='Start Game',font_size=2*UI_SIZE)
        self._start.on_release = self.release_button
        
        self._ready = False
    
    def update(self,touch):
        """
        Updates all of the UI elements in the scene
        
        This method sychronizes all of the UI elements so that we always have a
        consistent player state (e.g. no repeated colors) when done.
        
        Parameter touch: the current touch event
        Precondition touch: touch is None or a Point2 object
        """
        self._layout()
        for item in self._group1:
            item.update(touch)
        for item in self._group2:
            item.update(touch)
        self._color1.update(touch)
        self._color2.update(touch)
        self._start.update(touch)
    
    def draw(self,view):
        """
        Draws all of the UI elements on the screen.
        
        The color drop-downs are drawn last to make sure they are always on top.
        
        Parameter view: The window to draw to
        Precondition: view is a GView object
        """
        self._title.draw(view)
        
        self._label1.draw(view)
        for item in self._group1:
            item.draw(view)
        
        self._label2.draw(view)
        for item in self._group2:
            item.draw(view)

        self._start.draw(view)
        self._color1.draw(view)
        self._color2.draw(view)
    
    def toggle_player(self,obj,state):
        """
        Toggles the state of a player (AI or Human)
        
        This method works as a button group, ensuring that only one option is set
        at a time. When one option is selected, it unselects the other.
        
        Parameter obj: The UI object that was changed
        Precondition: obj is a Radio object
        
        Parameter state: The button state of obj
        Precondition: state is a bool
        """
        # Don't allow a not state
        if not state:
            obj.state = True
        elif obj in self._group1:
            for item in self._group1:
                if not item is obj:
                    item.state = False
        elif obj in self._group2:
            for item in self._group2:
                if not item is obj:
                    item.state = False
    
    def change_color(self,obj,color):
        """
        Changes the color of a player
        
        This method ensures that no two players have the same color. If we change
        the colors to match, the second player is adjusted to a new color.
        
        Parameter obj: The UI object that was changed
        Precondition: obj is a ColorDrop object
        
        Parameter color: The selected color
        Precondition: color is a color string
        """
        if obj is self._color1:
            alt = self._color2
        elif obj is self._color2:
            alt = self._color1
        else:
            return
        
        if alt.selected == color:
            # Find first unselected color
            for item in alt.colors:
                if item != color:
                    alt.selected = item
                    return
    
    def release_button(self,obj,touch):
        """
        Registers the release of the start button
        
        Parameter obj: The UI object that was changed
        Precondition: obj is a Button object
        
        Parameter touch: The initial location of the button press
        Precondition: touch is a Point2 object
        """
        self._ready = True
    
    def _layout(self):
        """
        Performs a delayed layout.
        
        This is necessary because have to wait for the text to render before we can
        start aligning anything.
        """
        if self._arranged:
            return
        
        self._label1.x = 5*self._width/16
        self._label1.top = self._title.bottom-15*VERT_SPACE
        self._label2.x = 11*self._width/16
        self._label2.top = self._title.bottom-15*VERT_SPACE
        
        self._group1[0].left =  self._width/4
        self._group1[0].top  = self._label1.bottom-2*VERT_SPACE
        self._group1[1].left = self._group1[0].left
        self._group1[1].top  = self._group1[0].bottom-VERT_SPACE
        self._group1[2].left = self._group1[1].left
        self._group1[2].top  = self._group1[1].bottom-VERT_SPACE
 
        self._color1.left = self._group1[-1].left
        self._color1.top = self._group1[-1].bottom-3*VERT_SPACE

        self._group2[0].left =  5*self._width/8
        self._group2[0].top  = self._label2.bottom-2*VERT_SPACE
        self._group2[1].left = self._group2[0].left
        self._group2[1].top  = self._group2[0].bottom-VERT_SPACE
        self._group2[2].left = self._group2[1].left
        self._group2[2].top  = self._group2[1].bottom-VERT_SPACE
 
        self._color2.left = self._group2[-1].left
        self._color2.top = self._group2[-1].bottom-3*VERT_SPACE

        self._start.x = self._width/2
        self._start.top = self._color2.bottom-20*VERT_SPACE
        self._arranged = True