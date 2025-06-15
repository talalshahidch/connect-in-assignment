"""
Primary module for Connect-N

This module contains the main controller class for the Connect-N application. If you
are student looking at this folder, know that this uses some very advanced Python to
interact with your code. It should not be studied as an example for Assignment 7.

Author: Walker M. White (wmw2)
Date:   October 22, 2023
"""
from consts import *
from gamescene import *
from playerscene import *

class ConnectN(GameApp):
    """
    The primary controller class for the Connect-N application
    
    This class extends GameApp and implements the various methods necessary for
    processing the player inputs and starting/running a game.
    
        Method start begins the application.
    
        Method update either changes the state or updates the Level object
    
        Method draw displays the Level object and any other elements on screen
    
    This class works leverages a scene-based architecture. The game is split into
    two scenes (player selection and gameplay). The scene classes do all the work.
    
    Attribute view: The game view, used in drawing (see examples from class)
    Invariant: view is an instance of GView and is inherited from GameApp
    
    Attribute input: The user input, used to control the ship and change state
    Invariant: input is an instance of GInput and is inherited from GameApp
    """
    # HIDDEN ATTRIBUTES
    # Attribute _playerscene: The player selection scene
    # Invariant: _playerscene is an instance of PlayerScene
    #
    # Attribute _gamescene: The gameplay scene
    # Invariant: _gamescene is an instance of GameScene

    def start(self):
        """
        Initializes the application.
        
        This method is distinct from the built-in initializer __init__. This method is
        called once the game is running. It is used to initialize any game specific
        attributes.
        """
        # These do all of the work
        self._gamescene = None
        self._playerscene = PlayerScene(self.width,self.height)

    def update(self,dt):
        """
        This method simply switches between the two scenes. The scenes do all the work.
        
        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        # Let the game scenes do all the work
        if not self._playerscene is None:
            self._playerscene.update(self.input.touch)
            if self._playerscene.isReady():
                self._gamescene = GameScene(self.width,self.height,self._playerscene.getPlayers())
                self._playerscene = None
        
        if not self._gamescene is None:
            self._gamescene.update(self.input,dt)
    
    def draw(self):
        """
        Draws the game objects to the view.
        
        Every single thing you want to draw in this game is a GObject. To draw a
        GObject g, simply use the method g.draw(self.view). It is that easy!
        """
        if not self._playerscene is None:
            self._playerscene.draw(self.view)
        
        if not self._gamescene is None:
            self._gamescene.draw(self.view)

    def cleanup(self):
        """
        Performs any necessary clean-up before the application stops.
        
        This is an obscure function that is only necessary if the application has some
        active resource (like a thread) that needs to be shutdown.
        """
        if not self._gamescene is None:
            self._gamescene.cleanup()
