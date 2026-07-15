import american_board as a
import enums as e
import game as g


class Controller:
    """ Defines the behaviors of a controller that will request decisions from a given strategy """
    # TODO consider if I should even bother making a wrapper class or if I should just have a bunch of implemenetations with these methods

    def __init__(self):
        return


    def draw_tickets(self, drawn: list[a.Ticket], min_keep: int, gamestate: g.PlayerPerspectiveGameState) -> list[a.Ticket]:
        # TODO receive the full game state and determine which tickets to keep
        return drawn[:min_keep]


    def draw_trains(self, gamestate: g.PlayerPerspectiveGameState) -> g.DrawTrain:
        # TODO receive the full game state and determine which action to do as the second draw
        return g.DrawTrain(e.DrawType.DECK)


    def make_turn(self, gamestate):
        # TODO receive the full game state and determine which action to take
        return


