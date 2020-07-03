import os
import sys
import time
import this
import math
import threading
import numpy as np
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


class pyqt_ipcam(QWidget):

    def __init__(self):
        super().__init__()
        self.setGeometry(200,300,750,600)        
        self.grid = QGridLayout()
        self.label1 = QLabel()
        self.label2 = QLabel()
        self.label3 = QLabel()
        self.label4 = QLabel()
        self.grid.addWidget(self.label1, 0, 0)
        self.grid.addWidget(self.label2, 0, 1)
        self.grid.addWidget(self.label3, 1, 0)
        self.grid.addWidget(self.label4, 1, 1) 
        self.setLayout(self.grid)
        self.show()
        
        
        
    def run1(self):
        self.camnumber = 'v2_1'
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, fps)
        cap_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.get_target(cap_h,cap_h)
        print(cap_w, ", ", cap_h)
        while running:
            #rev, img = cap.read()
            rev, img = cap.read()
            img = cv2.flip(img,0)
            img = cv2.flip(img,1)
            self.img = img
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            for i in range(10):
                cv2.rectangle(img,(self.x[i]-5,self.y[i]-5),(self.x[i]+5,self.y[i]+5),(0,255,0),1)
                pixel = str(i+1)
                cv2.putText(img, pixel, (self.x[i] + 3, self.y[i] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0))        
            h,w,c = img.shape
            qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label1.setPixmap(pixmap)
                
        cap.release()
        print('Thread end')
        
    def run2(self):
        self.camnumber = 'v2'
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, fps)
        cap_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(cap_w, ", ", cap_h)
        self.get_target(cap_h,cap_h)
        while running:
            #rev, img = cap.read()
            rev, img = cap.read()
            img = cv2.flip(img,0)
            img = cv2.flip(img,1)
            self.img = img
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            for i in range(10):
                cv2.rectangle(img,(self.x[i]-5,self.y[i]-5),(self.x[i]+5,self.y[i]+5),(0,255,0),1)
                pixel = str(i+1)
                cv2.putText(img, pixel, (self.x[i] + 3, self.y[i] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0))        
            h,w,c = img.shape
            qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label2.setPixmap(pixmap)
            
        cap.release()
        print('Thread end')
        
    def run3(self):
        self.camnumber = 'noir'
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, fps)
        cap_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(cap_w, ", ", cap_h)
        self.get_target(cap_h,cap_h)
        while running:
            #rev, frame = cap.read()
            rev, img = cap.read()
            img = cv2.flip(img,0)
            img = cv2.flip(img,1)
            self.img = img
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            for i in range(10):
                cv2.rectangle(img,(self.x[i]-5,self.y[i]-5),(self.x[i]+5,self.y[i]+5),(0,255,0),1)
                pixel = str(i+1)
                cv2.putText(img, pixel, (self.x[i] + 3, self.y[i] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0))        
            h,w,c = img.shape
            qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label3.setPixmap(pixmap)
                
        cap.release()
        print('Thread end')
        
    def run4(self):
        self.camnumber = 'noir_2'
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, fps)
        cap_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(cap_w, ", ", cap_h)
        self.get_target(cap_h,cap_h)
        while running:
            #rev, frame = cap.read()
            rev, img = cap.read()
            img = cv2.flip(img,0)
            img = cv2.flip(img,1)
            self.img = img
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            for i in range(10):
                cv2.rectangle(img,(self.x[i]-5,self.y[i]-5),(self.x[i]+5,self.y[i]+5),(0,255,0),1)
                pixel = str(i+1)
                cv2.putText(img, pixel, (self.x[i] + 3, self.y[i] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0))        
            h,w,c = img.shape
            qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label4.setPixmap(pixmap)
                
        cap.release()
        print('Thread end')
        
    def start(self, index: int):
        global running
        running = True
        if index == 1:
            self.i2c = "i2cset -y 1 0x70 0x00 0x04"
            os.system(self.i2c)
            gp.output(SEL, False)
            gp.output(EN1, False)
            gp.output(EN2, True)      
            th1 = threading.Thread(target=self.run1)
            th1.start()
            print("1st Camera started..")
            
        elif index == 2:
            self.i2c = "i2cset -y 1 0x70 0x00 0x05"
            os.system(self.i2c)
            gp.output(SEL, True)
            gp.output(EN1, False)
            gp.output(EN2, True)      
            th1 = threading.Thread(target=self.run2)
            th1.start()
            print("2st Camera started..")
            
        elif index == 3:
            self.i2c = "i2cset -y 1 0x70 0x00 0x06"
            os.system(self.i2c)
            gp.output(SEL, False)
            gp.output(EN1, True)
            gp.output(EN2, False)      
            th1 = threading.Thread(target=self.run3)
            th1.start()
            print("3st Camera started..")
            
        elif index == 4:
            self.i2c = "i2cset -y 1 0x70 0x00 0x07"
            os.system(self.i2c)
            gp.output(SEL, True)
            gp.output(EN1, True)
            gp.output(EN2, False)      
            th1 = threading.Thread(target=self.run4)
            th1.start()
            print("4st Camera started..")
            
    def stop(self):
        global running
        running = False        
        print("Stop..")
        
    def get_target(self, w: int, h: int):
        self.x = []
        self.y = []
        for i in range(10):
            self.x.append(random.randrange(10, w - 50))
            self.y.append(random.randrange(10, h - 50))
            
    def img_capture(self, filename: str, img: np.ndarray):
        path = str(os.getcwd())
        cmd = f"raspistill -hf -vf -e png -o {path}/images/{filename}.png"
        os.system(cmd)    
        #cv2.imwrite(f'{filename}.png', img)
        print("Image Save")

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        print(type(e))
        if e.key() == Qt.Key_Q:            
            self.stop()
            # sleep
            time.sleep(1)
            self.start(1)            
        elif e.key() == Qt.Key_W:
            self.stop()
            time.sleep(1)
            self.start(2)
        elif e.key() == Qt.Key_E:
            self.stop()
            time.sleep(1)
            self.start(3)
        elif e.key() == Qt.Key_R:
            self.stop()
            time.sleep(1)
            self.start(4)        
        elif e.key() == Qt.Key_G:
            self.stop()
            self.close()
        elif e.key() == Qt.Key_C:
            self.stop()
            time.sleep(1)
            os.system(self.i2c)
            epoch = int(time.time())
            epoch = time.strftime("%Y%m%d%H", time.localtime(epoch))
            filename = epoch + "_" + self.camnumber
            # img capture
            self.img_capture(filename, self.img)
            # get target rgb
            #rpi_image_get_rgb.get_rgb(filename)
            gp.output(SEL, False)
            gp.output(EN1, False)
            gp.output(EN2, False)
            
            
            


def main():
    app = QApplication(sys.argv)
    ex=pyqt_ipcam()
    #Default 1st Camera Start
    ex.start(2)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


