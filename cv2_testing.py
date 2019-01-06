# import cv2 and numpy libraries for test of image visualisation of halite map for each turn
import cv2
import numpy as np
# run a for loop just for single image - turn 2
for i in range(2, 401):
    # load data to variable "d"
    d = np.load(f'game_play/{i}.npy')
    # use cv2 to show image of created "d", resized to 20 times
    cv2.imshow("", cv2.resize(d, (0, 0), fx=20, fy=20))
    # add a wait time
    cv2.waitKey(25)
