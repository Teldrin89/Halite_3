# script to run halite games in loop as dataset preparation for training of ml model
import os
import secrets

# specify max turns
MAX_TURNS = 50
# specify map settings
map_settings = {
    32: 400,
    40: 425,
    48: 450,
    56: 475,
    64: 500
}

# run a while loop for different map sizes
while True:
    map_size = secrets.choice(list(map_settings.keys()))
    # check the random map size selection - commented out after check
    # print(map_size)
    # break
    # todo: finished on part3 21:08
