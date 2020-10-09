from button_actions import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import vispy.app
import sys

class Window(QMainWindow):
    # resize = pyqtSignal()
    def __init__(self):
        super(Window, self).__init__()
        # self.setWindowTitle("Lidar Snow Depth Calculator")
        self.initInterface()

    def initInterface(self):

        self.setWindowTitle("Lidar Snow Depth Calculator")

        ##### LEFT PANEL WIDGET
        # Set left layout
        self.left_widget_layout = QVBoxLayout()
        
        self.base_file_button = QPushButton("Choose Base File")
        # self.base_file_button.setText("Choose Base File")
        self.base_file_button.clicked.connect(self.click_base_file_button)

        self.snow_file_button = QPushButton("Choose Snow File")
        # self.snow_file_button.setText("Choose Snow File")
        self.snow_file_button.clicked.connect(self.click_snow_file_button)

        self.run_snowdepth_button = QPushButton("Calculate Snow Depth")
        # self.run_snowdepth_button.setText("Calculate Snow Depth")
        self.run_snowdepth_button.clicked.connect(self.click_snow_depth_button)

        self.run_alignment_button = QPushButton("Run Alignment")
        # self.run_alignment_button.setText("Run Alignment")
        self.run_alignment_button.clicked.connect(self.click_run_alignment_button)
        
        self.left_widget_layout.addWidget(self.base_file_button)
        self.left_widget_layout.addWidget(self.snow_file_button)
        self.left_widget_layout.addWidget(self.run_snowdepth_button)
        self.left_widget_layout.addWidget(self.run_alignment_button)

        # Make left widget and add the left layout
        self.left_widget = QWidget()
        self.left_widget.setLayout(self.left_widget_layout)

        ##### RIGHT PLOT WIDGET
        # Create Tab widget for plots
        self.plot_widgets = QTabWidget()
        self.plot_widgets.tabBar().setObjectName("mainTab")

        ##### RIGHT TERMINAL WIDGET
        # TODO: Create Terminal Widget
        self.message_window = QTextBrowser()
        self.message_window.setObjectName('Message Window')


        ##### RIGHT LAYOUT AND PARENT WIDGET
        # Set right window layout
        self.right_layout = QVBoxLayout()
        # Add right window and terminal widget to right widget
        self.right_layout.addWidget(self.plot_widgets)
        self.right_layout.addWidget(self.message_window)

        # RIGHT WIDGET
        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)

        # MAIN WIDGET
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.left_widget)
        self.main_layout.addWidget(self.right_widget)
        # MAIN WIDGET
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.main_widget)

        # Set Sizing
        self.message_window.setFixedHeight(int(self.right_widget.height()/4))
        self.left_widget.setFixedWidth(int(self.height()/4))
    
    # def resizeEvent(self, event):
    #     self.resize.emit()
        
    # def resize_widgets(self):
    #     self.message_window.setFixedHeight(int(self.right_widget.height()/4))
    #     self.left_widget.setFixedWidth(int(self.window.height()/4))
        
    def update(self):
        pass


    def click_base_file_button(self):
        self.base_file_path = get_file()
        self.message_window.append(str(self.base_file_path[0]))

    def click_snow_file_button(self):
        self.snow_file_path = get_file()
        self.message_window.append(str(self.snow_file_path[0]))

    def click_snow_depth_button(self):
        self.message_window.append(str(run_snowdepth()))
        # print("Calculate the depth")

    def click_run_alignment_button(self):
        print("Calculate the depth")

class Canvas(vispy.app.Canvas):
    # resize = pyqtSignal()
    def __init__(self):
        super(Canvas, self).__init__()
        # self.resize.connect(self.resize_widgets())
        self.window = Window()
        
    


def canvas():
    canvas = Canvas()
    canvas.window.show()
    vispy.app.run()

canvas()