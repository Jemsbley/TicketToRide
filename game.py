import random
from dataclasses import dataclass

import american_board as a
import constants as c
import controller
import enums as e
from enums import PlayerColor
from view import GameView


@dataclass
class RouteState:
    """ Defines the state of a route """
    route: a.Route
    claims: dict[e.Card, e.PlayerColor | None]


@dataclass
class Claim:
    """ Defines the information in a claim attempted by a player """
    start: a.City
    end: a.City
    path_color: e.Card
    cards: list[e.Card]


DrawTrain = e.DrawType | int

# An action is either drawing in some aspect or attempting to claim a route
Action = e.DrawTickets | Claim | DrawTrain | e.Pass


@dataclass
class PlayerPerspectiveGameState:
    """ Defines the state of a game from a scoped individual player perspective """
    players: list[e.PlayerColor]
    scores: dict[e.PlayerColor, int]
    longest_road_owner: e.PlayerColor
    longest_road_length: int
    my_hand: list[e.Card]
    trains_remaining: dict[e.PlayerColor, int]
    my_tickets: list[a.Ticket]
    revealed_cards: list[e.Card]
    tickets_left: int
    deck_left: int
    player_turn: e.PlayerColor
    turn_number: int
    routes: list[RouteState]


def _create_deck() -> list[e.Card]:
    """ Creates the deck of cards """
    new_deck: list[e.Card] = []
    for card in e.Card:
        new_deck.extend([card for _ in range(c.NUM_STANDARD_COLOR_CARDS)])
    new_deck.extend([e.Card.WILD for _ in range(c.NUM_ADDITIONAL_WILD_CARDS)])
    random.shuffle(new_deck)
    return new_deck


def _initialize_routes() -> list[RouteState]:
    """ Initializes the routes of the game """
    all_routes = [RouteState(item, {color: None for color in item.color}) for item in a.ROUTES]
    return all_routes


