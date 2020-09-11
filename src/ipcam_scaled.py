#!/usr/bin/env python3

"""Window resize test script
Develop real-time responsive UI that changes according to the user's platform.
You can change the window size through PyQt's GridLayout.
When the window is resized, we resize the widgets in it.
"""

""" 창 크기 변경 테스트 스크립트
사용자의 플랫폼에 따라 변하는 실시간 반응형 UI를 개발한다.
PyQt의 GridLayout을 통해 윈도우의 크기를 변경할 수 있다. 
우리는 윈도우의 크기가 변할 때 그 안에 위젯의 크기를 같이 조정한다.

2020.08.31: 위젯인 Label의 크기에 따라 cv2.resize로 이미지 크기를 조절했지만 용량 초과로 인해 강제 종료되는 에러가 발생한다.
2020.09.01: Label의 함수와 resizeEvent를 재정의하여 이미지 크기를 자유자재로 조절이 가능하다. 하지만 09.15일까지 시연해야되기 때문에 우선순위에 따라 잠시 보류하기로 한다.

"""
# QtWidgets은 PyQT5에서 모든 UI 객체를 포함하고 있는 클래스라서 무조건 import
import os
import sys
import threading
import time
import cv2
import pandas as pd
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QWidget, QLabel, QApplication, QLineEdit, QInputDialog, QFormLayout

# UI를 정의하는 클래스
# 키, 마우스 입력을 받으려면 QWidget 클래스를 상속 받아야 한다.
class pyqt_ipcam(QWidget):    

    def __init__(self):
        super().__init__()
        # label의 크기에 따라 Widget의 크기를 변경한다. 위젯은 변하지만 영상의 크기는 고정되어 있기 때문에 따로 
        # 설정해줘야 한다.
        self.grid = QGridLayout()
        self.label = QLabel()
        # setMinimumSize 설정해야 label이 작아질 수 있다. 설정안하면 이미지를 불러올 때가 최솟값으로 업데이트 된다.
        self.label.setMinimumSize(5,5)
        self.showFullScreen()
        # label의 크기에 따라 안에 이미지의 크기를 변경한다.
        self.label.setScaledContents(True)
        self.grid.addWidget(self.label, 0, 0)
        self.grid.setContentsMargins(0, 0, 0, 0)     
        self.setLayout(self.grid)
        self.show()
        self.prewidth = 1280
        self.preheight = 800

    def run(self):
        self.cap = cv2.VideoCapture(self.ADD)
        # 초기 사이즈 값을 저장한다.        
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        while running:            
            ret, img = self.cap.read()
            h, w, c=  img.shape
            if ret:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
                qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)                
                pixmap = QtGui.QPixmap.fromImage(qImg)
                # QPixmap의 크기를 종횡비(KeepAspectRatio)를 유지하고 이중 선형 필터링을(SmoothTransformation) 사용하여 변환된다. 
                pixmap = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label.setPixmap(pixmap)
                cv2.waitKey(0)
            else:                
                print("Cannot read frame.")
                break
        self.cap.release()
    
    # QWidget Layout의 사이즈가 변환될 때 호출되는 메서드
    # label 위젯의 크기를 변환하기 위해 재정의
    def resizeEvent(self, event):
        print(self.width(), ", ", self.height())
        self.label.resize(self.width(), self.height())       

    # 영상을 읽는다
    # Thread로 실행한다.
    def start(self):
        global running
        running = True
        self.camname = "hanhwa"
        self.ADD = "rtsp://admin:sijung5520@192.168.100.121/profile2/media.smp"
        th = threading.Thread(target=self.run)
        th.start()                       
        print("started..")

    # 영상 읽기를 중단한다.
    def stop(self):
        global running        
        running = False
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
            self.prewidth = self.width()
            self.preheight = self.height()     
            self.showFullScreen()
        elif e.key() == Qt.Key_N:
            self.stop()
            self.showNormal()            
            self.setGeometry(50, 50, self.prewidth, self.preheight)
            self.label.resize(self.prewidth, self.preheight)
def main():
    app = QApplication(sys.argv)
    ex = pyqt_ipcam()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
