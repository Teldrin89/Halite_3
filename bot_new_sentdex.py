# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
from hlt.positionals import Direction
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("Teldrin89_Python_Bot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """
# dictionary created outside of game loop
ship_states = {}
while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []
    # direction order list: move up, down, left, right or stand still
    direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]
    # added position choices that will contain a physical coordinate of a map - created to avoid ships crashing
    position_choices = []

    for ship in me.get_ships():
        # populate dictionary if ship is collecting
        if ship.id not in ship_states:
            ship_states[ship.id] = "collecting"

        # Introduce choices for the given ship
        position_options = ship.position.get_surrounding_cardinals() + [ship.position]
        # create a position dictionary, will map movement to the map coordinates
        position_dict = {}
        # create a halite dictionary that will map the position with halite amount at that position
        halite_dict = {}
        for n, direction in enumerate(direction_order):
            position_dict[direction] = position_options[n]

        for direction in position_dict:
            position = position_dict[direction]
            halite_amount = game_map[position].halite_amount
            if position_dict[direction] not in position_choices:
                halite_dict[direction] = halite_amount
            else:
                logging.info("attempting to move to the same spot\n")

        # if loop to check if given ship has a "depositing" or "collecting" tag
        if ship_states[ship.id] == "depositing":
            # in case of depositing the ship has to move towards shipyard to drop halite
            move = game_map.naive_navigate(ship, me.shipyard.position)
            # add to position choices
            position_choices.append(position_dict[move])
            # add the move to command que
            command_queue.append(ship.move(move))
            # added the logic for ship after it reaches shipyard and drops off halite
            if move == Direction.Still:
                ship_states[ship.id] = "collecting"
        elif ship_states[ship.id] == "collecting":
            # checks if halite on the map is lower than 10% of max halite - it moves to location with more
            # commented from previous version
            # if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10:
            directional_choice = max(halite_dict, key=halite_dict.get)
            position_choices.append(position_dict[directional_choice])
            command_queue.append(ship.move(game_map.naive_navigate(ship, position_dict[directional_choice])))
            # if the ship has more than a 1/3 of max capacity - this to avoid the bad collisions with enemy ship
            # that could cause a whole max halite amount of ship lost
            if ship.halite_amount > constants.MAX_HALITE * 0.90:
                # change of ship tag to "depositing"
                ship_states[ship.id] = "depositing"

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
