#!/usr/bin/env python3

import cv2
import threading

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QWidget


class pyqt_ipcam(QWidget):

    def __init__(self):
        super().__init__()
        self.grid = QGridLayout()
        self.label = QLabel()
        self.grid.addWidget(self.label, 0, 0)
        self.setLayout(self.grid)
        self.setGeometry(QtCore.QRect(500, 200, 800, 600))

    def run(self):
        cap = cv2.VideoCapture(0)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.label.resize(width, height)
        prewidth = width
        preheight = height

        while running:
            ret, img = cap.read()
            img = cv2.flip(img, 1)
            if ret:
                mowidth = self.label.width() / width
                moheight = self.label.height() / height
                if prewidth <= self.label.width() or preheight <= self.label.height():
                    img = cv2.resize(img, dsize=(0, 0), fx=mowidth, fy=moheight, interpolation=cv2.INTER_LINEAR)

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, c = img.shape
                qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.label.setPixmap(pixmap)
                prewidth = self.label.width()
                preheight = self.label.height()
            else:
                print("cannot read frame.")
                break
        cap.release()
        print("Thread end.")

    def start(self):
        global running
        running = True
        th = threading.Thread(target=self.run)
        th.start()
        print("started..")

    def onExit(self):
        print("exit")
        self.stop()
        self.close()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_T:
            self.start()
        elif e.key() == QtCore.Qt.Key_Q:
            self.close()


def main():
    import sys
    app = QApplication(sys.argv)
    ex = pyqt_ipcam()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
