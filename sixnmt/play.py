import click

from .game_state import GameState
from .player_state import InteractivePlayerStrategy


@click.command()
@click.option('-p', "--players", type=int, default=4, help='Number of players')
def play(players):
    game = GameState(players)
    game.players[0].set_strategy(InteractivePlayerStrategy())
    game.play_game()


if __name__ == '__main__':
    play()
