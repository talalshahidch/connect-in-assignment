'''
The models classes to represent a player.

This module has a base class (Player) as well as a subclass (AIPlayer). You will need
to implement both to play against the computer. But it is sufficient to implement the
first to have two humans play against each other.
'''
import introcs
import random
import connectn
from a6board import *
from a6consts import *


#### TASK 1 ####
class Player(object):
    """
    A class representing a human player.
    """
    def setName(self, value):
        assert isinstance(value, str)
        if value == '':
            self._name = self._color.capitalize() + ' player'
        else:
            self._name = value

    def getName(self):
        return self._name

    def getColor(self):
        return self._color

    def _init_(self, color, name=''):
        assert isinstance(color, str) and (introcs.is_tkcolor(color) or introcs.is_webcolor(color))
        assert isinstance(name, str)
        self._color = color
        self.setName(name)

    def chooseMove(self, board):
        assert type(board) == Board
        assert not board.isFullBoard()
        return connectn.get_choice(self._color)


#### TASK 5 ####
class AIPlayer(Player):
    """
    A class representing an acceptable AI player.
    """
    def _scoreRun(self, board, run):
        if run is None:
            return SCORE_BAD
        return dist(run[0], run[1], run[2], run[3])

    def _evaluate(self, board, r, c):
        color = self.getColor()
        streak = board.getStreak()
        best_score = SCORE_BAD

        for s in range(streak, 0, -1):
            run = board.hasHorizontal(color, r, c, s)
            if run is not None and s == streak:
                return SCORE_WIN
            best_score = max(best_score, self._scoreRun(board, run))

            run = board.hasVertical(color, r, c, s)
            if run is not None and s == streak:
                return SCORE_WIN
            best_score = max(best_score, self._scoreRun(board, run))

            run = board.hasDiagonal1(color, r, c, s)
            if run is not None and s == streak:
                return SCORE_WIN
            best_score = max(best_score, self._scoreRun(board, run))

            run = board.hasDiagonal2(color, r, c, s)
            if run is not None and s == streak:
                return SCORE_WIN
            best_score = max(best_score, self._scoreRun(board, run))

        return best_score if best_score > 0 else 1

    def _gatherMoves(self, board):
        result = {}
        for col in range(board.getWidth()):
            if not board.isFullColumn(col):
                result[col] = SCORE_BAD
        return result

    def _evaluateMoves(self, board, moves):
        color = self.getColor()
        for col in moves:
            row = board.getNextRow(col)
            board.place(color, col)
            moves[col] = self._evaluate(board, row, col)
            board.undoPlace(col)

    def _findBestMoves(self, board, moves):
        best = []
        max_score = max(moves.values())
        for key in moves:
            if moves[key] == max_score:
                best.append(key)
        return best

    def chooseMove(self, board):
        assert type(board) == Board
        assert not board.isFullBoard()
        moves = self._gatherMoves(board)
        self._evaluateMoves(board, moves)
        best_moves = self._findBestMoves(board, moves)
        return random.choice(best_moves)


#### EXTRA CREDIT ####
class BetterAIPlayer(AIPlayer):
    pass


#### HELPER FUNCTIONS ####
def is_valid_run(board, run):
    assert type(board) == Board
    if run is None:
        return True
    if type(run) != tuple:
        return False
    if len(run) != 4:
        return False
    r1, c1, r2, c2 = run
    if not all(isinstance(x, int) for x in run):
        return False
    return in_range(board, r1, c1) and in_range(board, r2, c2)

def is_valid_dict(board, moves):
    assert type(board) == Board
    if type(moves) != dict:
        return False
    for c in moves:
        if not isinstance(c, int) or c < 0 or c >= board.getWidth():
            return False
        if not isinstance(moves[c], int) or moves[c] < 0:
            return False
    return True