from controller import Controller
from game import Game

game = Game()

player_count = 2
players = []
for _ in range(player_count):
    players.append(Controller())

winner = game.start(players)

print("The winner is " + winner.name)