import numpy as np
import math
import time
from scipy import spatial
from scipy.spatial import *



######### Algorithm Outline #######
# 1. Initialize error
# 2. Find point correspondence
# 3. Find Alignment
# 4. Apply Alignment
# 5. Update Error
# If error > threshold repeat from 2

def icp_algorithm(base_points, snow_points):
    
    ###### Initializations
    iteration = 0
    error = float("INF")
    #MAKE KD_TREE
    base_tree = spatial.cKDTree(base_points)
    while error > 0.01 and iteration < 100:
        
        ###### FIND POINT CORRESPONDENCE
        # SEARCH FOR CLOSEST POINT FROM SNOW SCENE TO BASE
        # USE EUCLIDEAN DISTANCE or KD-Tree
        base_map_indices = point_correspondence(base_tree, snow_points)
        
        ###### FIND ALIGNMENT
        ### Y = ROT*(SNOW_POINTS) + TRANSLATION
        # FIND ROTATION AND TRANSLATION
        rotation_matrix, translation = calculate_rotation_translation(base_points[base_map_indices], snow_points, base_points)

        ###### 4. APPLY ALIGNMENT
        # NEW_SNOW = ROT*(SNOW_POINTS) + TRANSLATION
        for i in range(len(snow_points)):
            snow_points[i] = np.matmul(rotation_matrix, snow_points[i]) + translation
        
        
        ###### 5. UPDATE ERROR
        iteration += 1
        error_old = round(error, 2)
        error= round(calculate_error(base_points[base_map_indices], snow_points), 2)
        if (error == error_old):
            print("Error not improving")
            break
        # print("\n", "\n")

        print("\niteration", iteration)
        print("error", error)
    # error = calculate_error(base_points[base_map_indices], snow_points)
    # print("iteration", iteration)
    return snow_points, iteration, error

def point_correspondence(kdTree, snow_points):
    ###### 2. FIND POINT CORRESPONDENCE
    # SEARCH FOR CLOSEST POINT FROM SNOW SCENE TO BASE
    # USE EUCLIDEAN DISTANCE or KD-Tree
    ## need to find a better method to assign points. Optimization of point assignments? using error minimization for conflicts? what makes most sense?

    indices = kdTree.query(snow_points)[1]
    
    return indices
    

def calculate_rotation_translation(base_map_points, snow_points, base_points):
    # FIND ROTATION
    # COMPUTE CENTROID
    base_centroid = find_centroid(base_map_points)
    snow_centroid = find_centroid(snow_points)

    # COMPUTE POINT COORDINATE RELATIVE TO CENTROID
    base_map_relative = base_map_points - base_centroid
    snow_points_relative = snow_points - snow_centroid

    # COMPUTE: S_xx = SUM(BASE_xi' * SNOW_xi'), S_xy, S_xz, S_yx, S_yy, ETC...
    # COMPUTE SYMMETRIC MATRIX N BY COMBINING TERMS ABOVE AS FOLLOWS
    # N= [ S_xx + S_yy + S_zz   S_yz - S_zy         -S_xz+Szx        S_xy-Syx
    #     -S_zy + S_yz          S_xx - S_zz - S_yy   S_xy+S_yx       S_xz+S_zx
    #      S_zx - S_xz          S_yx + S_xy          S_yy-S_zz-S_xx  S_yz+S_zy
    #     -S_yx + Sxy           S_zx + S_xz          S_zy+S_yz       S_zz-S_yy-S_xx]
    
    B_rx = base_map_relative[:,0]
    B_ry = base_map_relative[:,1]
    # print("B_ry", B_ry)
    B_rz = base_map_relative[:,2]

    S_rx = snow_points_relative[:,0]
    S_ry = snow_points_relative[:,1]
    S_rz = snow_points_relative[:,2]

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
    
    # rotation_matrix = rotation_matrix[1:,1:]
    ##### TRANSPOSE LIKELY COMES FROM SWAPPING MODEL AND SCENE IN DETERMINING ROTATION MATRIX. MODEL ROTATED TO SCENE vs. SCENE ROTATED TO MODEL
    rotation_matrix = np.transpose(rotation_matrix[1:,1:])
    # print("rotation matrix \n", rotation_matrix)

    base_point_centroid = find_centroid(base_points)
    # print('Calculating translation')
    # translation = calculate_translation(base_point_centroid, snow_centroid, rotation_matrix)

    translation = calculate_translation(base_centroid, snow_centroid, rotation_matrix)

    return rotation_matrix, translation

    
