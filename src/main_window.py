# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem, QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView


class Ui_MainWindow:
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)

        app_icon = QtGui.QIcon("ui/logo.png")
        MainWindow.setWindowIcon(app_icon)

        width = QtWidgets.QApplication.primaryScreen().size().width()
        height = QtWidgets.QApplication.primaryScreen().size().height()
        MainWindow.resize(width, height)
        MainWindow.showFullScreen()

        MainWindow.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        MainWindow.setMaximumSize(QtCore.QSize(width, height))
        MainWindow.setMouseTracking(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMaximumSize(QtCore.QSize(width, height))
        self.centralwidget.setMouseTracking(False)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.blank_lbl = QtWidgets.QLabel(self.centralwidget)
        self.blank_lbl.setMinimumSize(QtCore.QSize(0, 0))
        self.blank_lbl.setMaximumSize(QtCore.QSize(16777215, 16777215))

        self.scene = QtWidgets.QGraphicsScene()
        self.graphicView = QtWidgets.QGraphicsView(self.scene)
        self.graphicView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.videoWidget = QGraphicsVideoItem()
        self.scene.addItem(self.videoWidget)
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.videoWidget)
        self.verticalLayout.addWidget(self.graphicView)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.webEngineView = QWebView()

        self.horizontalLayout.addWidget(self.webEngineView)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMainWindow.menuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, width, 0.0195 * height))
        self.menubar.setAutoFillBackground(False)
        #self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName("menubar")
        self.menuSource = QtWidgets.QMenu(self.menubar)
        self.menuSource.setObjectName("menuSource")
        self.menuMode = QtWidgets.QMenu(self.menubar)
        self.menuMode.setObjectName("menuMode")
        MainWindow.setMenuBar(self.menubar)
        self.actionImage_File = QtWidgets.QAction(MainWindow)
        self.actionImage_File.setObjectName("actionImage_File")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionInference = QtWidgets.QAction(MainWindow)
        self.actionInference.setCheckable(True)
        self.actionInference.setChecked(False)
        self.actionInference.setObjectName("actionInference")
        self.actionEdit_target = QtWidgets.QAction(MainWindow)
        self.actionEdit_target.setCheckable(True)
        self.actionEdit_target.setObjectName("actionEdit_target")
        self.actionAWS = QtWidgets.QAction(MainWindow)
        self.actionAWS.setCheckable(True)
        self.actionAWS.setObjectName("actionAWS")
        self.actionSaveframe = QtWidgets.QAction(MainWindow)
        self.actionSaveframe.setCheckable(True)
        self.actionSaveframe.setObjectName("actionSaveframe")
        self.menuSource.addAction(self.actionExit)
        self.menuMode.addAction(self.actionEdit_target)
        self.menuMode.addSeparator()
        self.menuMode.addAction(self.actionInference)
        self.menuMode.addAction(self.actionAWS)
        self.menuMode.addAction(self.actionSaveframe)
        self.menubar.addAction(self.menuSource.menuAction())
        self.menubar.addAction(self.menuMode.menuAction())
        self.retranslateUi(MainWindow)
        self.actionExit.triggered.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "JS-06"))
        self.menuSource.setTitle(_translate("MainWindow", "File"))
        self.menuMode.setTitle(_translate("MainWindow", "Mode"))
        self.actionImage_File.setText(_translate("MainWindow", "Image File"))
        self.actionImage_File.setStatusTip(_translate("MainWindow", "Open an image file"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionExit.setStatusTip(_translate("MainWindow", "Exit JS-06"))
        self.actionExit.setShortcut(_translate("MainWindow", "Ctrl+W"))
        self.actionInference.setText(_translate("MainWindow", "Inference"))
        self.actionInference.setShortcut(_translate("MainWindow", "I"))
        self.actionEdit_target.setText(_translate("MainWindow", "Edit_target"))
        self.actionEdit_target.setShortcut(_translate("MainWindow", "E"))
        self.actionAWS.setText(_translate("MainWindow", "AWS Sensor"))
        self.actionAWS.setShortcut(_translate("MainWindow", "A"))
        self.actionSaveframe.setText(_translate("MainWindow", "Save Frame"))
        self.actionSaveframe.setShortcut(_translate("MainWindow", "S"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
