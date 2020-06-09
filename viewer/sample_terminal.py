from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np

#from Distances import radial_distance
def radial_distance(body1, body2, utc, ref, abcorr, obs):
    x_1 = 1
    x_2 = 4
    y_1 = 5
    y_2 = 2
    z_1 = 7
    z_2 = 6

    d_rad = np.sqrt((x_2 - x_1)**2.0 + (y_2 - y_1)**2.0 + (z_2 - z_1)**2.0)

    return d_rad

class Ui_window1(object):
    def setupUi(self, window1):
        window1.setObjectName("window1")
        window1.resize(485, 530) # 820 530
        self.centralwidget = QtWidgets.QWidget(window1)
        self.centralwidget.setObjectName("centralwidget")
        window1.setCentralWidget(self.centralwidget)

        self.groupBox_2 = QtWidgets.QGroupBox("groupBox_2", self.centralwidget)

        self.output_rd = QtWidgets.QTextBrowser(self.groupBox_2)
        self.output_rd.setGeometry(QtCore.QRect(10, 90, 331, 111))
        self.output_rd.setObjectName("output_rd")



        self.retranslateUi(window1)

        QtCore.QMetaObject.connectSlotsByName(window1)        

    def retranslateUi(self, window1):
            _translate = QtCore.QCoreApplication.translate
            window1.setWindowTitle(_translate("window1", "GUI"))


    def rad_distance(self):
        time_rd = np.asarray([1, 2])         # ? (self.get_time_rd())

        body1, body2 = ['EARTH', 'SUN']

        rad_dis = radial_distance(body1, body2, time_rd, 'HCI', 'NONE', 'SUN')

#        self.output_rd.setText(rad_dis)
        self.output_rd.append(str(rad_dis))                                     # + str


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window1 = QtWidgets.QMainWindow()
    ui = Ui_window1()
    ui.setupUi(window1)

    ui.rad_distance() 
    ui.rad_distance()                                                          # +

    window1.show()
    sys.exit(app.exec_())