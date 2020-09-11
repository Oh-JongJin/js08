#!/usr/bin/env python3
"""Connect IP camera and specify target to get dissipation factor

Hanwha and COMMAX IP cameras and images are imported and displayed in real time 
The UI is implemented using the PyQT5 library, and input data can be changed 
or targets can be designated and deleted with a keyboard and mouse

Typical usage example:

    python pyqt_ipcam.py

Keyboard key:
    
    1 : Read Hanhwa camera 
    2 : Read Commax camera
    3 : Read Image

Mouse event:
    
    Left click : Add target
    Right click : Remove recently created target
"""
# QtWidgets은 PyQt5에서 모든 UI 객체를 포함하고 있는 클래스라서 무조건 import
import os
import sys
import threading
import time
import cv2
import pandas as pd
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QWidget, QLabel, QApplication, QLineEdit, QInputDialog


class worker(QThread):

    Videosig = pyqtSignal(QtGui.QImage)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.camname = ""
    # 저장된 영상 목표들을 불러온다 없으면 빈 리스트만 선언
    def get_target(self):
        self.x = []
        self.y = []
        self.dis = []
        if os.path.isfile(f"target/{self.camname}.csv") == True:
            result = pd.read_csv(f"target/{self.camname}.csv")
            self.x = result.x.tolist()
            self.y = result.y.tolist()
            self.dis = result.dis.tolist()
            print("target을 불러옵니다.")

    
    def run(self):
        global img
        # 영상 목표들을 불러오기  
        self.get_target()
        print(self.camname)
        print(self.ADD)
        print(self.isRun)
        if self.camname == "img":
            img = cv2.imread("test.png", cv2.IMREAD_COLOR)
            height, width, ch = img.shape
        else:            
            self.cap = cv2.VideoCapture(self.ADD)
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"video size {width}, {height}")
            # self.label.resize(width, height)

        # 초기 사이즈 값을 저장한다.
        prewidth = width
        preheight = height

        while self.isRun: 
            # camname이 이미지가 아닐 때 cap으로 읽기
            if self.cap.isOpened():
                ret, img = self.cap.read()
                print("이미지를 읽어옵니다.", ret)
                # TODO(성민): 윈도 크기를 작게 조정하는 기능이 작동하지 않습니다.             
                # resize의 fx는 비율로 크기를 조절한다.
                # 의 크기에 따라 영상 크기도 같이 변한다.
                # if prewidth <= self.label.width() or preheight <= self.label.height():
                #     img = cv2.resize(img, dsize=(0, 0), fx=mowidth, fy=moheight, 
                #                         interpolation=cv2.INTER_LINEAR)
                # if prewidth > self.label.width() or preheight > self.label.height():
                #     img = cv2.resize(img, dsize=(0, 0), 
                #             fx=self.label.width()/width, 
                #             fy=self.label.height()/height, 
                #             interpolation=cv2.INTER_AREA)        

            # camname이 이미지가 일 때 imread 메서드로 읽기        
            else:
                img = cv2.imread("test.png", cv2.IMREAD_COLOR)
                # img = cv2.resize(img, dsize=(self.label.width(), self.label.height()))
                ret = 1

            # 이미지를 읽어오면 실행
            if ret:
                # 영상 목표들을 사각형으로 호출 get_target
                if len(self.x) >= 0:
                    try:
                        for i in range(len(self.x)):
                            upper_left = self.x[i] - 5, self.y[i] - 5
                            lower_right = self.x[i] + 5, self.y[i] + 5
                            cv2.rectangle(img, upper_left, lower_right, (0, 255, 0), 1)
                            pixel = str(i+1)
                            text_loc = self.x[i] + 3, self.y[i] - 10
                            cv2.putText(img, str(self.dis[i]) + " km", text_loc, cv2.FONT_HERSHEY_COMPLEX, 
                                        0.5, (0, 0, 255))            
                    except Exception as e:
                        print("error : ", e)
                        pass
                else:
                    pass
                h, w, c=  img.shape

                # 하단 컨텐츠 소스
                # Dark background for the textual contents on the bottom
                subimg = img.copy()
                cv2.rectangle(subimg, (0, h - 100), (w, h), (0, 0, 0), -1)
                img = cv2.addWeighted(img, 0.5, subimg, 0.5, 1)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
                self.qimg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
                self.Videosig.emit(self.qimg)
            else:                
                print("Cannot read frame.")
                break
            self.cap.release()
            # 영상 목표 정보 저장.

        if len(self.x) >= 0:
            for i in range(len(self.x)):
                print(self.x[i], ", ", self.y[i], ", ", self.dis[i])
            col = ["x", "y", "dis"]
            result = pd.DataFrame(columns=col)
            result["x"] = self.x
            result["y"] = self.y
            result["dis"] = self.dis
            result.to_csv(f"target/{self.camname}.csv", mode="w", index=False)
            print("target이 저장되었습니다.")        
        print("Thread end.")


        
