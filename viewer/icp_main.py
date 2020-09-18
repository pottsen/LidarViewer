from ICP_window import Window
import vispy.app
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

def main():
    # canvas = Canvas()
    # canvas.window.show()
    # vispy.app.run()
    
    app = QApplication(sys.argv)

    window = Window()
    window.show() # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec_()

if __name__ == '__main__':
    main()
