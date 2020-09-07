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

import os
import sys
import time
import cv2
import numpy as np
import pandas as pd
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
        
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret :
                self.update_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.img_widthait()

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
        self.image_label.mousePressEvent = self.getpos  

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
            self.save_target()
            self.video_thread.stop()

        self.camname = "webcam"
        self.get_target()
        # create the video capture thread
        self.video_thread = VideoThread(0)
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()        

    def open_cam2_clicked(self):
        """Get video from Hanwha PNM-9030V"""
        if self.video_thread is not None:
            self.save_target()
            self.video_thread.stop()            

        self.camname = "PNM-9030V"
        self.get_target()
        # create the video capture thread
        self.video_thread = VideoThread('rtsp://admin:sijung5520@192.168.100.121/profile2/media.smp')
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()

    def open_cam3_clicked(self):
        """Get video from Hanwha XNO-8080R"""
        if self.video_thread is not None:
            self.save_target()
            self.video_thread.stop()

        self.camname = "XNO-8080R"
        self.get_target()
        # create the video capture thread
        self.video_thread = VideoThread('rtsp://admin:G85^mdPzCXr2@192.168.100.115/profile2/media.smp')
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()

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

        if len(self.x):
            for i in range(len(self.x)):
                t_x = int((self.x[i] / (self.label_width - (self.label_width - self.img_width))) * self.img_width)
                t_y = int((self.y[i] / (self.label_height - (self.label_height - self.img_height))) * self.img_height)
                upper_left = t_x - 10, t_y - 10
                lower_right = t_x + 10, t_y + 10
                cv2.rectangle(rgb_image, upper_left, lower_right, (0, 255, 0), 1)
                pixel = str(i+1)
                text_loc = t_x + 5, t_y - 15
                cv2.putText(rgb_image, str(self.dis[i]) + " km", text_loc, cv2.FONT_HERSHEY_COMPLEX, 
                            1, (255, 0, 0), 1)        

        
        bytes_per_line = ch * self.img_width
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, self.img_width, self.img_height, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.image_label.width(), self.image_label.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        
        return QtGui.QPixmap.fromImage(p)
    
    # https://stackoverflow.com/questions/3504522/pyqt-get-pixel-position-and-value-when-mouse-click-on-the-image
    # 마우스 컨트롤
    def getpos(self, e):
        if self.video_thread is not None :
            # 마우스 왼쪽 버튼을 누르면 영상 목표를 추가
            if e.buttons() == QtCore.Qt.LeftButton:
                text, ok = QtWidgets.QInputDialog.getText(self.centralwidget, '타겟거리입력', '거리(km)')

                if ok:
                    self.dis.append(str(text))
                    # Label의 크기와 카메라 원본 이미지 해상도의 차이를 고려해 계산한다. 약 3.175배
                    self.x.append(e.pos().x())
                    self.y.append(e.pos().y())
                    print("영상 목표위치:", e.pos().x(),", ", e.pos().y())

            # 오른쪽 버튼을 누르면 최근에 추가된 영상 목표를 제거.
            elif e.buttons() == QtCore.Qt.RightButton:
                if len(self.x) >= 1:
                    del self.x[-1]
                    del self.y[-1]
                    del self.dis[-1]            
                    print("영상 목표를 제거했습니다.")
                else:
                    print("제거할 영상 목표가 없습니다.")
        else:
            pass

    # 영상 목표를 불러오기
    def get_target(self):
        self.x = []
        self.y = []
        self.dis = []
        if not os.path.isdir("target") == True:
            os.mkdir("target")
        else:
            pass

        if os.path.isfile(f"target/{self.camname}.csv") == True:
            result = pd.read_csv(f"target/{self.camname}.csv")
            self.x = result.x.tolist()
            self.y = result.y.tolist()
            self.dis = result.dis.tolist()
            print("영상 목표를 불러옵니다.")
    
    def save_target(self):
        # 종료될 때 영상 목표 정보를 실행된 카메라에 맞춰서 저장
        if len(self.x) >= 0:
            for i in range(len(self.x)):
                print(self.x[i], ", ", self.y[i], ", ", self.dis[i])
            col = ["x","y","dis"]
            result = pd.DataFrame(columns=col)
            result["x"] = self.x
            result["y"] = self.y
            result["dis"] = self.dis
            result.to_csv(f"target/{self.camname}.csv", mode="w", index=False)
            print("영상 목표가 저장되었습니다.")

    # def coordinate(self, w, h):

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Js06MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
