import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys
import math
from remove_duplicates import remove_duplicates

import copy

import vispy.scene
from vispy.scene import visuals
# x = [0, 1, 0, 1, 0, 1, 0, 1]
# y = [0, 0, 1, 1, 0, 0, 1, 1]
# z = [0, 0, 0, 0, 1, 1, 1, 1]
# cube1 = np.stack((x,y,z))
# cube1 = np.transpose(cube1)

# cube1 = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]]
pyramid1 = [[0, 0, 0], [0.5, 0, 0], [0, 1, 0], [0.25, 0.5, 1]]

print(pyramid1[0])

pyramid2 = copy.deepcopy(pyramid1)
rotation_x = np.array(([1, 0, 0], [0, math.cos(math.pi), -math.sin(math.pi)], [0, math.sin(math.pi), math.cos(math.pi)]))
print(rotation_x)

for i in range(len(pyramid2)):
    print("c2[i]", pyramid2[i])
    coordinates = np.transpose(pyramid2[i])
    coordinates = np.matmul(rotation_x, coordinates)
    print("New Coordinates", coordinates)
    # print(coordinates.shape())
    # print(cube2[i].shape())
    # for j in coordinates:
    #     j = int(j)
    pyramid2[i] = coordinates
    # cube2[i] = np.matmul(rotation_x, np.transpose(cube2[i]))
    print("New c2[i] ", pyramid2[i])
    print(' ')



pyramid1_arr = np.array(pyramid1)
pyramid2_arr = np.array(pyramid2)

print(pyramid2_arr)

canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()
scatter = visuals.Markers()
scatter.set_data(pyramid1_arr, edge_color = None, face_color = "red", size = 20)
view.add(scatter)
scatter2 = visuals.Markers()
scatter2.set_data(pyramid2_arr, edge_color = None, face_color = "blue", size = 20)
view.add(scatter2)
view.camera = 'arcball' #'turntable'  # or try 'arcball'
# add a colored 3D axis for orientation
# Axes are x=red, y=green, z=blue
axis = visuals.XYZAxis(parent=view.scene)
vispy.app.run()