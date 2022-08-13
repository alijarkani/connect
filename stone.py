

class Stone(object):
    def __init__(self, owner, pos):
        """Initialize a stone when user play a stone"""
        self._owner = owner
        self._pos = pos

    @property
    def owner(self):
        return self._owner

    @property
    def pos(self):
        return self._pos


