import window as SDW
import ICP_window as AlgnW

class Window(QMainWindow):
    # resize = pyqtSignal()
    def __init__(self):
        super(Window, self).__init__()
        # self.setWindowTitle("Lidar Snow Depth Calculator")
        self.initInterface()

    def initInterface(self):
        self.snow_depth_window = SDW.Window()
        self.alignment_window = AlgnW.Window()

        self.window_widgets = QTabWidget()
        self.window_widgets.addTab(self.alignment_window, "Alignment")
        self.window_widgets.addTab(self.snow_depth_window, "Snow Depth")
        self.setCentralWidget(self.window_widgets)
