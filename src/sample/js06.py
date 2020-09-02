#!/usr/bin/env python3
# 
# A sample implementation of a main window for JS-06
# 
# This example illustrates the following techniques:
# * Layout design using Qt Designer
# * Open an image file
# * Open RTSP video source
# *
# Reference: https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1

import sys

import cv2
import numpy as np

from PyQt5 import QtWidgets, QtGui, QtCore 

from main_window import Ui_MainWindow


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
        
        while True:
            ret, cv_img = cap.read()
            if ret:
                self.update_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class Js06MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.video_thread = None

    def setupUi(self, MainWindow:QtWidgets.QMainWindow):
        super().setupUi(MainWindow)

        self.actionImage_File.triggered.connect(self.open_img_file_clicked)
        self.actionCamera_1.triggered.connect(self.open_cam1_clicked)
        self.actionCamera_2.triggered.connect(self.open_cam2_clicked)
        self.actionCamera_3.triggered.connect(self.open_cam3_clicked)

    def closeEvent(self, event):
        print("DEBUG: ", type(event))
        if self.video_thread is not None:
            self.video_thread.stop()
        event.accept()

    def open_img_file_clicked(self):
        if self.video_thread is not None:
            self.video_thread.stop()

        fname = QtWidgets.QFileDialog.getOpenFileName()[0]
        if fname != '':
            cv_img = cv2.imread(fname)
            # convert the image to Qt format
            qt_img = self.convert_cv_qt(cv_img)
            # display it
            self.image_label.setPixmap(qt_img)

    def open_cam1_clicked(self):
        """Connect to webcam"""
        if self.video_thread is not None:
            self.video_thread.stop()

        # create the video capture thread
        self.video_thread = VideoThread(0)
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()

    def open_cam2_clicked(self):
        """Get video from Hanwha PNM-9030V"""
        if self.video_thread is not None:
            self.video_thread.stop()

        # create the video capture thread
        self.video_thread = VideoThread('rtsp://admin:sijung5520@192.168.100.121/profile2/media.smp')
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()

    def open_cam3_clicked(self):
        """Get video from Hanwha XNO-8080R"""
        if self.video_thread is not None:
            self.video_thread.stop()

        # create the video capture thread
        self.video_thread = VideoThread('rtsp://admin:G85^mdPzCXr2@192.168.100.115/profile2/media.smp')
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()

    @QtCore.pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        # width, height = (w // 4, h // 4) if w > 1920 else (w, h)
        display_width, display_height = w // 4, h // 4
        p = convert_to_Qt_format.scaled(display_width, display_height, QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Js06MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
