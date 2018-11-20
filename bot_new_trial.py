# Import the Halite SDK, which will let you interact with the game.
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

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# Get size of the map (for future map loops)
gm_height = game.game_map.height
gm_width = game.game_map.width
ship_states = {}
# Create a direction order list: move up, down, left, right or hold still
direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("Teldrin89_Python_Bot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:
    game.update_frame()
    me = game.me
    game_map = game.game_map
    command_queue = []
    # Generate the list of ships to get the number of them
    number_of_ships = len(me.get_ships())
    # added position choices that will contain a physical coordinate of a map - created to avoid ships crashing
    # TODO - not used for now to avoid crashing but still used for movement
    position_choices = []
    # Created a dictionary that will contain all ships current positions
    ships_positions = {}
    # Run for loop for all ships on map
    for ship in me.get_ships():
        # Populate the dictionary w key:value pair of ship id and ship position
        ships_positions[ship.id] = ship.position

    for ship in me.get_ships():
        # Populate dictionary if ship is collecting
        if ship.id not in ship_states:
            ship_states[ship.id] = "collecting"

        # Introduce choices for the given ship
        position_options = ship.position.get_surrounding_cardinals() + [ship.position]
        # Create a position dictionary, will map movement to the map coordinates: {(0,1) : (19,48)}
        position_dict = {}
        # Create a halite dictionary that will map the position with halite amount at that position
        # {(0,1) : 550}
        halite_dict = {}
        # Populate the position dictionary for current ship with actual coordinates
        for n, direction in enumerate(direction_order):
            position_dict[direction] = position_options[n]
        # Populate the halite dictionary, taking the halite amount for each position from position
        # dictionary and also varying based on the selected direction promoting standing still (to avoid
        # constant movements from one position to the other - TODO consider putting additional if for small
        # differences in surrounding positions)
        for direction in position_dict:
            position = position_dict[direction]
            halite_amount = game_map[position].halite_amount
            if direction == Direction.Still:
                halite_dict[direction] = halite_amount * 3
            else:
                halite_dict[direction] = halite_amount

        # Check if given ship has a "depositing" or "collecting" tag
        if ship_states[ship.id] == "depositing":
            # in case of depositing the ship has to move towards shipyard to drop halite
            move = game_map.naive_navigate(ship, me.shipyard.position)
            # add to position choices
            position_choices.append(position_dict[move])
            # add the move to command que
            command_queue.append(ship.move(move))
            # added the logic for ship after it reaches shipyard and drops off halite
            if ship.position == me.shipyard.position:
                ship_states[ship.id] = "collecting"
        elif ship_states[ship.id] == "collecting":
            # Create a directional choice based on the max halite in halite dictionary
            directional_choice = max(halite_dict, key=halite_dict.get)
            position_choices.append(position_dict[directional_choice])
            command_queue.append(ship.move(game_map.naive_navigate(ship, position_dict[directional_choice])))
            # If ship has more than 90% of it's capacity the tag will change to depositing
            if ship.halite_amount > constants.MAX_HALITE * 0.90:
                # change of ship tag to "depositing"
                ship_states[ship.id] = "depositing"

    # If there is no ship then spawn one - up until 15 ships in total
    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.

    if number_of_ships < 20:
        if game.turn_number <= 150 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
            command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

