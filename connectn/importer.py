"""
Bridge module to interact with student code

We do NOT want students to write code in this folder (that is for Assignment 7). We want
this application to be a sealed black box.  To do that, this module takes the student
code that is outside of this folder, and imports it into this folder, without the student
knowing about it.

Author: Walker M. White (wmw2)
Date:   September 27, 2023
"""
import importlib.util
import sys,os
import traceback

# Get a reference to this module
root = sys.modules[__name__]
sys.path.append(os.getcwd())

def module_from_file(name, path):
    """
    Returns a module object from the file at the given path
    
    Path should be the name of a .py file. It can be a relative path or an absolute 
    path. If relative, it should be relative to the current working directory of Python.
    If the file does not exist or if name is not a valid identifier, this function 
    returns None.
    
    Code adapted from 
    
        https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
    
    Parameter name: The module name
    Precondition: name is a string
    
    Parameter path: The path to a .py file
    Precondition: name is a string
    """
    if not name.isidentifier():
        return None
    
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except:
        traceback.print_exc()
        return None

def import_from_file(name,path):
    """
    Imports the module at the given path with the given variable name
    
    Calling this function will create a global variable in this module with the given
    name.  If the module cannot be imported, this function does nothing.
    
    Parameter name: The module name
    Precondition: name is a string and a valid identifier
    
    Parameter path: The path to a .py file
    Precondition: name is a string
    """
    module =  module_from_file(name, path)
    if not module is None:
        setattr(root, name, module)
    else:
        raise RuntimeError('Failed to load '+repr(path))

# Import the modules
import_from_file("a6game","a6game.py")
import_from_file("a6board","a6board.py")
import_from_file("a6player","a6player.py")

# So precondition enforcement works properly
a6game.a6player = a6player
a6game.a6board  = a6board
a6player.Board  = a6board.Board
