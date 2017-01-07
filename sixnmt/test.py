from player_state import InteractivePlayerStrategy
from game_state import GameState
import sys

game = GameState(4)

if sys.argv[1] == "h":
    print("Making first player Human")
    game.players[0].set_strategy(InteractivePlayerStrategy())


game.deal_hands()

game.play_game()
