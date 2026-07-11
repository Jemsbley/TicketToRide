import random
from dataclasses import dataclass

import american_board as a
import constants as c
import controller
import enums as e


@dataclass
class Claim:
    """ Defines the information in a claim attempt taken by a player """
    start: a.City
    end: a.City
    path_color: e.Card
    cards: list[e.Card]


# An action is either drawing in some aspect or attempting to claim a route
Action = e.DrawType | Claim


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


def _create_deck() -> list[e.Card]:
    """ Creates the deck of cards """
    new_deck: list[e.Card] = []
    for card in e.Card:
        new_deck.extend([card for i in range(c.NUM_STANDARD_COLOR_CARDS)])
    new_deck.extend([e.Card.WILD for i in range(c.NUM_ADDITIONAL_WILD_CARDS)])
    random.shuffle(new_deck)
    return new_deck


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
        self.is_ending: bool = False


    def start(self, players: list[controller.Controller]):
        """ Starts and plays out the game """
        if len(players) < 2 or len(players) > 5:
            raise ValueError("Invalid number of players. Must be between 2 and 5 (inclusive)")
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
        for hand in self.hands.values():
            for i in range(c.START_OF_GAME_TRAIN_DRAW): hand.append(self._draw_from_deck())
        self._refill_reveal()
        self.tickets = a.TICKETS
        random.shuffle(self.tickets)
        for player in self.players.values():
            drawn = [self.tickets.pop(0) for _ in range(c.START_OF_GAME_TICKET_DRAW)]
            put_to_bottom = player.draw_tickets(drawn.copy(), c.START_OF_GAME_TICKET_REQUIRED_KEEP, self._get_game_state(self.player_turn))
            # TODO change put_to_bottom to make sure that the ones that they try to put to bottom are actually from the original list and put the drawn ones in their tickets hand
            self.tickets.extend(put_to_bottom)
        while not self.is_ending:
            self.player_turn = self.turn_cycle[self.player_turn]
            action = self.players.get(self.player_turn).make_turn(self._get_game_state(self.player_turn))
            self._complete_action(self.player_turn, action)
            if self.trains_remaining[self.player_turn] <= 2:
                self.is_ending = True
        final_turn = self.player_turn
        self.player_turn = self.turn_cycle[self.player_turn]
        while not self.player_turn == final_turn:
            self.player_turn = self.turn_cycle[self.player_turn]
            action = self.players.get(self.player_turn).make_turn(self._get_game_state(self.player_turn))
            self._complete_action(self.player_turn, action)
        # TODO declare winner


    def _complete_action(self, color: e.PlayerColor, action: Action):
        # TODO actually complete the player's action
        return



    def _get_game_state(self, color: e.PlayerColor) -> PlayerPerspectiveGameState:
        """ Generates the readable gamestate from a specific player perspective """
        return PlayerPerspectiveGameState(
            [col for col in self.players.keys()],
            self.scores.copy(),
            self.longest_road_owner,
            self.longest_road_length,
            self.hands.get(color).copy(),
            self.trains_remaining.copy(),
            self.tickets.get(color).copy(),
            self.revealed_cards.copy(),
            len(self.tickets),
            len(self.deck),
            self.player_turn
        )


    def _next_turn(self):
        """ Cycles the index logically associated with the player who will make their move next """
        self.player_turn = (self.player_turn + 1) % len(self.players)


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
