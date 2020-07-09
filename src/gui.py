#!/usr/bin/env python3

"""JS-06 그래픽 사용자 인터페이스

PyQt의 QLabel 위젯 안에 OpenCV의 영상을 보여준다. 소산계수 추정용 타켓의 위치를 사각형으로 표시한다.
하단 영역에 센서에서 수집한 데이터 등을 표시한다.

Required packages: python3-opencv, python3-pyqt5

Typical usage example: 

  python3 gui.py

"""
import glob
import os
import random
import sys
import time

import cv2
import pandas as pd
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
import threading

import rpi_image_get_rgb

fps = 5
scale = 3
path = "images/2020070810/"

class pyqt_ipcam(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 50, 750, 600)        
        self.grid = QGridLayout()
        self.label1 = QLabel()
        self.grid.addWidget(self.label1, 0, 0)
        self.setLayout(self.grid)
        self.show()        
        
    # Read image   
    def run(self):     
        self.get_target()        
        x = [i // scale for i in self.x]
        y = [i // scale for i in self.y]
        while running:
            img = cv2.imread(glob.glob(f"{path}*_{self.camnumber}.png")[0], cv2.IMREAD_COLOR)            
            h, w, c= img.shape
            dim = w // scale, h // scale
            self.img = img
            img = cv2.resize(img, None, fx=1/scale, fy=1/scale, interpolation=cv2.INTER_AREA)
            h, w, c = img.shape
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            for i in range(len(x)):
                cv2.rectangle(img, (x[i] - 5, y[i] - 5), (x[i] + 5, y[i] + 5), (0, 255, 0), 1)
                pixel = str(self.d[i]) + "km"
                cv2.putText(img, pixel, (x[i] + 3, y[i] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 0, 0))                        
            
            # Dark background for the textual contents on the bottom
            subimg = img.copy()
            cv2.rectangle(subimg, (0, h - 100), (w, h), (0, 0, 0), -1)
            img = cv2.addWeighted(img, 0.5, subimg, 0.5, 1)
            
            # TODO(Kyungwon): Structure the layout using QTableWidget Class.
            # Header for measured values
            text_position = (50, h - 40)
            cv2.putText(img, "Visibility", (text_position[0], text_position[1] - 10),  
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, "PM10", (text_position[0] + 180, text_position[1] - 10),  
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, "Temp.", (text_position[0] + 330, text_position[1] - 10),  
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, "Humidity", (text_position[0] + 460, text_position[1] - 10),  
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, "Atm. Pres.", (text_position[0] + 610, text_position[1] - 10),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            
            self.bottom_value()
            
            # Values of the content
            value_position = (50, h - 15)
            cv2.putText(img, f"{self.vi} km", (value_position[0] + 5, value_position[1] - 10),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, f"{self.md} ug/m3", (value_position[0] + 160, value_position[1] - 10),  
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, f"{self.tm} oC", (value_position[0] + 335, value_position[1] - 10),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, f"{self.hm} %", (value_position[0] + 480, value_position[1] - 10),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, f"{self.br} hpa", (value_position[0] + 620, value_position[1] - 10), 
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            epoch = int(time.time())
            epoch = time.strftime("%Y.%m.%d %H:%M:%S :%z", time.localtime(epoch))            
            cv2.putText(img, epoch, (value_position[0] + 830, value_position[1] - 10),  
                        cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255))
            qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label1.setPixmap(pixmap)
        print("End thread")
        
    # Start video stream
    def start(self, index: int):
        global running
        running = True
        if index == 1:
            self.camnumber = "v2"
            th1 = threading.Thread(target = self.run)
            th1.start()
            print("v2 camera started...")
        elif index == 2:
            self.camnumber = "ir"
            th1 = threading.Thread(target = self.run)
            th1.start()
            print("IR camera started...")
            
    def stop(self):
        global running
        running = False        
        print("Stop...")
        
    def get_target(self):
        df = pd.read_csv(f"{path}{self.camnumber}.csv")
        self.x = df["x"]
        self.y = df["y"]
        self.d = df["distance"]       

    #TODO(ChaeSeongMin): 센서에서 수집한 데이터를 InfluxDB에 저장한 후 값을 보여준다.    
    def bottom_value(self):        
        a = [0.1, 0.12, 0.21, 0.28, 0.91, 0.93, 0.33, 1.3, 2.0,
             3.7, 5.4, 5.0, 6.5, 1.7]        
        i = random.randint(0, len(a) - 1)
        self.vi = str(a[i])        
        self.md = str(random.randint(20, 60))
        self.tm = str(random.randint(28, 33))
        self.hm = str(random.randint(40, 70))
        self.br = str(random.randint(990, 1000))
        
    def keyPressEvent(self, e: QtGui.QKeyEvent):
        # v2 image read
        if e.key() == Qt.Key_Q:            
            self.stop()
            time.sleep(1)            
            self.start(1)
            
        # Read IR image
        elif e.key() == Qt.Key_W:
            self.stop()
            time.sleep(1)            
            self.start(2)
            
        # Quit program
        elif e.key() == Qt.Key_G:
            self.stop()
            self.close()
            
def main():
    app = QApplication(sys.argv)
    ex = pyqt_ipcam()
    # Default behavior is to read a v2 image
    ex.start(1)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
