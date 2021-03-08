"""
    3D Points Picking & select tool based on Vispy library
    Author: Penny Xuran Qian (NAOC/SAO) pennyqxr@gmail.com
    Controls:
    * 1 - free lasso select
    * 2 - rectangle select
"""

import sys
import numpy as np
import copy

from PyQt5 import QtWidgets, QtCore, QtGui
from vispy import scene
from matplotlib import path
from laspy.file import File


def rectangle_vertice(center, height, width):
    # Borrow from _generate_vertices in vispy/visuals/rectangle.py

    half_height = height / 2.
    half_width = width / 2.

    bias1 = np.ones(4) * half_width
    bias2 = np.ones(4) * half_height

    corner1 = np.empty([1, 3], dtype=np.float32)
    corner2 = np.empty([1, 3], dtype=np.float32)
    corner3 = np.empty([1, 3], dtype=np.float32)
    corner4 = np.empty([1, 3], dtype=np.float32)

    corner1[:, 0] = center[0] - bias1[0]
    corner1[:, 1] = center[1] - bias2[0]
    corner1[:, 2] = 0

    corner2[:, 0] = center[0] + bias1[1]
    corner2[:, 1] = center[1] - bias2[1]
    corner2[:, 2] = 0

    corner3[:, 0] = center[0] + bias1[2]
    corner3[:, 1] = center[1] + bias2[2]
    corner3[:, 2] = 0

    corner4[:, 0] = center[0] - bias1[3]
    corner4[:, 1] = center[1] + bias2[3]
    corner4[:, 2] = 0

    # Get vertices between each corner of the rectangle for border drawing
    vertices = np.concatenate(([[center[0], center[1], 0.]],
                               [[center[0] - half_width, center[1], 0.]],
                               corner1,
                               [[center[0], center[1] - half_height, 0.]],
                               corner2,
                               [[center[0] + half_width, center[1], 0.]],
                               corner3,
                               [[center[0], center[1] + half_height, 0.]],
                               corner4,
                               [[center[0] - half_width, center[1], 0.]]))

    # vertices = np.array(output, dtype=np.float32)
    return vertices[1:, ..., :2]

