

class Stone(object):
    def __init__(self, owner, pos):
        """
        After each player action, a stone will be placed on the board.
        Owner is Player instance and refers to the player who made the action.
        pos is Tuple[int, int] and refers to position of stone on the board,
        e.g. (0,0) refers to top left and (0,N) refers to top right and etc
        """
        self._owner = owner
        self._pos = pos

    @property
    def owner(self):
        return self._owner

    @property
    def pos(self):
        return self._pos


