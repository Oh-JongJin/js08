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

import cv2
import os
import sys
import time

import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore
from main_window import Ui_MainWindow

from PyQt5 import QtWidgets, QtGui, QtCore

from video_thread import VideoThread
from aws_thread import AwsThread
import inference_tflite

class Js06MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.video_thread = None        
        self.target_x = []
        self.target_y = []
        self.distance = []
        self.camera_name = ""
        self.video_thread = None
        self.crop_imagelist100 = []
        self.aws_thread = AwsThread()
        self.target_process = False

    def setupUi(self, MainWindow:QtWidgets.QMainWindow):
        super().setupUi(MainWindow)

        self.actionImage_File.triggered.connect(self.open_img_file_clicked)
        self.actionCamera_1.triggered.connect(self.open_cam1_clicked)
        self.actionCamera_2.triggered.connect(self.open_cam2_clicked)
        self.actionCamera_3.triggered.connect(self.open_cam3_clicked)
        self.image_label.mousePressEvent = self.getpos  
        self.actionON.triggered.connect(self.aws_clicked)
        self.actionTarget_ON.triggered.connect(self.target_ModeOn)
        self.actionTarget_OFF.triggered.connect(self.target_ModeOff)

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
            self.camera_name = "file_image"
            self.get_target()
            # display it
            self.image_label.setPixmap(qt_img)

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
        if self.video_thread is not None:
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
        if self.video_thread is not None:
            self.save_target()
            self.video_thread.stop()

        self.camera_name = "XNO-8080R"
        # create the video capture thread
        self.video_thread = VideoThread('rtsp://admin:G85^mdPzCXr2@192.168.100.115/profile2/media.smp')
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()        
        self.get_target()


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
        
        self.coordinator()
        self.restoration()
        
        self.label_width = self.image_label.width()
        self.label_height = self.image_label.height()

        # 시간 저장
        epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))

        if epoch[-2:] == "00":
            self.save_image(rgb_image, epoch)

        if self.target_x:           

            for name, x, y, dis in zip(self.target_name, self.target_x, self.target_y, self.distance):         
                # image_y = int((y / (self.label_height - (self.label_height - self.img_height))) * self.img_height)
                upper_left = x - 25, y - 25
                lower_right = x + 25, y + 25
                cv2.rectangle(rgb_image, upper_left, lower_right, (0, 255, 0), 6)
                text_loc = x + 30, y - 35                
                cv2.putText(rgb_image, name[7:]+ ": " + str(dis) + "km", text_loc, cv2.FONT_HERSHEY_COMPLEX, 
                            1.5, (255, 0, 0), 2)
        
        bytes_per_line = ch * self.img_width
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, self.img_width, self.img_height, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.image_label.width(), self.image_label.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        return QtGui.QPixmap.fromImage(p)

    def target_ModeOn(self):
        
        self.target_process = True
        return self.target_process
    
    def target_ModeOff(self):
        
        self.target_process = False
        return self.target_process
    
    # https://stackoverflow.com/questions/3504522/pyqt-get-pixel-position-and-value-when-mouse-click-on-the-image
    # 마우스 컨트롤
    def getpos(self, event):
        if self.video_thread is None:
            return

        if self.target_process is False:
            return

        # 마우스 왼쪽 버튼을 누르면 영상 목표를 추가
        if event.buttons() == QtCore.Qt.LeftButton:
            text, ok = QtWidgets.QInputDialog.getText(self.centralwidget, '타겟거리입력', '거리(km)')

            if ok:
                
                self.distance.append(float(text))
                self.target_x.append(int(event.pos().x() / self.label_width * self.img_width))
                self.target_y.append(int(event.pos().y() / self.label_height * self.img_height))
                self.target_name.append("target_" + str(len(self.target_x)))
                print("영상 목표위치:", self.target_x[-1],", ", self.target_y[-1])
                self.save_target()

        # 오른쪽 버튼을 누르면 최근에 추가된 영상 목표를 제거.
        elif event.buttons() == QtCore.Qt.RightButton:
            if len(self.target_x) >= 1:
                del self.target_name[-1]
                del self.target_x[-1]
                del self.target_y[-1]
                del self.distance[-1]            
                print("영상 목표를 제거했습니다.")
                self.save_target()
            else:
                print("제거할 영상 목표가 없습니다.")

    # 영상 목표를 불러오기
    def get_target(self):
        self.target_name = []
        self.target_x = []
        self.target_y = []
        self.distance = []
        if not os.path.isdir("target") == True:
            os.mkdir("target")
        else:
            pass

        if os.path.isfile(f"target/{self.camera_name}.csv") == True:
            result = pd.read_csv(f"target/{self.camera_name}.csv")
            self.target_name = result.target_name.tolist()
            self.target_x = result.target_x.tolist()
            self.target_y = result.target_y.tolist()
            self.distance = result.distance.tolist()
            self.oxlist = [0 for i in range(len(self.target_x))]
            print("영상 목표를 불러옵니다.")
    
    def save_target(self):
        """영상 목표 정보를 실행된 카메라에 맞춰서 저장한다."""
        if self.target_x:
            col = ["target_name", "target_x", "target_y", "distance", "predict"]
            self.result = pd.DataFrame(columns=col)
            self.result["target_name"] = self.target_name
            self.result["target_x"] = self.target_x
            self.result["target_y"] = self.target_y
            self.result["distance"] = self.distance
            self.result['predict'] = self.oxlist
            self.result.to_csv(f"target/{self.camera_name}.csv", mode="w", index=False)
            self.coordinator()
            self.restoration()            

    def coordinator(self):
        """ 영상 목표의 좌표값을 -1~1 값으로 정규화한다."""
        self.prime_y = [ y / self.img_height for y in self.target_y]
        self.prime_x = [2 * x / self.img_width - 1 for x in self.target_x]
    
    def restoration(self):
        """ 정규화한 값을 다시 복구한다."""
        self.res_x = [self.to_int((x + 1) * self.img_width / 2) for x in self.prime_x]
        self.res_y = [self.to_int(y * self.img_height) for y in self.prime_y]
    
    def to_int(self, num: float):
        """ float형 숫자를 0.5를 더하고 정수형으로 바꿔준다."""
        return int(num + 0.5)      
        
    def save_image(self, image: np.ndarray, epoch: str):
        """ 영상 목표들을 각 폴더에 저장한다."""
        self.crop_imagelist100 = []
        for i in range(len(self.target_x)):
            
            if not(os.path.isdir(f"target/image/100x100/target{i+1}")):
                os.makedirs(os.path.join(f"target/image/100x100/target{i+1}"))
            else:
                pass
        
            if not(os.path.isfile(f"target/image/100x100/target{i+1}/target_{i+1}_{epoch}.jpg")):
                # 모델에 넣을 이미지 추출
                crop_img = image[self.target_y[i] - 50 : self.target_y[i] + 50 , self.target_x[i] - 50 : self.target_x[i] + 50]
                self.crop_imagelist100.append(crop_img)
                # cv로 저장할 때는 bgr 순서로 되어 있기 때문에 rgb로 바꿔줌.
                b, g, r = cv2.split(crop_img)
                # 영상 목표의 각 폴더에 크롭한 이미지 저장
                cv2.imwrite(f"target/image/100x100/target{i+1}/target_{i+1}_{epoch}.jpg", cv2.merge([r, g, b]))
            else:
                pass

        self.get_visiblity()

    def get_visiblity(self):
        """ 크롭한 이미지들을 모델에 돌려 결과를 저장하고 보이는것들 중 가장 먼 거리를 출력한다."""
        self.oxlist = []
        for image in self.crop_imagelist100:
            image = cv2.resize(image, dsize = (224, 224), interpolation = cv2.INTER_LINEAR)
            self.oxlist.append(inference_tflite.inference(image))

        res = [self.distance[x] for x, y in enumerate(self.oxlist) if y == 1]
        visivlity = str(max(res)) + " km"
        print(visivlity)        
        self.save_target()
        self.to_jongjin()
        time.sleep(1)

    def to_jongjin(self):
        """ polar plot에 필요한 값들을 사전형으로 만들어 출력한다."""        
        result_dict = {key:[p_x, distance, ox_value] for key, p_x, distance, ox_value in zip(self.target_name, self.prime_x, self.distance, self.oxlist)}
        print(result_dict)

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

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Js06MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
