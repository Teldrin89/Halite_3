# a trial for ml python bot for halite 3 competition
# based on the sentdex tutorial
# a trial to test the idea of getting some square of coordinates around the ship
# set up size
size = 12
# create an empty list for the surroundings coordinates
surroundings = []
# run a loop for 2 dimensions - x and y - in 4 directions
for y in range(-1*size, size+1):
    # create a row list for single row coordinates
    row = []
    # loop for 2nd coordinate
    for x in range(-1*size, size+1):
        # print(x, y)
        # append each row
        row.append([x, y])
    # append the surroundings with each row
    surroundings.append(row)
# print the result - a square of coordinates for given size
for r in surroundings:
    print(r)