class Scene(QtWidgets.QWidget):
    def __init__(self, grid, points, color, scene_type, keys='interactive'):
        super(Scene, self).__init__()
        # Layout and canvas creation
        box = QtWidgets.QVBoxLayout(self)
        # self.resize(500, 500)
        self.grid = grid
        # print('grid', self.grid)
        self.setLayout(box)
        self.canvas = scene.SceneCanvas(keys=keys)
        self.scene_type = scene_type
        box.addWidget(self.canvas.native)
        self.total_selected = [False for i in points]

        # Connect events
        self.canvas.events.mouse_press.connect(self.on_mouse_press)
        self.canvas.events.mouse_release.connect(self.on_mouse_release)
        self.canvas.events.mouse_move.connect(self.on_mouse_move)
        self.canvas.events.key_press.connect(self.on_key_press)

        # Setup some defaults
        self.mesh = None
        self.selected = []
        self.white = (1.0, 1.0, 1.0)#, 1.0)
        self.black = (0.0, 0.0, 0.0)#, 0.0)

        # Data
        self.data = points
        avg_x = np.average(self.data[:,0])
        avg_y = np.average(self.data[:,1])
        avg_z = np.average(self.data[:,2])
        
        # Camera
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.cameras.TurntableCamera(#fov=45,
        elevation=-np.arctan(avg_z/avg_x)*360,
        azimuth=np.arctan(avg_y/avg_x)*360,
        roll=np.arctan(avg_z/avg_y)*360,
        distance=np.sqrt(avg_x**2+avg_y**2+avg_z**2),
        center=(avg_x, avg_y, avg_z))

        # Add Plot
        self.base_facecolor = copy.deepcopy(color)
        self.facecolor = copy.deepcopy(color)
        self.ptsize = 3
        self.scatter = scene.visuals.Markers()
        self.scatter.set_data(self.data, face_color=self.facecolor,
                              edge_color=None, size=self.ptsize)
        self.view.add(self.scatter)

        font_size = 20.0
        # Add a text instruction
        self.text = scene.visuals.Text('', pos=(self.canvas.size[0],  20),
                                       color='w', parent=self.canvas.scene)
        self.stats_text = scene.visuals.Text('', pos=(self.canvas.size[0]/3.0,  int(font_size*1.33+font_size*1.33*0.5)),
                                       color='w', bold = True, font_size = font_size, parent=self.canvas.scene)
        self.stats_text2 = scene.visuals.Text('', pos=(self.canvas.size[0]/3.0,  int(font_size*1.33*2+font_size*1.33*2*0.5)),
                                       color='w', bold = True, font_size = font_size, parent=self.canvas.scene)
        self.stats_text3 = scene.visuals.Text('', pos=(self.canvas.size[0]/3.0,  int(font_size*1.33*3+font_size*1.33*3*0.5)),
                                       color='w', bold = True, font_size = font_size, parent=self.canvas.scene)

        self.stats_text4 = scene.visuals.Text('', pos=(self.canvas.size[0]/3.0,  int(font_size*1.33*4+font_size*1.33*5*0.5)),
                                       color='w', bold = True, font_size = font_size, parent=self.canvas.scene)
        self.stats_text5 = scene.visuals.Text('', pos=(self.canvas.size[0]/3.0, int(font_size*1.33*5+font_size*1.33*6*0.5)),
                                       color='w', bold = True, font_size = font_size, parent=self.canvas.scene)
        self.tr = self.scatter.node_transform(self.view)

        # Add a 3D axis to keep us oriented
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)

        # Set up for lasso drawing
        self.line_pos = []
        self.line = scene.visuals.Line(color='white', method='gl',
                                       parent=self.canvas.scene)

        # select
        self.select_flag = False
        self.select_pool = {'1': 'lasso', '2': 'rectangle'}
        self.select_id = '2'  # default as 2
        self.select_origin = (0, 0)

    def event_connect(self, flag):
        cam_events = self.view.camera._viewbox.events
        cam_mouse_event = self.view.camera.viewbox_mouse_event
        if flag:
            cam_events.mouse_move.disconnect(cam_mouse_event)
            cam_events.mouse_press.disconnect(cam_mouse_event)
            cam_events.mouse_release.disconnect(cam_mouse_event)
            cam_events.mouse_wheel.disconnect(cam_mouse_event)
        else:
            cam_events.mouse_move.connect(cam_mouse_event)
            cam_events.mouse_press.connect(cam_mouse_event)
            cam_events.mouse_release.connect(cam_mouse_event)
            cam_events.mouse_wheel.connect(cam_mouse_event)

    def mark_selected(self):
        # Change the color of the selected point
        # print('changing color')
        self.facecolor = copy.deepcopy(self.base_facecolor)
        # print('equal' , self.facecolor==self.base_facecolor)
        self.scatter.set_data(self.data, face_color=self.facecolor,
                              size=self.ptsize)

        for i in self.selected:
            self.facecolor[i] = [1.0, 0.0, 1.0]

        self.scatter.set_data(self.data, face_color=self.facecolor,
                              size=self.ptsize)
        self.scatter.update()

        if self.scene_type in ['depth', 'intensity']:
            if len(self.data[tuple(self.selected)]) > 0 and self.grid.stats_key != None:
                if self.scene_type in ['depth']:
                    stats = self.grid.get_depth_stats(self.data[tuple(self.selected)])#, self.scene_type) 

                if self.scene_type in ['intensity']:
                    stats = self.grid.get_intensity_stats(self.selected)
                
                # add call to get snowdepth here
                # get average x,y,z
                self.stats_text.text = str(f'Avg Gd/IS, Avg Snow- Avg {self.scene_type}: {stats[0]}')
                self.stats_text2.text = str(f'Avg Gd/IS, Avg Snow- Max {self.scene_type}: {stats[1]}')
                self.stats_text3.text = str(f'Avg Gd/IS, Avg Snow- Min {self.scene_type}: {stats[2]}')
                self.stats_text4.text = str(f'Min Gd/IS, Avg Snow- Avg {self.scene_type}: {stats[3]}')
                self.stats_text5.text = str(f'Min Gd/IS, Avg Snow- Max {self.scene_type}: {stats[4]}')


                
            else:
                self.stats_text.text = str(f'Avg Gd/IS, Avg Snow- AVG: n/a')
                self.stats_text2.text = str(f'Avg Gd/IS, Avg Snow- MAX: n/a')
                self.stats_text3.text = str(f'Avg Gd/IS, Avg Snow- MIN: n/a')
                self.stats_text4.text = str(f'Min Gd/IS, Avg Snow- AVG: n/a')
                self.stats_text5.text = str(f'Min Gd/IS, Avg Snow- MAX: n/a')

    def remove_selected_points(self):#, removal_points):
            if len(self.selected) > 0:
                self.data = copy.deepcopy(self.data[tuple(np.invert(self.selected))])
                self.base_facecolor = copy.deepcopy(self.base_facecolor[tuple(np.invert(self.selected))])
                self.facecolor = copy.deepcopy(self.base_facecolor)
                self.scatter.set_data(self.data, face_color=self.facecolor,
                                    size=self.ptsize)
                self.scatter.update()
                print('selected 1', self.selected)
                # self.selected = []
            return self.selected

    def reset_selected(self):
        self.selected = []

    def permanently_mark_selected(self):
        for i in self.selected:
            self.base_facecolor[i] = [1.0, 1.0, 1.0]
        self.scatter.set_data(self.data, face_color=self.base_facecolor,
                              size=self.ptsize)
        self.scatter.update()

    def on_key_press(self, event):
        # Set select_flag and instruction text

        if event.text == '1': #in self.select_pool.keys():
            if self.select_flag:
                if self.select_id == '2':
                    self.select_id = '1'
                    self.text.text = 'In lasso select mode, press 1 to switch to rectangular select'
                else:
                    self.select_id = '2'
                    self.text.text = 'In rectangular select mode, press 1 to switch to lasso select'
                                 

    def on_mouse_press(self, event):
        # Realize picking functionality and set origin mouse pos
        
        if event.button == 1 and self.select_flag:
            self.select_origin = event.pos

    def on_mouse_release(self, event):
        # Identify selected points and mark them

        if event.button == 1 and self.select_flag:

            self.facecolor = self.base_facecolor
            data = self.tr.map(self.data)[:, :2]

            self.selected = []
            select_path = path.Path(self.line_pos, closed=True)
            mask = [select_path.contains_points(data)]

            # if len(self.data[tuple(mask)]) > 0:
            self.selected = mask
            self.mark_selected()

            # Reset lasso
            # TODO: Empty pos input is not allowed for line_visual
            self.line_pos = []
            self.line.set_data(np.array(self.line_pos))
            self.line.update()

            if self.select_id == '2':
                self.select_origin = None

    def on_mouse_move(self, event):
        # Draw lasso/rectangle/ellipse shape with mouse dragging

        if event.button == 1 and event.is_dragging and self.select_flag:
            if self.select_id == '1':
                self.line_pos.append(event.pos)
                self.line.set_data(np.array(self.line_pos))

            if self.select_id == '2':
                width = event.pos[0] - self.select_origin[0]
                height = event.pos[1] - self.select_origin[1]
                center = (width/2. + self.select_origin[0],
                          height/2.+self.select_origin[1], 0)
                self.line_pos = rectangle_vertice(center, height, width)
                self.line.set_data(np.array(self.line_pos))