## Testing rotation
import numpy as np
import math
import time
from scipy import spatial
from scipy.spatial import *

def icp_rotation(base_points, snow_points):
    ###### 1. Initializations
    iteration = 0
    error = float("INF")
    #MAKE KD_TREE
    while error > 0.01 and iteration < 1:
        
        ###### 2. FIND POINT CORRESPONDENCE
        # SEARCH FOR CLOSEST POINT FROM SNOW SCENE TO BASE
        # USE EUCLIDEAN DISTANCE or KD-Tree
        # print("base map", base_points[base_map_indices])
        # print("snow points", snow_points)
        error = calculate_error(base_points, snow_points)
        ###### 3. FIND ALIGNMENT
        ### Y = ROT*(SNOW_POINTS) + TRANSLATION

        # FIND TRANSLATION USING CENTROIDS
        # CENTROID_i = 1/#POINTS_i * SUM(POINTS_i)
        # POINTS_i' = POINTS_i - CENTROID_i
        # AFTER TRANSFORM: 1/#POINTS_i * SUM(POINTS_i') = 0
        # TRANSLATION WILL THEN BE THE DIFFERENCE IN THE SNOW AND BASE CENTROIDS

        # FIND ROTATION
        rotation_matrix = calculate_rotation(base_points, snow_points)

        # CALCULATE TRANSLATION
        # CALCULATE Q^-T AND Q FROM q
        # T = CENTROID_base - (Q^-T * Q) * CENTROID_snow


        ###### 4. APPLY ALIGNMENT
        # NEW_SNOW = ROT*(SNOW_POINTS) + TRANSLATION
        print("old snow points\n", snow_points)
        for i in range(len(snow_points)):
            print(snow_points[i])
            snow_points[i] = np.matmul(np.transpose(rotation_matrix), snow_points[i])
            print("temp\n", snow_points[i])

        print("new snow points\n", snow_points)
        
        
        ###### 5. UPDATE ERROR
        iteration += 1
        error = calculate_error(base_points, snow_points)
        print("\n", "\n")
    return snow_points

