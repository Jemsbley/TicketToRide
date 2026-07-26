import random

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


    def draw_trains(self, gamestate: g.PlayerPerspectiveGameState) -> g.Action:
        # TODO receive the full game state and determine which action to do as the second draw
        # print("drwaing again")
        if gamestate.deck_left > 0:
            return e.DrawType.DECK
        elif len(gamestate.revealed_cards) > 0 and gamestate.revealed_cards[0] != e.Card.WILD:
            return 0
        else:
            return e.Pass.PASS


    def make_turn(self, gamestate: g.PlayerPerspectiveGameState) -> g.Action:
        # TODO receive the full game state and determine which action to take
        choices = [0, 1, 2]
        while True:
            if len(choices) == 0:
                # print(gamestate)
                # print(gamestate.my_hand)
                return e.Pass.PASS
            choice = random.choice(choices)
            if choice == 0:
                if gamestate.deck_left == 0:
                    if len(gamestate.revealed_cards) == 0:
                        choices.remove(0)
                        continue
                    else:
                        return 0
                return e.DrawType.DECK
            elif choice == 1:
                if gamestate.tickets_left == 0:
                    choices.remove(1)
                    continue
                # print("tickets")
                return e.DrawTickets.DRAWTICKETS
            elif choice == 2:
                all_routes = self._find_open_routes(gamestate)
                random.shuffle(all_routes)
                for rs in all_routes:
                    for item in rs.claims.keys():
                        if rs.claims[item] is None:
                            cards = self._count_colors(gamestate, item)
                            if len(cards) >= rs.route.length:
                                # print("claiming")
                                return g.Claim(rs.route.start, rs.route.end, item, cards[:rs.route.length])
                choices.remove(2)



    def _find_open_routes(self, gamestate: g.PlayerPerspectiveGameState) -> list[g.RouteState]:
        to_return: list[g.RouteState] = []
        for route in gamestate.routes:
            for item in route.claims.keys():
                if route.claims[item] is None and route not in to_return:
                    to_return.append(route)
        return to_return


    def _count_colors(self, gamestate: g.PlayerPerspectiveGameState, color) -> list[e.Card]:
        count = []
        if color is None:
            my_cards_sorted = dict()
            most = 0
            to_use = None
            for color in e.Card:
                my_cards_sorted[color] = []
            for item in gamestate.my_hand:
                if item in my_cards_sorted.keys():
                    my_cards_sorted[item].append(item)
            for item in my_cards_sorted.keys():
                if to_use is None or most < len(my_cards_sorted[item]):
                    most = len(my_cards_sorted[item])
                    to_use = item
            return my_cards_sorted[to_use]

        for item in gamestate.my_hand:
            if item == color or item == e.Card.WILD:
                count.append(item)
        return count