# UI를 정의하는 클래스
# 키입력으로 바꿔서 적용하려면 클래스를 만들어서 해야함.
class pyqt_ipcam(QWidget):

    def __init__(self):
        super().__init__()
        # 라벨의 크기에 따라 Widget의 크기를 변경한다. 위젯은 변하지만 영상의 크기는 고정되어 있기때문에 따로 
        # 설정해줘야 한다.
        self.grid = QGridLayout()
        self.label = QLabel()       
        # self.setGeometry(50, 50, 1820, 980) 
        self.showFullScreen()
        self.grid.addWidget(self.label, 0, 0)
        self.grid.setContentsMargins(0, 0, 0, 0)     
        self.setLayout(self.grid)
        self.th = worker(self)
        self.th.Videosig.connect(self.read_start)        
        self.show()
        #마우스 트래킹 감지 False이면 클릭시 이동을 감지
        self.setMouseTracking(False)        
    
    @pyqtSlot(QtGui.QImage)
    def read_start(self, qimg):
        pixmap = QtGui.QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap)

    # 영상을 읽는다
    # Thread로 실행한다.
    def start(self):
        self.th.isRun = True
        # th = threading.Thread(target=self.run)
        # th.start()
        self.th.start() 
        print("started..")
    
    # 영상 읽기를 중단한다.
    def stop(self):
        self.th.isRun = False
        self.th.wait()
        print("stoped..")
        time.sleep(1)

    # 프로그램을 종료한다.
    def onExit(self):
        print("exit")
        self.stop()
        self.close()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_T:
            self.start()
        elif e.key() == Qt.Key_Space:
            self.stop()
        elif e.key() == Qt.Key_Q:
            self.onExit()
        elif e.key() == Qt.Key_F:
            # self.showMaximized()
            self.showFullScreen()
        elif e.key() == Qt.Key_N:
            self.showNormal()
        elif e.key() == Qt.Key_1:
            self.stop()
            self.th.camname = "hanhwa"
            self.th.ADD = "rtsp://nalgaem:zf!w58DN4jCu@192.168.100.115/profile2/media.smp"
            self.start()
        elif e.key() == Qt.Key_2:
            self.stop()
            self.th.camname = "commax"
            self.th.ADD = "rtsp://admin:1234@192.168.100.251:554/1/1"
            self.start()
        elif e.key() == Qt.Key_3:
            self.stop()
            self.th.camname = "img"            
            self.start()
        

    # 마우스 왼쪽 버튼을 누르면 영상 목표를 추가, 오른쪽 버튼은 최근에 추가된 영상 목표를 제거.
    def mousePressEvent(self, e):        
        if e.button() == Qt.LeftButton:
            text, ok = QInputDialog.getText(self, '영상 목표 거리입력', '거리(km)')
            if ok:
                self.dis.append(str(text))
                self.x.append(e.x())
                self.y.append(e.y())
                print("영상 목표 위치:", e.x(), ", ", e.y())
                time.sleep(1)
        elif e.button() == Qt.RightButton:
            if len(self.x) >= 1:
                del self.x[-1]
                del self.y[-1]
                del self.dis[-1]            
                print("영상 목표를 제거했습니다.")       
                time.sleep(1)
            else:
                pass
                print("제거할 영상 목표가 없습니다.")
    def mouseReleaseEvent(self, e):
        return super().mouseReleaseEvent(e)
    
def main():
    app = QApplication(sys.argv)
    ex = pyqt_ipcam()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    
