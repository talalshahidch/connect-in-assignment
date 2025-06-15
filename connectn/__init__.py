"""
File defining the module functionality of the folder

When you import this folder, this file defines what you get. In this case, we are only
providing access to two functions

Author: Walker M. White (wmw2)
Date:   September 28, 2023
"""
import sys

# This fixes the singleton problem.
# But it requires exporter to be imported in app FIRST
if 'exporter' in sys.modules:
    # Don't import if already exists
    exporter = sys.modules['exporter']
    get_choice = exporter.get_choice
    set_choice = exporter.set_choice
else:
    from .exporter import get_choice, set_choice
