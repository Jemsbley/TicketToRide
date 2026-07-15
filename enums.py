from enum import IntEnum, auto


class Card(IntEnum):
    """ Defines the set of all possible card colors """
    RED = auto()
    ORANGE = auto()
    YELLOW = auto()
    GREEN = auto()
    BLUE = auto()
    PURPLE = auto()
    BLACK = auto()
    WHITE = auto()
    WILD = auto()
    # Gray paths for trains will contain None as their color


class PlayerColor(IntEnum):
    """ Defines the set of all possible player colors """
    GREEN = auto()
    BLUE = auto()
    YELLOW = auto()
    BLACK = auto()
    RED = auto()


class DrawType(IntEnum):
    """ Defines the set of all possible draw types """
    DECK = auto()
    REVEALED = auto()


DRAW_TICKETS = auto()