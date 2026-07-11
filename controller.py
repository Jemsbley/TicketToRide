import american_board as a
import game as g

class Controller:
    """ Defines the behaviors of a controller that will request decisions from a given strategy """

    def __init__(self):
        # TODO field for the response modal through which we forward requests
        return


    def draw_tickets(self, drawn: list[a.Ticket], min_keep: int, gamestate: g.PlayerPerspectiveGameState) -> list[a.Ticket]:
        # TODO receive the full game state and determine which tickets to keep
        return drawn[:min_keep]


    def make_turn(self, gamestate):
        # TODO receive the full game state and determine which action to take
        return