def calculate_rotation(base_map_points, snow_points):
    ###### 3. FIND ALIGNMENT
    ### Y = ROT*(SNOW_POINTS) + TRANSLATION
    # FIND ROTATION
    print("base points\n", base_map_points)
    print("snow points\n", snow_points)
    

    # COMPUTE: S_xx = SUM(BASE_xi' * SNOW_xi'), S_xy, S_xz, S_yx, S_yy, ETC...
    # COMPUTE SYMMETRIC MATRIX N BY COMBINING TERMS ABOVE AS FOLLOWS
    # N= [ S_xx + S_yy + S_zz   S_yz - S_zy         -S_xz+Szx        S_xy-Syx
    #     -S_zy + S_yz          S_xx - S_zz - S_yy   S_xy+S_yx       S_xz+S_zx
    #      S_zx - S_xz          S_yx + S_xy          S_yy-S_zz-S_xx  S_yz+S_zy
    #     -S_yx + Sxy           S_zx + S_xz          S_zy+S_yz       S_zz-S_yy-S_xx]
    
    B_rx = base_map_points[:,0]
    B_ry = base_map_points[:,1]
    print("B_ry", B_ry)
    B_rz = base_map_points[:,2]

    S_rx = snow_points[:,0]
    S_ry = snow_points[:,1]
    S_rz = snow_points[:,2]

    # S_xx = np.sum(np.multiply(S_rx,B_rx))
    # S_xy = np.sum(np.multiply(S_rx,B_ry))
    # S_xz = np.sum(np.multiply(S_rx,B_rz))
    # S_yx = np.sum(np.multiply(S_ry,B_rx))
    # S_yy = np.sum(np.multiply(S_ry,B_ry))
    # S_yz = np.sum(np.multiply(S_ry,B_rz))
    # S_zx = np.sum(np.multiply(S_rz,B_rx))
    # S_zy = np.sum(np.multiply(S_rz,B_ry))
    # S_zz = np.sum(np.multiply(S_rz,B_rz))

    S_xx = np.sum(np.multiply(B_rx,S_rx))
    S_xy = np.sum(np.multiply(B_rx,S_ry))
    S_xz = np.sum(np.multiply(B_rx,S_rz))
    S_yx = np.sum(np.multiply(B_ry,S_rx))
    S_yy = np.sum(np.multiply(B_ry,S_ry))
    S_yz = np.sum(np.multiply(B_ry,S_rz))
    S_zx = np.sum(np.multiply(B_rz,S_rx))
    S_zy = np.sum(np.multiply(B_rz,S_ry))
    S_zz = np.sum(np.multiply(B_rz,S_rz))

    # print("S_xx", S_xx)
    # print("S_xy", S_xy)
    # print("S_xz", S_xz)
    # print("S_yx", S_yx)
    # print("S_yy", S_yy)
    # print("S_yz", S_yz)
    # print("S_zx", S_zx)
    # print("S_zy", S_zy)
    # print("S_zz", S_zz)


    # S_ii = [0 for i in range(9)]
    # for i in range(3):
    #     for j in range(3):
    #         for k in range(len(snow_points_relative)):
    #             S_ii[3*i + j] += base_map_relative[k][i]*snow_points_relative[k][j]

    # print("S_ii\n", S_ii)
   
    # S_xx = S_ii[0]
    # S_xy = S_ii[1]
    # S_xz = S_ii[2]
    # S_yx = S_ii[3]
    # S_yy = S_ii[4]
    # S_yz = S_ii[5]
    # S_zx = S_ii[6]
    # S_zy = S_ii[7]
    # S_zz = S_ii[8]

    N= [ [S_xx + S_yy + S_zz,   S_yz - S_zy,         -S_xz + S_zx,         S_xy - S_yx],
        [-S_zy + S_yz,          S_xx - S_zz - S_yy,   S_xy+S_yx,          S_xz + S_zx],
        [S_zx - S_xz,           S_yx + S_xy,          S_yy - S_zz - S_xx, S_yz + S_zy],
        [-S_yx + S_xy,           S_zx + S_xz,          S_zy + S_yz,        S_zz-S_yy-S_xx]]

    # print("N\n", N)

    ## FIND THE EIGENVALUES AND EIGENVECTORS OF N. 
    # THE QUARTERNION q REPRESENTING THE ROTATION IS THE EIGENVECTOR OF LARGEST EIGENVALUE
    # USE NUMPY np.linalg.eig() function to get eigenvalues/eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(N)
    max_index = np.argmax(eigenvalues)
    # print("max_index", max_index)
    eigen_value = eigenvalues[max_index]
    eigen_vector = eigenvectors[:, max_index]
    # print("eigenvalues\n", eigenvalues)
    # print("eigenvectors\n", eigenvectors)
    # print("Eigen value and vector\n", eigen_value, eigen_vector)

    q0 = eigen_vector[0]
    q1 = eigen_vector[1]
    q2 = eigen_vector[2]
    q3 = eigen_vector[3]

    Qbar = [[q0, -q1, -q2, -q3],
            [q1,  q0,  q3, -q2],
            [q2, -q3,  q0,  q1],
            [q3,  q2, -q1,  q0]]

    # print("Qbar\n", Qbar)

    Q = [[q0, -q1,  -q2,  -q3],
         [q1,   q0,  -q3,   q2],
         [q2,   q3,   q0,  -q1],
         [q3,  -q2,   q1,   q0]]

    # print("Q\n", Q)

    ### TODO: FIND WHICH MULTIPLICATION IS CORRECT
    rotation_matrix = np.matmul(np.transpose(Qbar), Q)
    # rotation_matrix = np.matmul(Qbar, Q)
    # rotation_matrix = np.multiply(Qbar, Q)
    
    rotation_matrix = rotation_matrix[1:,1:]
    print("rotation matrix \n", rotation_matrix)

    return rotation_matrix

def calculate_error(base_map_points, snow_points):
    error = 0
    for i in range(len(base_map_points)):
        for j in range(len(base_map_points[i])):
            error += (base_map_points[i,j]-snow_points[i,j])**2

    error = error/len(snow_points)
    print("Error", error)
    return error