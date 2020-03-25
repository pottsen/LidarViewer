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
from iterative_closest_point import *
from icp_rotation import *

# cube1 = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]]

# pyramid1 = [[1, 1, 0]]
# pyramid1 = [[0, 1, 0], [0, 2, 0]]
# pyramid1 = [[0, 1, 0], [0, 2, 0], [0, 1.5, 1]]
pyramid1 = [[1, 1, 0], [1.5, 1, 0], [1, 2, 0], [1.25, 1.5, 1]]

print(pyramid1[0])

pyramid2 = copy.deepcopy(pyramid1)
# rotation_x = np.array(([1, 0, 0], [0, math.cos(math.pi/2), -math.sin(math.pi/2)], [0, math.sin(math.pi/2), math.cos(math.pi/2)]))
rotation_x = np.array(([1, 0, 0], [0, math.cos(math.pi/6), -math.sin(math.pi/6)], [0, math.sin(math.pi/6), math.cos(math.pi/6)]))
# rotation_x = np.array(([1, 0, 0], [0, math.cos(math.pi/12), -math.sin(math.pi/12)], [0, math.sin(math.pi/12), math.cos(math.pi/12)]))

# print(rotation_x)

for i in range(len(pyramid2)):
    # print("c2[i]", pyramid2[i])
    coordinates = np.transpose(pyramid2[i])
    coordinates = np.matmul(rotation_x, coordinates)
    # print("New Coordinates", coordinates)
    pyramid2[i] = coordinates
    # cube2[i] = np.matmul(rotation_x, np.transpose(cube2[i]))
    # print("New c2[i] ", pyramid2[i])
    print(' ')



pyramid1_arr = np.array(pyramid1)
pyramid2_arr = np.array(pyramid2)
pyramid3_arr = copy.deepcopy(pyramid2_arr)
print("P2", pyramid2_arr)
pyramid3_arr = icp_algorithm(pyramid1_arr, pyramid3_arr)
# pyramid3_arr = icp_rotation(pyramid1_arr, pyramid3_arr)


print("P2", pyramid2_arr)
print("P3", pyramid3_arr)

canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()
scatter = visuals.Markers()
scatter.set_data(pyramid1_arr, edge_color = None, face_color = "red", size = 20)
view.add(scatter)
scatter2 = visuals.Markers()
scatter2.set_data(pyramid2_arr, edge_color = None, face_color = "blue", size = 20)
view.add(scatter2)
scatter3 = visuals.Markers()
scatter3.set_data(pyramid3_arr, edge_color = None, face_color = "green", size = 20)
view.add(scatter3)
view.camera = 'arcball' #'turntable'  # or try 'arcball'
# add a colored 3D axis for orientation
# Axes are x=red, y=green, z=blue
axis = visuals.XYZAxis(parent=view.scene)
vispy.app.run()