class Game:
    """ Defines the behaviors of the game """

    def __init__(self):
        """ Sets up the fields of the game"""
        self.players: dict[e.PlayerColor, controller.Controller] = dict()
        self.scores: dict[e.PlayerColor, int] = dict()
        self.longest_road_owner: e.PlayerColor = [col for col in e.PlayerColor][0]
        self.longest_road_length: int = 0
        self.hands: dict[e.PlayerColor, list[e.Card]] = dict()
        self.trains_remaining: dict[e.PlayerColor, int] = dict()
        self.player_tickets: dict[e.PlayerColor, list[a.Ticket]] = dict()
        self.deck: list[e.Card] = []
        self.revealed_cards: list[e.Card] = []
        self.withdraw_pile: list[e.Card] = []
        self.tickets: list[a.Ticket] = []
        self.player_turn: e.PlayerColor = [col for col in e.PlayerColor][0]
        self.turn_cycle: dict[e.PlayerColor, e.PlayerColor] = dict()
        self.routes: list[RouteState] = []
        self.is_ending: bool = False
        self.turn_number: int = 0
        self.in_progress: bool = False
        self.views: dict[e.PlayerColor, GameView] = dict()
        self.passes: int = 0


    def start(self, players: list[controller.Controller]) -> PlayerColor:
        """ Starts and plays out the game """
        # TODO make viewing conditional as an argument to this method
        if self.in_progress:
            raise ValueError("Game already started")
        if len(players) < 2 or len(players) > 5:
            raise ValueError("Invalid number of players. Must be between 2 and 5 (inclusive)")
        self.in_progress = True
        colors = [col for col in e.PlayerColor]
        color_prev = colors[0]
        for i in range(len(players)):
            self.players[colors[i]] = players[i]
            self.hands[colors[i]] = []
            self.scores[colors[i]] = 0
            self.trains_remaining[colors[i]] = c.START_OF_GAME_PLAYER_TRAIN_COUNT
            if i > 0:
                self.turn_cycle[color_prev] = colors[i]
                color_prev = colors[i]
        self.turn_cycle[color_prev] = colors[0]

        self.deck = _create_deck()
        self.routes = _initialize_routes()
        for hand in self.hands.values():
            for i in range(c.START_OF_GAME_TRAIN_DRAW): hand.append(self._draw_from_deck())
        self._refill_reveal()
        self.tickets = a.TICKETS
        random.shuffle(self.tickets)
        for player in self.players.keys():
            self.player_tickets[player] = []
            self.views[player] = GameView(player)
            self.views[player].redraw(self._get_game_state(player))
            self._draw_tickets(player, c.START_OF_GAME_TICKET_DRAW, c.START_OF_GAME_TICKET_REQUIRED_KEEP)
        while not self.is_ending:
            if self.passes == len(self.players.keys()):
                break
            self.player_turn = self.turn_cycle[self.player_turn]
            if self.player_turn == colors[0]:
                self.turn_number += 1
            for color in self.views.keys():
                self.views.get(color).redraw(self._get_game_state(color))
            action = self.players.get(self.player_turn).make_turn(self._get_game_state(self.player_turn))
            self._complete_action(self.player_turn, action)
            if self.trains_remaining[self.player_turn] <= 2:
                self.is_ending = True
        final_turn = self.player_turn
        self.player_turn = self.turn_cycle[self.player_turn]
        self.turn_number += 1
        while not self.player_turn == final_turn:
            self.player_turn = self.turn_cycle[self.player_turn]
            for color in self.views.keys():
                self.views.get(color).redraw(self._get_game_state(color))
            action = self.players.get(self.player_turn).make_turn(self._get_game_state(self.player_turn))
            self._complete_action(self.player_turn, action)
        first = None
        max = -1
        for item in self.scores.keys():
            if self.scores[item] > max:
                first = item
        return first


    def _complete_action(self, color: e.PlayerColor, action: Action, can_draw_wild: bool = True, drawn_once: bool = False) -> int:
        """ Attempts to complete a turn action provided by a player. Returns 0 on success and 1 on failure """
        if isinstance(action, e.Pass):
            self.passes += 1
            return 0
        self.passes = 0

        if isinstance(action, DrawTrain):
            if isinstance(action, e.DrawType):
                self.hands[color].append(self._draw_from_deck())
                if not drawn_once and (len(self.deck) + len(self.withdraw_pile) > 0 or len(self.revealed_cards) > 0):
                    self._complete_action(color, self.players.get(color).draw_trains(self._get_game_state(color)), drawn_once = True)
                return 0
            else:
                card = self.revealed_cards.pop(action)
                if len(self.deck) or len(self.withdraw_pile) > 0:
                    self._refill_reveal()
                self.hands[color].append(card)
                if card != e.Card.WILD and not drawn_once:
                    self._complete_action(color, self.players.get(color).draw_trains(self._get_game_state(color)),
                                          False)
                    return 0
                elif not can_draw_wild:
                    raise ValueError("Cannot draw wild card right now")
                return 0
        elif isinstance(action, e.DrawTickets):
            self._draw_tickets(color, c.TICKETS_DRAWN_DURING_TURN, c.TICKETS_REQUIRED_KEEP_DURING_TURN)
            return 0
        elif isinstance(action, Claim):
            rs_found = None
            for index in range(len(self.routes)):
                rs = self.routes[index]
                if (rs.route.start == action.start and rs.route.end == action.end) or (
                        rs.route.end == action.start and rs.route.start == action.end):
                    if rs.claims.get(action.path_color) is not None or color in rs.claims.keys(): return 1
                    rs_found = rs
                    break
            if not self._cards_sufficient(rs_found.route, action.path_color, action.cards):
                return 1
            for card in action.cards:
                if card not in self.hands.get(color):
                    return 1
            rs_found.claims.update({action.path_color: color})
            for card in action.cards:
                self.hands[color].remove(card)
            self.scores[color] += c.PATH_LENGTH_POINTS[rs_found.route.length]
            self.trains_remaining[color] -= rs_found.route.length
            # TODO calculate longest route and determine if we need to reassign the bonus
            return 0
        else:
            raise ValueError("Invalid action")


    def _determine_if_new_longest_route(self, route: a.Route, color: e.PlayerColor) -> int:
        """ Determines if the addition of the given route to the player's claims gives them the longest route.
        Returns the length of this player's longest route including this new route. This player can only acquire
        longest route through the newest addition, so we can always check a DFS starting from this
        route's start and end."""
        # TODO idk if this is correct. make logic for figuring out player's longest route
        players_routes = [rs.route for rs in self.routes if color in rs.claims.keys()]
        return route.length


    def _cards_sufficient(self, route: a.Route, color: e.Card, cards: list[e.Card]) -> bool:
        """ Determines if the cards provided are sufficient for the given route"""
        if len(cards) != route.length:
            return False
        if color is None:
            color_need = None
            for card in cards:
                if card != e.Card.WILD:
                    if color_need is None:
                        color_need = card
                    elif color_need != card:
                        return False
            return True
        for card in cards:
            if card != e.Card.WILD and card != color:
                return False
        return True


    def _route_is_open(self, start: a.City, end: a.City, color: e.Card) -> bool:
        """ Determines if the given route exists and is open """
        for rs in self.routes:
            if (rs.route.start == start and rs.route.end == end) or (rs.route.end == start and rs.route.start == end):
                return rs.claims.get(color) is None
        return False


    def _draw_tickets(self, player: e.PlayerColor, num_to_draw: int, num_to_keep: int):
        drawn = [self.tickets.pop(0) for _ in range(min(num_to_draw, len(self.tickets)))]
        keep = (self.players.get(player).draw_tickets(drawn.copy(), min(num_to_keep, len(drawn)),
                                                               self._get_game_state(self.player_turn)))
        for item in keep:
            if item not in drawn: raise ValueError("Kept ticket not from drawn set")
        put_to_bottom = [item for item in drawn if item not in keep]
        self.player_tickets.get(player).extend(keep)
        self.tickets.extend(put_to_bottom)



    def _get_game_state(self, color: e.PlayerColor) -> PlayerPerspectiveGameState:
        """ Generates the readable game state from a specific player perspective """
        return PlayerPerspectiveGameState(
            [col for col in self.players.keys()],
            self.scores.copy(),
            self.longest_road_owner,
            self.longest_road_length,
            self.hands.get(color).copy(),
            self.trains_remaining.copy(),
            self.player_tickets.get(color).copy(),
            self.revealed_cards.copy(),
            len(self.tickets),
            len(self.deck),
            self.player_turn,
            self.turn_number,
            self.routes
        )


    def _refill_reveal(self):
        """ Refills the revealed cards """
        while True:
            to_reveal = c.FACE_UP_CARD_COUNT - len(self.revealed_cards)
            for i in range(to_reveal):
                self.revealed_cards.append(self._draw_from_deck())
            if self.revealed_cards:
                break
            self.withdraw_pile.extend(self.revealed_cards)
            self.revealed_cards.clear()


    def _reveal_valid_check(self):
        """ Checks if the revealed cards are valid"""
        wild_count = 0
        for card in self.revealed_cards:
            if card == e.Card.WILD:
                wild_count += 1
        return wild_count >= c.WILD_REDRAW_COUNT


    def _draw_from_deck(self):
        """ Draws a card from the deck and reshuffles if necessary """
        if len(self.deck) == 0:
            random.shuffle(self.withdraw_pile)
            self.deck.extend(self.withdraw_pile)
            self.withdraw_pile.clear()
        return self.deck.pop(0)
