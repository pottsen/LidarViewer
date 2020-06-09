from button_actions import *
from PyQt5.QtWidgets import *
import vispy.app
import sys

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        # self.setWindowTitle("Lidar Snow Depth Calculator")

class Canvas(vispy.app.Canvas):
    def __init__(self):
        super(Canvas, self).__init__()
        self.initInterface()
        
    def initInterface(self):
        self.window = Window()
        self.window.setWindowTitle("Lidar Snow Depth Calculator")

        self.widget = QWidget()
        self.window.setCentralWidget(self.widget)
        self.widget.setLayout(QVBoxLayout())

        self.base_file_button = QPushButton(self.window)
        self.base_file_button.setText("Choose Base File")
        self.base_file_button.clicked.connect(self.click_base_file_button)

        self.snow_file_button = QPushButton(self.window)
        self.snow_file_button.setText("Choose Snow File")
        self.snow_file_button.clicked.connect(self.click_snow_file_button)

        self.run_snowdepth_button = QPushButton(self.window)
        self.run_snowdepth_button.setText("Calculate Snow Depth")
        self.run_snowdepth_button.clicked.connect(self.click_snow_depth_button)

        self.run_alignment_button = QPushButton(self.window)
        self.run_alignment_button.setText("Run Alignment")
        self.run_alignment_button.clicked.connect(self.click_run_alignment_button)

        self.widget.layout().addWidget(self.native)
        self.widget.layout().addWidget(self.base_file_button)
        self.widget.layout().addWidget(self.snow_file_button)
        self.widget.layout().addWidget(self.run_snowdepth_button)
        self.widget.layout().addWidget(self.run_alignment_button)

    def update(self):
        pass


    def click_base_file_button(self):
        self.base_file_path = get_file()
        print(self.base_file_path[0])

    def click_snow_file_button(self):
        self.snow_file_path = get_file()
        print(self.snow_file_path[0])

    def click_snow_depth_button(self):
        print("Calculate the depth")

    def click_run_alignment_button(self):
        print("Calculate the depth")


def canvas():
    canvas = Canvas()
    canvas.window.show()
    vispy.app.run()

canvas()