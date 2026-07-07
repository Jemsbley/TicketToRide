# Start of game values
START_OF_GAME_PLAYER_TRAIN_COUNT = 45 # Each player starts the game with this many trains
START_OF_GAME_TRAIN_DRAW = 4 # Each player starts the game with this many train cards
START_OF_GAME_TICKET_DRAW = 3 # Each player draws this many tickets at the start of the game
START_OF_GAME_TICKET_REQUIRED_KEEP = 2 # Each player must keep at least this many of the drawn tickets during this game

# Deck setup values
NUM_STANDARD_COLOR_CARDS = 12 # There are these many of each of the standard colored cards in a game deck
NUM_ADDITIONAL_WILD_CARDS = 2 # How many more wildcards exist in the deck than standard color

# Available open cards rule values
FACE_UP_CARD_COUNT = 5 # These many cards will be face up at the draw area at all times
WILD_REDRAW_COUNT = 3 # If at any point the number of face up cards equals this value, redraw the entire face up set

# Gameplay values
MAX_CARDS_PER_TURN_DRAWN = 2 # A player may draw this many cards should they draw trains during their turn (except for wild rules)
TICKETS_DRAWN_DURING_TURN = 3 # A player must draw this many tickets if they choose to draw tickets during their turn
TICKETS_REQUIRED_KEEP_DURING_TURN = 1 # The amount of tickets you are required to keep after drawing tickets during your turn
MAX_TRAINS_FOR_GAME_END = 2 # When a player has this many trains remaining, the game cycles one more turn and ends.

# Scoring system values
LONGEST_PATH_BONUS = 10 # The player with the longest continuous path at the end of the game receives this many points
PATH_LENGTH_POINTS = [0, 1, 2, 4, 7, 10, 15] # When completing a route of length x, the player receives this array at x many points
# ^ the zero is padded here so it can effectively be 1-indexed and we do not need to subtract 1 from the length when we request values