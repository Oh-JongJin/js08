#!/usr/bin/env python3
# 
# Main window of JS-06
#

import cv2
import os
import sys
import time

import numpy as np
import pandas as pd

from PyQt5 import QtWidgets, QtGui, QtCore

from aws_thread import AwsThread
from video_thread import VideoThread

from main_window import Ui_MainWindow


class Js06MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.video_thread = None
        self.aws_thread = AwsThread()

        self.x = []
        self.y = []
        self.distance = []

        self.camera_name = ""

    def setupUi(self, MainWindow: QtWidgets.QMainWindow):
        super().setupUi(MainWindow)

        self.actionImage_File.triggered.connect(self.open_img_file_clicked)
        self.actionCamera_1.triggered.connect(self.open_cam1_clicked)
        self.actionCamera_2.triggered.connect(self.open_cam2_clicked)
        self.actionCamera_3.triggered.connect(self.open_cam3_clicked)
        self.image_label.mousePressEvent = self.getpos
        # TODO(Kyungwon): self.actionON should use a more precise name.
        self.actionON.triggered.connect(self.aws_clicked)
        # self.actionPolar_Plot.triggered.connect(self.polar_clicked)

    def closeEvent(self, event):
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

    # TODO(Kyungwon): The image should be flipped left and right.
    def open_cam1_clicked(self):
        """Connect to webcam"""
        if self.video_thread is not None:
            self.save_target()
            self.video_thread.stop()

        self.camera_name = "webcam"
        self.get_target()
        # create the video capture thread
        self.video_thread = VideoThread(0)
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()

    def open_cam2_clicked(self):
        """Get video from Hanwha PNM-9030V"""
        if self.video_thread:
            self.save_target()
            self.video_thread.stop()            

        self.camera_name = "PNM-9030V"
        self.get_target()
        # create the video capture thread
        self.video_thread = VideoThread('rtsp://admin:sijung5520@192.168.100.121/profile2/media.smp')
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()

    def open_cam3_clicked(self):
        """Get video from Hanwha XNO-8080R"""
        if self.video_thread:
            self.save_target()
            self.video_thread.stop()

        self.camera_name = "XNO-8080R"
        self.get_target()
        # create the video capture thread
        self.video_thread = VideoThread('rtsp://admin:G85^mdPzCXr2@192.168.100.115/profile2/media.smp')
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()

    def aws_clicked(self):
        """Start saving AWS sensor value at InfluxDB"""

        if self.actionON.isChecked():   # True
            if not self.aws_thread.run_flag:
                print("AWS Thread Start.")
                self.aws_thread.run_flag = True
                self.aws_thread.start()

        elif not self.actionON.isChecked():     # False
            if self.aws_thread.run_flag:
                print("AWS Thread Stop")
                self.aws_thread.run_flag = False

    # TODO(Kyungwon): Wrong implementation!
    def polar_clicked(self):
        """Print Polar Plot"""
        # self.plt_window = PolarPlotWindow()
        # self.plt_window.setupUI(MainWindow)
        # MainWindow.show()
        pass

    # function decorator does not work properly.
    # https://stackoverflow.com/questions/62272988/typeerror-connect-failed-between-videothread-change-pixmap-signalnumpy-ndarr
    # @QtCore.pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        self.img_height, self.img_width, ch = rgb_image.shape
        
        self.label_width = self.image_label.width()
        self.label_height = self.image_label.height()

        if self.x:
            for x, y, dist in zip(self.x, self.y, self.distance):
                t_x = int((x / (self.label_width - (self.label_width - self.img_width))) * self.img_width)
                t_y = int((y / (self.label_height - (self.label_height - self.img_height))) * self.img_height)
                upper_left = t_x - 10, t_y - 10
                lower_right = t_x + 10, t_y + 10
                cv2.rectangle(rgb_image, upper_left, lower_right, (0, 255, 0), 1)
                # pixel = str(i+1)
                text_loc = t_x + 5, t_y - 15
                cv2.putText(rgb_image, str(dist) + " km", text_loc, cv2.FONT_HERSHEY_COMPLEX, 
                            1, (255, 0, 0), 1)

        bytes_per_line = ch * self.img_width
        convert_to_qt_format = QtGui.QImage(rgb_image.data, self.img_width, self.img_height, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_qt_format.scaled(self.image_label.width(), self.image_label.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        return QtGui.QPixmap.fromImage(p)
    
    def getpos(self, event):
        """마우스 컨트롤

        Referenced from 
        https://stackoverflow.com/questions/3504522/pyqt-get-pixel-position-and-value-when-mouse-click-on-the-image
        """
        if self.video_thread is None:
            return

        # 마우스 왼쪽 버튼을 누르면 영상 목표를 추가
        if event.buttons() == QtCore.Qt.LeftButton:
            text, ok = QtWidgets.QInputDialog.getText(self.centralwidget, '타겟거리입력', '거리(km)')

            if ok:
                self.dis.append(str(text))
                # Label의 크기와 카메라 원본 이미지 해상도의 차이를 고려해 계산한다. 약 3.175배
                self.x.append(event.pos().x())
                self.y.append(event.pos().y())
                print("영상 목표위치:", event.pos().x(),", ", event.pos().y())

        # 오른쪽 버튼을 누르면 최근에 추가된 영상 목표를 제거.
        elif event.buttons() == QtCore.Qt.RightButton:
            if len(self.x) >= 1:
                del self.x[-1]
                del self.y[-1]
                del self.distance[-1]            
                print("영상 목표를 제거했습니다.")
            else:
                print("제거할 영상 목표가 없습니다.")


    def get_target(self):
        """영상 목표를 불러오기"""

        self.x = []
        self.y = []
        self.distance = []
        if os.path.isdir("target") is not True:
            os.mkdir("target")
        else:
            pass

        if os.path.isfile(f"target/{self.camera_name}.csv") == True:
            result = pd.read_csv(f"target/{self.camera_name}.csv")
            self.x = result.x.tolist()
            self.y = result.y.tolist()
            self.distance = result.dis.tolist()
            print("영상 목표를 불러옵니다.")

    def save_target(self):
        """종료될 때 영상 목표 정보를 실행된 카메라에 맞춰서 저장"""

        if self.x:
            for x, y, distance in zip(self.x, self.y, self.distance):
                print(f"{x}, {y}, {distance}")
            col = ["x", "y", "distance"]
            result = pd.DataFrame(columns=col)
            result["x"] = self.x
            result["y"] = self.y
            result["distance"] = self.distance
            # TODO(Kyungwon): The path should be concatenated using os.path.join.
            result.to_csv(f"target/{self.camera_name}.csv", mode="w", index=False)
            print("영상 목표가 저장되었습니다.")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Js06MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
