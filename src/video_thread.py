#!/usr/bin/env python3

import numpy as np
import time
import cv2

from PyQt5 import QtWidgets, QtGui, QtCore


class VideoThread(QtCore.QThread):
    """
    Video output running as QThread
    QThread로 실행되는 OpenCV 비디오 출력
    """
    update_pixmap_signal = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, src: str = ""):
        super().__init__()
        self._run_flag = True
        self.cap = None
        self.src = src

    def run(self):
        try:
            time.sleep(0)
            if self.src == "":
                self.cap = cv2.VideoCapture(0)
            else:
                self.cap = cv2.VideoCapture(self.src)

            while self._run_flag:
                ret, cv_img = self.cap.read()
                if ret:
                    self.update_pixmap_signal.emit(cv_img)
                    cv2.waitKey(1)

            # Shut down capture system
            self.cap.release()
            cv2.destroyAllWindows()
            del cv_img

        except cv2.error:
            self.cap.release()
            cv2.destroyAllWindows()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()
