from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys

def las_shifter(las_file):
        base_file_input = las_file
        print(base_file_input)
        base_file = File(base_file_input, mode = "r")

        file_name = base_file_input.split('.')[0]
        print(file_name)

        points = base_file.points

        max_intensity = np.max(base_file.intensity)
        print(max_intensity)
        min_intensity = np.min(base_file.intensity)
        print(min_intensity)


if __name__ == "__main__":
        las_shifter(sys.argv[1])