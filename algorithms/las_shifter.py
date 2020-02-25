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

    shifted_z = base_file.z + 10

    shift_file_name = file_name+'_shifted.las'
    shift_file = File(shift_file_name, mode = "w", header = base_file.header)
    shift_file.points = base_file.points
    shift_file.z = shifted_z
    shift_file.close()
    
    return shift_file_name

if __name__ == "__main__":
        las_shifter(sys.argv[1])
