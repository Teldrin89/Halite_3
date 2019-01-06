# A machine learning bot in python for Halite 3 competition:
# - using the convolutional neural network (evolution learning)
# - the AI will control the movement and decision of either collecting or depositing for each ship
import hlt  # main halite stuff
from hlt import constants  # halite constants
from hlt.positionals import Direction  # helper for moving
from hlt.positionals import Position  # helper for moving
import logging  # logging stuff to console
import numpy as np

game = hlt.Game()  # game object
# Initializes the game
game.ready("Teldrin89_Python_Bot")

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me

    '''comes from game, game comes from before the loop, hlt.Game points to networking, which is where you will
    find the actual Game class (hlt/networking.py). From here, GameMap is imported from hlt/game_map.py.
    open that file to see all the things we do with game map.'''
    game_map = game.game_map  # game map data

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    # specify the order we know this all to be
    direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]
    # information about dropoff and shipyard locations
    dropoff_positions = [d.position for d in list(me.get_dropoffs()) + [me.shipyard]]
    # information about positions of ships - to distinguish enemy and our ships
    ship_positions = [s.position for s in list(me.get_ships())]

    for ship in me.get_ships():
        # use f-string for logging the ship position and relative position - modify by -3 and 3
        # hint: for f-string use either single quotes (') or select from list (select the "f" and press Alt+Enter)
        # remember: add "Position" class from halite positionals to add relative change position
        logging.info(f'{ship.position}, {ship.position + Position(-3, 3)}')
        # 2nd f-string will produce the position of map cell (the relative one) and the amount of halite there
        logging.info(f'{game_map[ship.position + Position(-3,3)]}')

        # decide on a size of square for getting coordinates around the ship - used 16 to use one of the
        # popular ML models (requiring 32x32 grid)
        size = 16
        # create an empty list for the surroundings
        surroundings = []
        # surroundings = [HALITE_AMOUNT, SHIP, DROPOFF, ...] - possibility for the additional properties to be added,
        # for example turn number (to decide how to behave based on the time of game)
        # run a loop for 2 dimensions - x and y - in 4 directions
        for y in range(-1*size, size+1):
            # create a row list for single row coordinates
            row = []
            # loop for 2nd coordinate
            for x in range(-1*size, size+1):
                # print(x, y)
                # marking one of the positions from 32x32 square being checked
                current_cell = game_map[ship.position + Position(x, y)]
                # check if in given position there is our dropoff/shipyard
                if current_cell.position in dropoff_positions:
                    # if yes then variable is equal to 1
                    drop_friend_foe = 1
                else:
                    # if it is the enemy dropoff/shipyard variable is equal to -1
                    drop_friend_foe = -1
                # check if the current position is occupied by our or enemy ship
                if current_cell.position in ship_positions:
                    ship_friend_foe = 1
                else:
                    ship_friend_foe = -1
                # get the halite amount from given cell, divide it by MAX_HALITE (to work with smaller numbers)
                halite = round(current_cell.halite_amount/constants.MAX_HALITE, 2)

                # get a current cell ship and structure (if there is one)
                a_ship = current_cell.ship
                a_structure = current_cell.structure

                # check for the halite, ship and structure - if it is not in given cell set to 0
                if halite is None:
                    halite = 0
                if a_ship is None:
                    a_ship = 0
                else:
                    # if there is a ship get the ship halite amount divided by max and rounded to 2 decimal places
                    # the value will be positive for our ship and negative for enemy ship
                    a_ship = round(ship_friend_foe * (a_ship.halite_amount/constants.MAX_HALITE), 2)

                if a_structure is None:
                    a_structure = 0
                else:
                    # if there is a structure in given cell check if it is our dropoff/shipyard
                    a_structure = drop_friend_foe

                amounts = (halite, a_ship, a_structure)

                # append each row
                row.append(amounts)
            # append the surroundings with each row
            surroundings.append(row)

        if game.turn_number == 5:
            with open("test.txt", "w") as f:
                f.write(str(surroundings))
        # using the numpy library save all turns surroundings (with ships) for each ship as numpy file
        # commented save files to avoid flipping the screen with results as the game was running against itself
        # np.save(f'game_play/{game.turn_number}.npy', surroundings)

        # shift the ship always north to check how it will behave at the edge and crossing the edge of map
        command_queue.append(ship.move(Direction.North))

    # if there is less than 1 ship, create one
    if len(me.get_ships()) < 1:
        # ship costs 1000, don't make a ship on a ship or they both sink
        if me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
            command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
