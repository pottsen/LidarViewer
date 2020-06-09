from PyQt5.QtWidgets import *

class Button(QPushButton):
    def __init__(self, window, name):
        super(Button, self).__init__(window)
        self.setText(name)

    def open_file(self):
        pass

    def save_file(self):
        pass

"""
or just have button methods
"""

def get_file():
    return QFileDialog.getOpenFileName()

def run_snowdepth():
    return "Calculating Snow Depth"



