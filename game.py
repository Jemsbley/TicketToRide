import constants as c
import enums as e
import american_board as a
import controller
import random


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
        self.players: list[controller.Controller] = []
        self.hands: list[list[e.Card]] = []
        self.trains_remaining: list[int] = []
        self.deck: list[e.Card] = []
        self.revealed_cards: list[e.Card] = []
        self.withdraw_pile: list[e.Card] = []
        self.tickets: list[a.Ticket] = []
        self.double_paths: bool = False
        self.player_turn: int = 0


    def initialize(self, players: list[controller.Controller]):
        """ Initializes the game """
        if len(players) < 2 or len(players) > 5:
            raise ValueError("Invalid number of players. Must be between 2 and 5 (inclusive)")
        if len(players) > 3:
            self.double_paths = True
        self.players = players
        self.hands = [[] for _ in range(len(self.players))]
        self.trains_remaining = [c.START_OF_GAME_PLAYER_TRAIN_COUNT for _ in range(len(self.players))]
        self.deck = _create_deck()
        for hand in self.hands:
            for i in range(c.START_OF_GAME_TRAIN_DRAW): hand.append(self._draw_from_deck())
        self._refill_reveal()
        self.tickets = a.TICKETS
        random.shuffle(self.tickets)
        # give players tickets then ask for them to decide which to keep, then start the game
        for player in self.players:
            drawn = [self.tickets.pop(0) for _ in range(c.START_OF_GAME_TICKET_DRAW)]
            put_to_bottom = player.draw_tickets(drawn, c.START_OF_GAME_TICKET_REQUIRED_KEEP) # TODO change this to also provide them the entire game state which they are allowed to see
            self.tickets.extend(put_to_bottom)
        # TODO ask player 0 to begin their turn and actually start the game


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
