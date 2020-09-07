<<<<<<< HEAD
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(375, 458)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.image_label = QtWidgets.QLabel(self.centralwidget)
        self.image_label.setText("")
        self.image_label.setObjectName("image_label")
        self.verticalLayout.addWidget(self.image_label)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 375, 21))
        self.menubar.setObjectName("menubar")
        self.menuSource = QtWidgets.QMenu(self.menubar)
        self.menuSource.setObjectName("menuSource")
        self.menuSensor = QtWidgets.QMenu(self.menubar)
        self.menuSensor.setObjectName("menuSensor")
        self.menuAWS = QtWidgets.QMenu(self.menuSensor)
        self.menuAWS.setObjectName("menuAWS")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionImage_File = QtWidgets.QAction(MainWindow)
        self.actionImage_File.setObjectName("actionImage_File")
        self.actionCamera_1 = QtWidgets.QAction(MainWindow)
        self.actionCamera_1.setObjectName("actionCamera_1")
        self.actionCamera_2 = QtWidgets.QAction(MainWindow)
        self.actionCamera_2.setObjectName("actionCamera_2")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionCamera_3 = QtWidgets.QAction(MainWindow)
        self.actionCamera_3.setObjectName("actionCamera_3")
        self.actionON = QtWidgets.QAction(MainWindow)
        self.actionON.setCheckable(True)
        self.actionON.setChecked(False)
        self.actionON.setObjectName("actionON")
        self.actionPolar_Plot = QtWidgets.QAction(MainWindow)
        self.actionPolar_Plot.setObjectName("actionPolar_Plot")
        self.menuSource.addAction(self.actionImage_File)
        self.menuSource.addAction(self.actionCamera_1)
        self.menuSource.addAction(self.actionCamera_2)
        self.menuSource.addAction(self.actionCamera_3)
        self.menuSource.addAction(self.actionExit)
        self.menuAWS.addAction(self.actionON)
        self.menuSensor.addAction(self.menuAWS.menuAction())
        self.menuView.addAction(self.actionPolar_Plot)
        self.menubar.addAction(self.menuSource.menuAction())
        self.menubar.addAction(self.menuSensor.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(MainWindow)
        self.actionExit.triggered.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "JS-06"))
        self.menuSource.setTitle(_translate("MainWindow", "File"))
        self.menuSensor.setTitle(_translate("MainWindow", "Sensor"))
        self.menuAWS.setTitle(_translate("MainWindow", "AWS"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.actionImage_File.setText(_translate("MainWindow", "Image File"))
        self.actionImage_File.setStatusTip(_translate("MainWindow", "Open an image file"))
        self.actionCamera_1.setText(_translate("MainWindow", "Camera 1"))
        self.actionCamera_1.setStatusTip(_translate("MainWindow", "Get video from webcam"))
        self.actionCamera_2.setText(_translate("MainWindow", "Camera 2"))
        self.actionCamera_2.setStatusTip(_translate("MainWindow", "Get video from Hanwha PNM-9030V"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionExit.setStatusTip(_translate("MainWindow", "Exit JS-06"))
        self.actionExit.setShortcut(_translate("MainWindow", "Ctrl+W"))
        self.actionCamera_3.setText(_translate("MainWindow", "Camera 3"))
        self.actionCamera_3.setStatusTip(_translate("MainWindow", "Get video from Hanwha XNO-8080R"))
        self.actionON.setText(_translate("MainWindow", "ON"))
        self.actionON.setStatusTip(_translate("MainWindow", "AWS Sensor Start"))
        self.actionPolar_Plot.setText(_translate("MainWindow", "Polar Plot"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

=======
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(480, 375)
        MainWindow.setMouseTracking(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMouseTracking(False)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.image_label = QtWidgets.QLabel(self.centralwidget)
        self.image_label.setMinimumSize(QtCore.QSize(1, 1))
        self.image_label.setMouseTracking(False)
        self.image_label.setText("")
        self.image_label.setObjectName("image_label")
        self.verticalLayout.addWidget(self.image_label)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 480, 21))
        self.menubar.setObjectName("menubar")
        self.menuSource = QtWidgets.QMenu(self.menubar)
        self.menuSource.setObjectName("menuSource")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionImage_File = QtWidgets.QAction(MainWindow)
        self.actionImage_File.setObjectName("actionImage_File")
        self.actionCamera_1 = QtWidgets.QAction(MainWindow)
        self.actionCamera_1.setObjectName("actionCamera_1")
        self.actionCamera_2 = QtWidgets.QAction(MainWindow)
        self.actionCamera_2.setObjectName("actionCamera_2")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionCamera_3 = QtWidgets.QAction(MainWindow)
        self.actionCamera_3.setObjectName("actionCamera_3")
        self.menuSource.addAction(self.actionImage_File)
        self.menuSource.addAction(self.actionCamera_1)
        self.menuSource.addAction(self.actionCamera_2)
        self.menuSource.addAction(self.actionCamera_3)
        self.menuSource.addAction(self.actionExit)
        self.menubar.addAction(self.menuSource.menuAction())

        self.retranslateUi(MainWindow)
        self.actionExit.triggered.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "JS-06"))
        self.menuSource.setTitle(_translate("MainWindow", "File"))
        self.actionImage_File.setText(_translate("MainWindow", "Image File"))
        self.actionImage_File.setStatusTip(_translate("MainWindow", "Open an image file"))
        self.actionCamera_1.setText(_translate("MainWindow", "Camera 1"))
        self.actionCamera_1.setStatusTip(_translate("MainWindow", "Get video from webcam"))
        self.actionCamera_2.setText(_translate("MainWindow", "Camera 2"))
        self.actionCamera_2.setStatusTip(_translate("MainWindow", "Get video from Hanwha PNM-9030V"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionExit.setStatusTip(_translate("MainWindow", "Exit JS-06"))
        self.actionExit.setShortcut(_translate("MainWindow", "Ctrl+W"))
        self.actionCamera_3.setText(_translate("MainWindow", "Camera 3"))
        self.actionCamera_3.setStatusTip(_translate("MainWindow", "Get video from Hanwha XNO-8080R"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
>>>>>>> d7f1e3e... sample안에 파일 이동
