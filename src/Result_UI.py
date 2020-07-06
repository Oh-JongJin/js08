import os
import sys
import time
import this
import math
import threading
import numpy as np
import pandas as pd
import RPi.GPIO as gp
import random
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QGridLayout
from PyQt5 import uic
from PyQt5.QtCore import Qt
from imutils.video import VideoStream
import rpi_image_get_rgb

import cv2


SEL = 7
EN1 = 11
EN2 = 12

gp.setwarnings(False)
gp.setmode(gp.BOARD)
gp.setup(SEL,gp.OUT)
gp.setup(EN1,gp.OUT)
gp.setup(EN2,gp.OUT)

fps = 5
# img size and target point
scale = 3

class pyqt_ipcam(QWidget):

    def __init__(self):
        super().__init__()
        self.setGeometry(0,50,750,600)        
        self.grid = QGridLayout()
        self.label1 = QLabel()
        self.label2 = QLabel()
        self.label3 = QLabel()
        self.label4 = QLabel()
        self.grid.addWidget(self.label1, 0, 0)
        self.grid.addWidget(self.label2, 0, 1)
        self.setLayout(self.grid)
        self.show()
        
        
    # v2 camera on   
    def run1(self):
        self.camnumber = 'v2'
        self.get_target()
        
        x = [int(i/scale) for i in self.x]
        y = [int(i/scale) for i in self.y]
        while running:
            img = cv2.imread('images/2020070313_v2.png', cv2.IMREAD_COLOR)            
            h, w, c= img.shape
            dim = (int(w/scale),int(h/scale))
            self.img = img
            img = cv2.resize(img,None, fx = 1/scale, fy = 1/scale, interpolation = cv2.INTER_AREA)
            h, w, c= img.shape
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            for i in range(len(x)):
                cv2.rectangle(img, (x[i]-5, y[i]-5), (x[i]+5, y[i]+5), (0, 255, 0), 1)
                pixel = str(self.d[i]) + "km"
                cv2.putText(img, pixel, (x[i] + 3, y[i] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 0, 0))                        
            
            # bottom black rectangle
            subimg = img.copy()
            cv2.rectangle(subimg, (0, h-100), (w, h), (0, 0, 0), -1)
            img = cv2.addWeighted(img, 0.5, subimg, 0.5, 1)
            
            
            # bottom content
            #
            text_position = (50, h-40) 
            cv2.putText(img, 'Visibility', (text_position[0], text_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, 'Micro Dust(PM10)', (text_position[0]+150, text_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, 'Temperature', (text_position[0]+350, text_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, 'Humidity', (text_position[0]+510, text_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, 'Barometer', (text_position[0]+640, text_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            
            
            # value text
            value_position = (50, h-15) 
            cv2.putText(img, '6.5 km', (value_position[0]+10, value_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, '37 ug/m', (value_position[0]+180, value_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, '28 C', (value_position[0]+380, value_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, '79 %', (value_position[0]+530, value_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, '1000 hpa', (value_position[0]+650, value_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255))
            epoch = int(time.time())
            epoch = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(epoch))            
            cv2.putText(img, epoch, (value_position[0]+750, value_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255))
            qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label1.setPixmap(pixmap)    
        print('Thread end')
    # noir camera on    
    def run2(self):
        self.camnumber = 'noir'
        self.get_target()
        # capture image size to cv video size
        x = [int(i/scale) for i in self.x]
        y = [int(i/scale) for i in self.y]
        
        while running:
            img = cv2.imread('images/2020070313_noir.png', cv2.IMREAD_COLOR)
            h, w, c= img.shape
            dim = (int(w/scale),int(h/scale))
            self.img = img
            img = cv2.resize(img,None, fx = 1/scale, fy = 1/scale, interpolation = cv2.INTER_AREA)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h,w,c = img.shape
            for i in range(len(x)):
                cv2.rectangle(img,(x[i]-5, y[i]-5), (x[i]+5, y[i]+5), (0, 255, 0), 1)
                pixel = str(self.d[i]) + "km"
                cv2.putText(img, pixel, (x[i] + 3, y[i] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 0, 0))
            # bottom black rectangle
            subimg = img.copy()
            cv2.rectangle(subimg, (0, h-100), (w, h), (0, 0, 0), -1)
            img = cv2.addWeighted(img, 0.5, subimg, 0.5, 1)
            
            text_position = (100, h-50) 
            cv2.putText(img, 'visibility : 6.5 km', (text_position[0], text_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 0, 0))
            qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label2.setPixmap(pixmap)
        print('Thread end')
        
    #video run    
    def start(self, index: int):
        global running
        running = True
            
        if index == 1:  
            th1 = threading.Thread(target=self.run1)
            th1.start()
            print("v2 Camera started..")
            
        elif index == 2:     
            th2 = threading.Thread(target=self.run2)
            th2.start()
            print("noir Camera started..")
            
            
    def stop(self):
        global running
        running = False        
        print("Stop..")
        
    def get_target(self):
        df = pd.read_csv(f"data/{self.camnumber}.csv")
        self.x = df['x']
        self.y = df['y']
        self.d = df['distance']
            
    def img_capture(self, filename: str, img: np.ndarray):        
        path = str(os.getcwd())
        cmd = f"raspistill -hf -vf -e png -o {path}/images/{filename}.png"
        print('Please wait')
        os.system(cmd)
        print("Image Save")

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        print(type(e))
        # v2 camera on
        if e.key() == Qt.Key_Q:            
            self.stop()
            # sleep
            time.sleep(1)
            self.start(1)
        # noir camera on    
        elif e.key() == Qt.Key_W:
            self.stop()
            time.sleep(1)
            self.start(2)
        # cam close
        elif e.key() == Qt.Key_G:
            self.stop()
            self.close() 
            


def main():
    app = QApplication(sys.argv)
    ex=pyqt_ipcam()
    #Default v2 Camera Start
    ex.start(1)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()




