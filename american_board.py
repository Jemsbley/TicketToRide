from dataclasses import dataclass
from enum import IntEnum, auto
import enums as e

class City(IntEnum):
    """ Defines the set of cities in the american board of the game """
    ATLANTA = auto()
    BOSTON = auto()
    CALGARY = auto()
    CHARLESTON = auto()
    CHICAGO = auto()
    DALLAS = auto()
    DENVER = auto()
    DULUTH = auto()
    EL_PASO = auto()
    HELENA = auto()
    HOUSTON = auto()
    KANSAS_CITY = auto()
    LAS_VEGAS = auto()
    LITTLE_ROCK = auto()
    LOS_ANGELES = auto()
    MIAMI = auto()
    MONTREAL = auto()
    NASHVILLE = auto()
    NEW_ORLEANS = auto()
    NEW_YORK = auto()
    OKLAHOMA_CITY = auto()
    OMAHA = auto()
    PHOENIX = auto()
    PITTSBURGH = auto()
    PORTLAND = auto()
    RALEIGH = auto()
    SAINT_LOUIS = auto()
    SALT_LAKE_CITY = auto()
    SAN_FRANCISCO = auto()
    SANTA_FE = auto()
    SAULT_ST_MARIE = auto()
    SEATTLE = auto()
    TORONTO = auto()
    VANCOUVER = auto()
    WASHINGTON = auto()
    WINNIPEG = auto()

@dataclass
class Ticket:
    start: City
    end: City
    value: int

# List of all tickets on the american version of the game [ start city, end city, point value ]
TICKETS_LIST = [
    [City.BOSTON, City.MIAMI, 12],
    [City.CALGARY, City.PHOENIX, 13],
    [City.CALGARY, City.SALT_LAKE_CITY, 7],
    [City.CHICAGO, City.NEW_ORLEANS, 7],
    [City.CHICAGO, City.SANTA_FE, 9],
    [City.DALLAS, City.NEW_YORK, 11],
    [City.DENVER, City.EL_PASO, 4],
    [City.DENVER, City.PITTSBURGH, 11],
    [City.DULUTH, City.EL_PASO, 10],
    [City.DULUTH, City.HOUSTON, 8],
    [City.HELENA, City.LOS_ANGELES, 8],
    [City.KANSAS_CITY, City.HOUSTON, 5],
    [City.LOS_ANGELES, City.CHICAGO, 16],
    [City.LOS_ANGELES, City.MIAMI, 20],
    [City.LOS_ANGELES, City.NEW_YORK, 21],
    [City.MONTREAL, City.ATLANTA, 9],
    [City.MONTREAL, City.NEW_ORLEANS, 13],
    [City.NEW_YORK, City.ATLANTA, 6],
    [City.PORTLAND, City.NASHVILLE, 17],
    [City.PORTLAND, City.PHOENIX, 11],
    [City.SAN_FRANCISCO, City.ATLANTA, 17],
    [City.SAULT_ST_MARIE, City.NASHVILLE, 8],
    [City.SAULT_ST_MARIE, City.OKLAHOMA_CITY, 9],
    [City.SEATTLE, City.LOS_ANGELES, 9],
    [City.SEATTLE, City.NEW_YORK, 22],
    [City.TORONTO, City.MIAMI, 10],
    [City.VANCOUVER, City.MONTREAL, 20],
    [City.VANCOUVER, City.SANTA_FE, 13],
    [City.WINNIPEG, City.HOUSTON, 12],
    [City.WINNIPEG, City.LITTLE_ROCK, 11]
]

TICKETS = [Ticket(start, end, val) for start, end, val in TICKETS_LIST]

@dataclass
class Route:
    start: City
    end: City
    color: list[e.Card]
    length: int

