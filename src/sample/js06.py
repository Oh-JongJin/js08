#!/usr/bin/env python3
# 
# A sample implementation of a main window for JS-06
# 
# This example illustrates the following techniques:
# * Layout design using Qt Designer
# * 
# Reference: https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1

import sys

import cv2
from PyQt5 import QtWidgets, QtGui, QtCore 

from main_window import Ui_MainWindow

class Js06MainWindow(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)

        self.actionImage_File.triggered.connect(self.open_img_file_clicked)

    def open_img_file_clicked(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', './')
        # if fname is not None: 
        #     cv_img = cv2.imread(fname)
        #     # convert the image to Qt format
        #     qt_img = self.convert_cv_qt(cv_img)
        #     # display it
        #     self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        width, height = (w // 4, h // 4) if w > 1920 else (w, h)
        p = convert_to_Qt_format.scaled(width, height, QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Js06MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
