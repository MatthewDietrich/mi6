"""
MAKE IT SIX

An unofficial Python implementation of Arrowplay Game Design's premier
roll-and-reface dice game.
"""


from src import config, game


if __name__ == "__main__":
    game.Game(config.NUM_PLAYERS).run()
