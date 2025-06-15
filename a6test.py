"""
The board class for the Connect-N game.

This module keeps track of the current status of the board.
"""
from a6consts import *

class Board:
    """
    A class representing a Connect-N game board.
    """
    def _init_(self, width, height, streak):
        assert type(width) == int and width > 0
        assert type(height) == int and height > 0
        assert type(streak) == int and 0 < streak <= min(width, height)
        self._width = width
        self._height = height
        self._streak = streak
        self._grid = [[NOBODY] * width for _ in range(height)]

    def getWidth(self):
        return self._width

    def getHeight(self):
        return self._height

    def getStreak(self):
        return self._streak

    def getCell(self, row, col):
        assert 0 <= row < self._height and 0 <= col < self._width
        return self._grid[row][col]

    def isFullBoard(self):
        return all(self._grid[0][col] != NOBODY for col in range(self._width))

    def isFullColumn(self, col):
        assert 0 <= col < self._width
        return self._grid[0][col] != NOBODY

    def getNextRow(self, col):
        assert 0 <= col < self._width and not self.isFullColumn(col)
        for row in range(self._height-1, -1, -1):
            if self._grid[row][col] == NOBODY:
                return row

    def place(self, color, col):
        assert type(color) == str and color != NOBODY
        assert 0 <= col < self._width and not self.isFullColumn(col)
        row = self.getNextRow(col)
        self._grid[row][col] = color

    def undoPlace(self, col):
        assert 0 <= col < self._width
        for row in range(self._height):
            if self._grid[row][col] != NOBODY:
                self._grid[row][col] = NOBODY
                return

    def _checkRun(self, color, r, c, dr, dc, streak):
        end_r = r + (streak - 1) * dr
        end_c = c + (streak - 1) * dc
        if not (0 <= end_r < self._height and 0 <= end_c < self._width):
            return None
        for i in range(streak):
            if self._grid[r + i * dr][c + i * dc] != color:
                return None
        return (r, c, end_r, end_c)

    def hasHorizontal(self, color, r, c, streak):
        return self._checkRun(color, r, c, 0, 1, streak)

    def hasVertical(self, color, r, c, streak):
        return self._checkRun(color, r, c, 1, 0, streak)

    def hasDiagonal1(self, color, r, c, streak):  # SW to NE
        return self._checkRun(color, r, c, -1, 1, streak)

    def hasDiagonal2(self, color, r, c, streak):  # NW to SE
        return self._checkRun(color, r, c, 1, 1, streak)

# Distance function used in AI evaluation
def dist(r1, c1, r2, c2):
    return abs(r1 - r2) + abs(c1 - c2)

def in_range(board, r, c):
    return 0 <= r < board.getHeight() and 0 <= c < board.getWidth()
