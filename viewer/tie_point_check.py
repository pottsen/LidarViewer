import numpy as np
from scipy import spatial, signal
from scipy.spatial import *
import time
import sys
import math
import copy

def tie_point_error(base, alignment, matched):
        print("Calculating Tie Point Error:")
        # print("Making trees..")
        # base_tree = spatial.cKDTree(base)
        # alignment_tree = spatial.cKDTree(alignment)

        ######## BC Scan 1
        # LookersRight
        # alignment_tie_points = [[-12.979106, -261.574128, 1732.78212], [-12.648628, -319.262555, 1745.626416], [-13.517328, -108.493827, 1687.991239]]
        # alignment_tp_indices = [36901, 39998, 33591]
        # LookersLeft
        # base_tie_points = [[-12.791863, -261.608945, 1732.800418], [-12.772755, -319.273812, 1745.343716], [-13.558948, -108.43461, 1687.963776]]
        # base_tp_indices = [36349, 36733, 31823]

        ######## Lift Shack
        # Lift Balcony
        # base_tie_points = [[-427.650349, -837.341975, 2927.88136], [-555.438164, -828.128651, 2987.397632]]
        # base_tp_indices = [814572, 461567]
        # On Snow
        # alignment_tie_points = [[-427.58228, -837.413667, 2927.735315], [-555.539838, -828.076453, 2987.205581]]
        # alignment_tp_indices = [265581, 156224] 
        
        ######### Test5 and Test10
        # Test10
        # base_tie_points = [[-704.858655, -250.928919, 2815.650352], [-894.031537, -136.883815, 2858.912302]]
        # Test 10 for test5 big
        # base_tie_points = [[-704.858655, -250.928919, 2815.650352], [-900.301597, 73.905413, 2845.349185]]
        # # base_tp_indices = [4024008,  268708]

        # # Test5
        # # alignment_tie_points = [[-704.858655, -250.928919, 2815.650352], [-893.585119, -137.797877, 2859.365728]]
        # # Test5 big
        # alignment_tie_points = [[-704.858655, -250.928919, 2815.650352], [-900.306196 , 73.957415, 2845.182149]]
        # alignment_tp_indices = [948812,  20731]
        """
        Original error
        Total:  1.1167521875000246
        Normalized:  0.5583760937500123
        Match error
        Total:  0.9651570217744727
        Normalized:  0.48257851088723636
        """


        ######### Cliffs
        """
        ## Original Error:
        ## Total:  0.09865093749995223
        ## Normalized:  0.03288364583331741
        ## Match error
        ## Total:  0.037359259362686054
        ## Normalized:  0.012453086454228685
        """
        ## Lift Balcony
        # base_tie_points = [[-710.589053, -232.794525, 2814.560238], [-836.109332, -265.927537, 2892.579737], [-898.181519, -112.218379, 2857.614506]]
        base_tp_indices = [1024539,  278226,   23014]
        ## On Snow
        # alignment_tie_points = [[-710.600795, -232.817664, 2814.398774], [-836.101498, -265.969774, 2892.424745], [-898.058942, -112.37893, 2857.511832]]
        alignment_tp_indices = [1104461,  318444,   18474]
        
        
        print("Querying the trees...")
        # base_tp_indices = base_tree.query(base_tie_points)[1]
        # alignment_tp_indices = alignment_tree.query(alignment_tie_points)[1]

        print("Base Indices: ", base_tp_indices)
        print("Snow Indices: ", alignment_tp_indices)

        base_tie_points = base[base_tp_indices]
        alignment_tie_points = alignment[alignment_tp_indices]
        match_tie_points = matched[alignment_tp_indices]

        tie_point_original_error = 0.0
        tie_point_matched_error = 0.0

        for i in range(len(base_tp_indices)):
            original_error = 0.0
            matched_error = 0.0
            for j in range(len(base[base_tp_indices[i]])):
                original_error += (float(base[base_tp_indices[i],j]) - float(alignment[alignment_tp_indices[i],j]))**2
                matched_error += (float(base[base_tp_indices[i],j]) - float(matched[alignment_tp_indices[i],j]))**2
            tie_point_original_error += original_error
            tie_point_matched_error += matched_error
            print("Point ", i, "\nOriginal Point Error: ", original_error, "\nOriginal Normalized Error: ", tie_point_original_error/(i+1))
            print("Point ", i, "\nMatched Point Error: ", matched_error, "\nMatched Normalized Error: ", tie_point_matched_error/(i+1))
        
        normalized_tp_orig_error = tie_point_original_error/len(base_tie_points)
        normalized_tp_match_error = tie_point_matched_error/len(base_tie_points)

        print("Original error\n Total: ", tie_point_original_error, "\n Normalized: ", normalized_tp_orig_error)
        print("Match error\n Total: ", tie_point_matched_error, "\n Normalized: ", normalized_tp_match_error)
