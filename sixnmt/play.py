import click

from .game_state import GameState
from .player_state import InteractivePlayerStrategy


@click.command()
@click.option('-p', "--players", type=int, default=4, help='Number of players')
@click.option('-s', "--spectator-mode", is_flag=True, default=False, help="Make all players AIs")
def play(players, spectator_mode):
    game = GameState(players)
    if not spectator_mode:
        game.players[0].set_strategy(InteractivePlayerStrategy())
    game.play_game()


if __name__ == '__main__':
    play()