def find_centroid(points):
    centroid = [[0,0,0]]
    for i in range(len(points)):
        # print("Points i", points[i])
        centroid += points[i]
        
    return centroid/len(points)




def calculate_translation(base_centroid, snow_centroid, rotation_matrix):
    # CALCULATE TRANSLATION
    # CALCULATE Q^-T AND Q FROM q
    # T = CENTROID_base - (Q^-T * Q) * CENTROID_snow
    #### Use transpose like we used on the snow points individually
    # rotated_snow = np.transpose(np.matmul(np.transpose(rotation_matrix), np.transpose(snow_centroid)))
    rotated_snow = np.transpose(np.matmul(rotation_matrix, np.transpose(snow_centroid)))
    # print("rotated snow\n", rotated_snow)

    ### Swapped to just the snow centroid. The centroid shouldn't change with rotating the points about it so why would you subject the centroid to a rotation? not rotating centroid gives better results?
    ### UPDATE: Using transpose of rotation matrix makes the rotated snow better!!
    translation = base_centroid - rotated_snow
    # translation = base_centroid - snow_centroid
    # print("translation\n", translation)
    return translation

def calculate_error(base_map_points, snow_points):
    error = 0
    for i in range(len(base_map_points)):
        for j in range(len(base_map_points[i])):
            error += (base_map_points[i,j]-snow_points[i,j])**2

    error = error/len(snow_points)
    # print("Error", error)
    return error


def initial_alignment(base_points, snow_points):
    base_centroid = find_centroid(base_points)
    snow_centroid = find_centroid(snow_points)

    B_rx = base_centroid[:,0]
    B_ry = base_centroid[:,1]
    B_rz = base_centroid[:,2]

    S_rx = snow_centroid[:,0]
    S_ry = snow_centroid[:,1]
    S_rz = snow_centroid[:,2]

    S_xx = np.sum(np.multiply(B_rx,S_rx))
    S_xy = np.sum(np.multiply(B_rx,S_ry))
    S_xz = np.sum(np.multiply(B_rx,S_rz))
    S_yx = np.sum(np.multiply(B_ry,S_rx))
    S_yy = np.sum(np.multiply(B_ry,S_ry))
    S_yz = np.sum(np.multiply(B_ry,S_rz))
    S_zx = np.sum(np.multiply(B_rz,S_rx))
    S_zy = np.sum(np.multiply(B_rz,S_ry))
    S_zz = np.sum(np.multiply(B_rz,S_rz))

    N= [ [S_xx + S_yy + S_zz,   S_yz - S_zy,         -S_xz + S_zx,         S_xy - S_yx],
        [-S_zy + S_yz,          S_xx - S_zz - S_yy,   S_xy+S_yx,          S_xz + S_zx],
        [S_zx - S_xz,           S_yx + S_xy,          S_yy - S_zz - S_xx, S_yz + S_zy],
        [-S_yx + S_xy,           S_zx + S_xz,          S_zy + S_yz,        S_zz-S_yy-S_xx]]

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
    
    # rotation_matrix = rotation_matrix[1:,1:]
    ##### TRANSPOSE LIKELY COMES FROM SWAPPING MODEL AND SCENE IN DETERMINING ROTATION MATRIX. MODEL ROTATED TO SCENE vs. SCENE ROTATED TO MODEL
    rotation_matrix = np.transpose(rotation_matrix[1:,1:])
    # print("rotation matrix \n", rotation_matrix)

    base_point_centroid = find_centroid(base_points)
    # print('Calculating translation')
    # translation = calculate_translation(base_point_centroid, snow_centroid, rotation_matrix)

    translation = calculate_translation(base_centroid, snow_centroid, rotation_matrix)

    return rotation_matrix, translation



