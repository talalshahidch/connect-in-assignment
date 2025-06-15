"""
The gameboard for the Connect-N game.

This module keeps the board state of the game. This game supports R rows, C columns, and
a requirement of N in a line to win.  Traditionally, all of these values are fixed to:

    R == 6
    C == 7
    N == 4

Our version of the game allows variations on some or all of these parameters.

# YOUR NAME(S) AND NETID(S) HERE
# DATE COMPLETED HERE
"""
import introcs
from a6consts import *


#### TASK 2 ####
class Board:
    def _init_(self, rows=6, cols=7, streak=4):
        self._width = cols
        self._height = rows
        self._streak = streak
        self._board = [[NOBODY for _ in range(cols)] for _ in range(rows)]
        self._moves = []

    def getWidth(self):
        return self._width

    def getHeight(self):
        return self._height

    def getStreak(self):
        return self._streak

    def clear(self):
        self._board = [[NOBODY for _ in range(self._width)] for _ in range(self._height)]
        self._moves = []

    def getColor(self, r, c):
        return self._board[r][c]

    def getMoveCount(self):
        return len(self._moves)

    def getLastMove(self):
        return self._moves[-1] if self._moves else None

    def findAvailableRow(self, col):
        for r in range(self._height):
            if self._board[r][col] == NOBODY:
                return r
        return self._height

    def isFullColumn(self, col):
        return self._board[self._height - 1][col] != NOBODY

    def isFullBoard(self):
        for r in range(self._height):
            for c in range(self._width):
                if self._board[r][c] == NOBODY:
                    return False
        return True

    def place(self, column, color):
        row = self.findAvailableRow(column)
        if row == self._height:
            return -1
        self._board[row][column] = color
        self._moves.append((row, column))
        return row

    def undoPlace(self):
        if self._moves:
            row, col = self._moves.pop()
            self._board[row][col] = NOBODY

    def _str_(self):
        pad = max(len(cell) for row in self._board for cell in row)
        result = '['
        for row in range(self._height - 1, -1, -1):
            if row < self._height - 1:
                result += ' '
            result += '['
            for col in range(self._width):
                result += repr(self._board[row][col].ljust(pad)) + ','
            result = result[:-1] + '],\n'
        result = result[:-2] + ']'
        return result

    def findVertical(self, r, c, leng):
        color = self._board[r][c]
        r2 = r
        while r2 >= 0 and self._board[r2][c] == color:
            r2 -= 1
        r2 += 1
        if dist(self, r, c, r2, c) >= leng:
            return (r, c, r2, c)
        return None

    def findAcross(self, r, c, leng):
        color = self._board[r][c]
        c1 = c
        while c1 >= 0 and self._board[r][c1] == color:
            c1 -= 1
        c1 += 1
        c2 = c
        while c2 < self._width and self._board[r][c2] == color:
            c2 += 1
        c2 -= 1
        if dist(self, r, c1, r, c2) >= leng:
            return (r, c1, r, c2)
        return None

    def findSWNE(self, r, c, leng):
        color = self._board[r][c]
        r1, c1 = r, c
        while in_range(self, r1 - 1, c1 - 1) and self._board[r1 - 1][c1 - 1] == color:
            r1 -= 1
            c1 -= 1
        r2, c2 = r, c
        while in_range(self, r2 + 1, c2 + 1) and self._board[r2 + 1][c2 + 1] == color:
            r2 += 1
            c2 += 1
        if dist(self, r1, c1, r2, c2) >= leng:
            return (r1, c1, r2, c2)
        return None

    def findNWSE(self, r, c, leng):
        color = self._board[r][c]
        r1, c1 = r, c
        while in_range(self, r1 + 1, c1 - 1) and self._board[r1 + 1][c1 - 1] == color:
            r1 += 1
            c1 -= 1
        r2, c2 = r, c
        while in_range(self, r2 - 1, c2 + 1) and self._board[r2 - 1][c2 + 1] == color:
            r2 -= 1
            c2 += 1
        if dist(self, r1, c1, r2, c2) >= leng:
            return (r1, c1, r2, c2)
        return None

    def findWins(self, r, c):
        streak = self.getStreak()
        for check in [self.findVertical, self.findAcross, self.findSWNE, self.findNWSE]:
            result = check(r, c, streak)
            if result:
                return result
        return None
