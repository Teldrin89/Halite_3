
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

game = hlt.Game()
gm_height = game.game_map.height
gm_width = game.game_map.width
ship_states = {}
direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]
game.ready("Teldrin89_Python_Bot")
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

while True:

    game.update_frame()
    me = game.me
    game_map = game.game_map
    command_queue = []
    number_of_ships = len(me.get_ships())

    for ship in me.get_ships():
        if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
            command_queue.append(
                ship.move(
                    random.choice([Direction.North, Direction.South, Direction.East, Direction.West])))
        else:
            command_queue.append(ship.stay_still())

    if number_of_ships < 10:
        if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
            command_queue.append(me.shipyard.spawn())

    game.end_turn(command_queue)
