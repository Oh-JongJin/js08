#!/usr/bin/env python3

import numpy as np

import cv2

from PyQt5 import QtWidgets, QtGui, QtCore


class VideoThread(QtCore.QThread):
    update_pixmap_signal = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, src: str = 0):
        super().__init__()
        self._run_flag = True
        self.src = src
        self.img_width = 0
        self.img_height = 0

    def run(self):
        cap = cv2.VideoCapture(self.src)

        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.update_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()