# All routes that exist [ start city, end city, length, width ]
ROUTES_LIST = [
    [City.VANCOUVER, City.SEATTLE, [None, None], 1],
    [City.VANCOUVER, City.CALGARY, [None], 3],
    [City.SEATTLE, City.PORTLAND, [None, None], 1],
    [City.SEATTLE, City.CALGARY, [None], 4],
    [City.SEATTLE, City.HELENA, [e.Card.YELLOW], 6],
    [City.PORTLAND, City.SALT_LAKE_CITY, [e.Card.BLUE], 6],
    [City.PORTLAND, City.SAN_FRANCISCO, [e.Card.GREEN, e.Card.PURPLE], 5],
    [City.SAN_FRANCISCO, City.SALT_LAKE_CITY, [e.Card.ORANGE, e.Card.WHITE], 5],
    [City.SAN_FRANCISCO, City.LOS_ANGELES, [e.Card.YELLOW, e.Card.PURPLE], 3],
    [City.LOS_ANGELES, City.LAS_VEGAS, [None], 2],
    [City.LOS_ANGELES, City.PHOENIX, [None], 3],
    [City.LOS_ANGELES, City.EL_PASO, [e.Card.BLACK], 6],
    [City.LAS_VEGAS, City.SALT_LAKE_CITY, [e.Card.ORANGE], 3],
    [City.EL_PASO, City.PHOENIX, [None], 3],
    [City.SANTA_FE, City.PHOENIX, [None], 3],
    [City.PHOENIX, City.DENVER, [e.Card.WHITE], 5],
    [City.CALGARY, City.WINNIPEG, [e.Card.WHITE], 6],
    [City.HELENA, City.CALGARY, [None], 4],
    [City.HELENA, City.WINNIPEG, [e.Card.BLUE], 4],
    [City.SALT_LAKE_CITY, City.DENVER, [e.Card.YELLOW, e.Card.RED], 3],
    [City.HELENA, City.SALT_LAKE_CITY, [e.Card.PURPLE], 3],
    [City.HELENA, City.DENVER, [e.Card.GREEN], 4],
    [City.DENVER, City.SANTA_FE, [None], 2],
    [City.EL_PASO, City.SANTA_FE, [None], 2],
    [City.SANTA_FE, City.OKLAHOMA_CITY, [e.Card.BLUE], 3],
    [City.OKLAHOMA_CITY, City.DENVER, [e.Card.RED], 4],
    [City.HELENA, City.DULUTH, [e.Card.ORANGE], 6],
    [City.HELENA, City.OMAHA, [e.Card.RED], 5],
    [City.OMAHA, City.DENVER, [e.Card.PURPLE], 4],
    [City.KANSAS_CITY, City.DENVER, [e.Card.BLACK, e.Card.ORANGE], 4],
    [City.WINNIPEG, City.DULUTH, [e.Card.BLACK], 4],
    [City.WINNIPEG, City.SAULT_ST_MARIE, [None], 6],
    [City.DULUTH, City.OMAHA, [None, None], 2],
    [City.EL_PASO, City.HOUSTON, [e.Card.GREEN], 6],
    [City.EL_PASO, City.DALLAS, [e.Card.RED], 4],
    [City.EL_PASO, City.OKLAHOMA_CITY, [e.Card.YELLOW], 5],
    [City.DALLAS, City.HOUSTON, [None, None], 1],
    [City.DALLAS, City.OKLAHOMA_CITY, [None, None], 2],
    [City.KANSAS_CITY, City.OKLAHOMA_CITY, [None, None], 2],
    [City.OMAHA, City.KANSAS_CITY, [None, None], 1],
    [City.OKLAHOMA_CITY, City.LITTLE_ROCK, [None], 2],
    [City.DALLAS, City.LITTLE_ROCK, [None], 2],
    [City.HOUSTON, City.NEW_ORLEANS, [None], 2],
    [City.LITTLE_ROCK, City.NEW_ORLEANS, [e.Card.GREEN], 3],
    [City.OMAHA, City.CHICAGO, [e.Card.BLUE], 4],
    [City.CHICAGO, City.DULUTH, [e.Card.RED], 3],
    [City.KANSAS_CITY, City.SAINT_LOUIS, [e.Card.BLUE, e.Card.PURPLE], 2],
    [City.DULUTH, City.SAULT_ST_MARIE, [None], 3],
    [City.LITTLE_ROCK, City.SAINT_LOUIS, [None], 2],
    [City.SAINT_LOUIS, City.CHICAGO, [e.Card.GREEN, e.Card.WHITE], 2],
    [City.TORONTO, City.DULUTH, [e.Card.PURPLE], 6],
    [City.SAULT_ST_MARIE, City.TORONTO, [None], 2],
    [City.SAULT_ST_MARIE, City.MONTREAL, [e.Card.BLACK], 5],
    [City.MONTREAL, City.TORONTO, [None], 3],
    [City.NEW_ORLEANS, City.MIAMI, [e.Card.RED], 6],
    [City.NEW_ORLEANS, City.ATLANTA, [e.Card.ORANGE, e.Card.YELLOW], 4],
    [City.LITTLE_ROCK, City.NASHVILLE, [e.Card.WHITE], 3],
    [City.SAINT_LOUIS, City.NASHVILLE, [None], 2],
    [City.ATLANTA, City.NASHVILLE, [None], 1],
    [City.ATLANTA, City.MIAMI, [e.Card.BLUE], 5],
    [City.CHARLESTON, City.MIAMI, [e.Card.PURPLE], 4],
    [City.ATLANTA, City.CHARLESTON, [None], 2],
    [City.RALEIGH, City.CHARLESTON, [None], 2],
    [City.RALEIGH, City.ATLANTA, [None, None], 2],
    [City.NASHVILLE, City.RALEIGH, [e.Card.BLACK], 3],
    [City.CHICAGO, City.TORONTO, [e.Card.WHITE], 4],
    [City.CHICAGO, City.PITTSBURGH, [e.Card.BLACK, e.Card.ORANGE], 3],
    [City.SAINT_LOUIS, City.PITTSBURGH, [e.Card.GREEN], 5],
    [City.NASHVILLE, City.PITTSBURGH, [e.Card.YELLOW], 4],
    [City.PITTSBURGH, City.TORONTO, [None], 2],
    [City.PITTSBURGH, City.RALEIGH, [None], 2],
    [City.WASHINGTON, City.RALEIGH, [None, None], 2],
    [City.PITTSBURGH, City.WASHINGTON, [None], 2],
    [City.WASHINGTON, City.NEW_YORK, [e.Card.ORANGE, e.Card.BLACK], 2],
    [City.PITTSBURGH, City.NEW_YORK, [e.Card.GREEN, e.Card.WHITE], 2],
    [City.MONTREAL, City.NEW_YORK, [e.Card.BLUE], 3],
    [City.MONTREAL, City.BOSTON, [None, None], 2],
    [City.NEW_YORK, City.BOSTON, [e.Card.YELLOW, e.Card.RED], 2],
]

ROUTES = [Route(start, end, color, length) for start, end, color, length in ROUTES_LIST]