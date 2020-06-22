# 구글 파이썬 스타일 가이드를 적용해야된다.

import cv2
import threading
import sys
from random import *
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout


class MyMain(QWidget):
    def __init__(self):
        super().__init__()

        self.statusbar = self.statusBar()

        print(self.hasMouseTracking())
        self.setMouseTracking(True)   # True 면, mouse button 안눌러도 , mouse move event 추적함.
        print(self.hasMouseTracking())


        cv2.putText(img, pixel, (self.x[i] + 3, self.y[i] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
        h,w,c = img.shape
        qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.label.setPixmap(pixmap)
        self.show()

    def mouseMoveEvent(self, event):
        txt = "Mouse 위치 ; x={0},y={1}, global={2},{3}".format(event.x(), event.y(), event.globalX(), event.globalY())
        self.statusbar.showMessage(txt)
        print(event.globalX())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyMain()
    sys.exit(app.exec_())