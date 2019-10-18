from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys


def depth_calculator(las_files):
        base_file_input = las_files[1]
        # print(base_file_input)
        snow_file_input = las_files[2]
        # print(snow_file_input)

        base_file = File(base_file_input, mode = "r")
        snow_file = File(snow_file_input, mode = "r")

        # points = np.array(base_file.points)

        base_X = np.array(base_file.X)
        # print("base_X ", len(base_X))

        base_Y = np.array(base_file.Y)
        # print("base_Y ", len(base_Y))

        base_Z = np.array(base_file.Z)
        # print("base_Z ", len(base_Z))

        snow_X = np.array(snow_file.X)
        # print("snow_X ", len(snow_X))

        snow_Y = np.array(snow_file.Y)
        # print("snow_Y ", len(snow_Y))

        snow_Z = np.array(snow_file.Z)
        # print("snow_Z ", len(snow_Z))


        base_XY = np.stack((base_X,base_Y), axis=-1)
        snow_XY = np.stack((snow_X,snow_Y), axis=-1)
        print("Created XY arrays")

        np.random.shuffle(base_XY)

        print("Building Tree of size ", len(base_XY))
        start = time.time()
        kdTree = spatial.cKDTree(base_XY)
        end = time.time()
        print("KDTree Loading: " + str(end - start) + " seconds")

        print("Querying Tree with data of size ", len(snow_XY))
        start = time.time()
        indices = kdTree.query(snow_XY)[1]
        end = time.time()
        print("KDTree Query: " + str(end - start) + " seconds")

        depths = snow_Z - base_Z[indices]

        print("Mean depth: " + str(np.mean(depths)))
        print("Max depth: " + str(np.max(depths)))
        print("Min depth: " + str(np.min(depths)))

if __name__ == "__main__":
        depth_calculator(sys.argv)


