from PyQt5.QtWidgets import *
import vispy.app
import sys

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

    def initUI(self):
        self.setWindowTitle("Lidar Snow Depth Calculator")
        self.canvas = vispy.app.Canvas() 
        
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QVBoxLayout())

        self.base_file_button = QPushButton(self)
        self.base_file_button.setText("Choose Base File")
        self.base_file_button.clicked.connect(self.click_base_file_button)

        self.snow_file_button = QPushButton(self)
        self.snow_file_button.setText("Choose Snow File")
        self.snow_file_button.clicked.connect(self.click_snow_file_button)

        self.run_snowdepth_button = QPushButton(self)
        self.run_snowdepth_button.setText("Calculate Snow Depth")
        self.run_snowdepth_button.clicked.connect(self.click_snow_depth_button)

        self.widget.layout().addWidget(self.canvas.native)
        self.widget.layout().addWidget(self.base_file_button)
        self.widget.layout().addWidget(self.snow_file_button)
        self.widget.layout().addWidget(self.run_snowdepth_button)

    def click_base_file_button(self):
        print("Add base file")

    def click_snow_file_button(self):
        print("Add snow file")

    def click_snow_depth_button(self):
        print("Calculate the depth")



def window():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
    vispy.app.run()

window()