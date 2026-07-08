from enum import IntEnum, auto

class City(IntEnum):
    """ Defines the set of cities in the american board of the game """
    ATLANTA = auto()
    BOSTON = auto()
    CALGARY = auto()
    CHICAGO = auto()
    DALLAS = auto()
    DENVER = auto()
    DULUTH = auto()
    EL_PASO = auto()
    HELENA = auto()
    HOUSTON = auto()
    KANSAS_CITY = auto()
    LITTLE_ROCK = auto()
    LOS_ANGELES = auto()
    MIAMI = auto()
    MONTREAL = auto()
    NASHVILLE = auto()
    NEW_ORLEANS = auto()
    NEW_YORK = auto()
    OKLAHOMA_CITY = auto()
    PHOENIX = auto()
    PITTSBURGH = auto()
    PORTLAND = auto()
    SALT_LAKE_CITY = auto()
    SAN_FRANCISCO = auto()
    SANTA_FE = auto()
    SAULT_ST_MARIE = auto()
    SEATTLE = auto()
    TORONTO = auto()
    VANCOUVER = auto()
    WINNIPEG = auto()

# List of all tickets on the american version of the game
TICKETS = [
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