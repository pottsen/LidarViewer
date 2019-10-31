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
#     print(file_name)

    shifted_Z = base_file.Z + 1000

    shift_file = File(file_name+'_shifted.las', mode = "w", header = base_file.header)

    shift_file.points = base_file.points
    shift_file.Z = shifted_Z
    shift_file.close()

if __name__ == "__main__":
        las_shifter(sys.argv[1])
