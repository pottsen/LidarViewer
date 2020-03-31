import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys
import math
import random
from remove_duplicates import remove_duplicates
import copy
import vispy.scene
from vispy.scene import visuals
from iterative_closest_point import *
from icp_rotation import *

cloud_x = 100
cloud_y = 100

test_case = 1
# results_file = open("results_10k_ext.txt", "w+")
# results_file = open("results_100k.txt", "w+")
# results_file = open("results_1M.txt", "w+")
results_file = open("results_size_test.txt", "w+")

while test_case <= 10:
    cloud_size = int(cloud_x*cloud_y)
    start = time.time()
    print('Creating point cloud')
    base_cloud = []
    for i in range(cloud_x):
        for j in range(cloud_y):
            base_cloud.append([float(i), float(j), float(0)])

    # print(pyramid1[0])
    base_cloud = np.array(base_cloud)

    ### TEST CASES
    # RANDOM POINT SHIFT
    for i in range(int(cloud_size/2)):
        j = random.randint(1, cloud_size-1)
        height = random.randint(1,5)
        base_cloud[j] += [0, 0, height]

    base_cloud = np.array(base_cloud)
    snow_cloud = copy.deepcopy(base_cloud)

    angle_x = math.pi/random.randint(2,24)
    print("angle x", angle_x*180/math.pi)

    angle_y = math.pi/random.randint(2,24)
    print("angle y", angle_y*180/math.pi)

    angle_z = math.pi/random.randint(2,24)
    print("angle z", angle_z*180/math.pi)
  
    rotation_x = np.array(([1, 0, 0], [0, math.cos(angle_x), -math.sin(angle_x)], [0, math.sin(angle_x), math.cos(angle_x)]))
    
    rotation_y = np.array(([math.cos(angle_y), 0, math.sin(angle_y)], [0, 1, 0], [-math.sin(angle_y), 0, math.cos(angle_y)]))
    
    rotation_z = np.array(([math.cos(angle_z), -math.sin(angle_z), 0],[math.sin(angle_z), math.cos(angle_z), 0], [0, 0, 1]))

    shift_x = random.gauss(0,1)*50
    print("shift x", shift_x)
    shift_y = random.gauss(0,1)*50
    print("shift y", shift_y)
    shift_z = random.gauss(0,1)*50
    print("shift z", shift_z)

    # print(rotation_x)
    print('rotating second cloud')
    for i in range(len(snow_cloud)):
        # print("c2[i]", snow_cloud[i])
        coordinates = np.transpose(snow_cloud[i])
        coordinates = np.matmul(rotation_x, coordinates)
        coordinates = np.matmul(rotation_y, coordinates)
        coordinates = np.matmul(rotation_z, coordinates)
        snow_cloud[i] = coordinates

    snow_cloud += [shift_x, shift_y, shift_z]



    base_cloud_arr = np.array(base_cloud)
    snow_cloud_arr = np.array(snow_cloud)
    match_cloud_arr = copy.deepcopy(snow_cloud_arr)

    match_cloud_arr, iteration, error = icp_algorithm(base_cloud_arr, match_cloud_arr)
    end = time.time()
    duration = end-start
    if iteration >= 999:
        flag = str("FAIL - Max iterations reached")
    else:
        flag = str("Passed")
    print("Test Case", test_case)
    print("Time", duration)
    print("\n")
    
    
    results_file.write("\nTest Case " + str(test_case) + "\nCloud Size " + str(cloud_size) + "\nAngles " + str(angle_x*180/math.pi) + " " + str(angle_y*180/math.pi) + " " + str(angle_z*180/math.pi) + "\nShifts " + str(shift_x) + " " + str(shift_y) + " " + str(shift_z) + "\n" + flag + "\nIterations " + str(iteration) + "\nError " + str(error) + "\nTime " + str(duration) + "\n")

    test_case += 1
    cloud_x += 100
    cloud_y += 100

results_file.close()
    

canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()
scatter = visuals.Markers()
scatter.set_data(base_cloud_arr, edge_color = None, face_color = "red", size = 10)
view.add(scatter)
scatter2 = visuals.Markers()
scatter2.set_data(snow_cloud_arr, edge_color = None, face_color = "blue", size = 10)
view.add(scatter2)
scatter3 = visuals.Markers()
scatter3.set_data(match_cloud_arr, edge_color = None, face_color = "green", size = 10)
view.add(scatter3)
view.camera = 'arcball' #'turntable'  # or try 'arcball'
# add a colored 3D axis for orientation
# Axes are x=red, y=green, z=blue
axis = visuals.XYZAxis(parent=view.scene)
vispy.app.run()
