from PyQt5.QtWidgets import *
import vispy.app
import sys


def click_base_file_button():
    print("Add base file")

def click_snow_file_button():
    print("Add snow file")

def click_snow_depth_button():
    print("Calculate the depth")


def canvas():
    canvas = vispy.app.Canvas()
    window = QMainWindow()
    window.setWindowTitle("Lidar Snow Depth Calculator")

    # label = QLabel(window)
    # label.setText("Lidar Snow Depth Calculator")

    widget = QWidget()
    window.setCentralWidget(widget)
    widget.setLayout(QVBoxLayout())

    base_file_button = QPushButton(window)
    base_file_button.setText("Choose Base File")
    base_file_button.clicked.connect(click_base_file_button)

    snow_file_button = QPushButton(window)
    snow_file_button.setText("Choose Snow File")
    snow_file_button.clicked.connect(click_snow_file_button)

    # snow_file_button = QPushButton("Choose Snow File")
    # run_snowdepth_button =  QPushButton("Calculate Snow Depth")


    widget.layout().addWidget(canvas.native)
    widget.layout().addWidget(base_file_button)
    widget.layout().addWidget(snow_file_button)
    # widget.layout().addWidget(run_snowdepth_button)
    window.show()
    vispy.app.run()

canvas()