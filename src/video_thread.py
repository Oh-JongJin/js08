# !/usr/bin/env python3
#
# Copyright 2020-21 Sijung Co., Ltd.
# Authors:
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import numpy as np
import time
import cv2

from PyQt5 import QtWidgets, QtGui, QtCore


class VideoThread(QtCore.QThread):
    """Video output running as QThread"""
    update_pixmap_signal = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, src: str = ""):
        super().__init__()
        self._run_flag = True
        self.cap = None
        self.src = src
    # end of __init__

    def run(self):
        try:
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
    # end of run

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()
    # end of stop


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = VideoThread()
    sys.exit(app.exec_())

# end of video_thread.py
