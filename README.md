## Peter Ottsen - Computer Science Master's Student
## Montana State University - May 2021

# January 2021 Update - Crop and Alignment Workflow Demo
https://youtu.be/xgg58JBMem4

# June 2020 - Snowdepth Visualization Workflow Demo
https://youtu.be/JCf_W-9abqg

# LidarViewer

## Setup (Update 10/16/2021)
Anaconda with python 3.7.3-4 is known to work. Laspy package needs to be version<2.0 as they made some changes that break functionality. The package_list.txt has all the packages installed in the environment used for the software.  

### Known Issues:
MacOS seems to have issues with the OpenGL library within Vispy, but I am not sure if this is an M1 chip issues or a general MacOS issue. A google search indicates a general MacOS issue. 

## Notes
Repository for my master's thesis project. The goal is to develop an all in one software tool for editing, aligning, then calculating the snowdepth based on two lidar scans of the same mountianous area.

The algorithms folder contains the work done for algorithms development and testing, while the viewer folder has the most up to date working version of the full software. Run 'python master_main.py' from the command line. 
