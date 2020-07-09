#!/usr/bin/env python3
# TODO(ChaeSeongMin): Apply Google Python Style Guide 3.13 Imports formatting
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
import RPi.GPIO as gp
import threading

import rpi_image_get_rgb

SEL = 7
EN1 = 11
EN2 = 12
fps = 5
path = "images/"

gp.setwarnings(False)
gp.setmode(gp.BOARD)
gp.setup(SEL, gp.OUT)
gp.setup(EN1, gp.OUT)
gp.setup(EN2, gp.OUT)

class pyqt_ipcam(QWidget):


    def __init__(self):
        super().__init__()
        self.setGeometry(200, 300, 750, 600)        
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
        self.camnumber = "v2"
        self.get_target()
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, fps)
        x = [int(i/5.125)for i in self.x]
        y = [int(i/5.125)for i in self.y]
        while running:
            rev, img = cap.read()
            img = cv2.flip(img, 0)
            img = cv2.flip(img, 1)
            self.img = img
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            for i in range(len(x)):
                cv2.rectangle(img, (x[i] - 2, y[i] - 2), (x[i] + 2, y[i] + 2), (0, 255, 0), 1)
                pixel = str(self.d[i]) + "km"
                cv2.putText(img, pixel, (x[i] + 3, y[i] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 0, 0))        
            h, w, c = img.shape
            qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label1.setPixmap(pixmap)            
        cap.release()
        print("Thread end")
        
    # ir camera on    
    def run2(self):
        self.camnumber = "ir"
        self.get_target()
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, fps)
        # capture image size to cv video size
        x = [int(i / 5.125)for i in self.x]
        y = [int(i / 5.125)for i in self.y]
        
        while running:
            rev, img = cap.read()
            img = cv2.flip(img, 0)
            img = cv2.flip(img, 1)
            self.img = img
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            for i in range(len(x)):
                cv2.rectangle(img, (x[i] - 2, y[i] - 2), (x[i] + 2, y[i] + 2), (0, 255, 0), 1)
                pixel = str(self.d[i]) + "km"
                cv2.putText(img, pixel, (x[i] + 3, y[i] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 0, 0))        
            h, w, c = img.shape
            qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label2.setPixmap(pixmap)                
        cap.release()
        print("Thread end")
        
    #video run    
    def start(self, index: int):
        global running
        running = True
            
        if index == 1:
            self.i2c = "i2cset -y 1 0x70 0x00 0x05"
            os.system(self.i2c)
            gp.output(SEL, True)
            gp.output(EN1, False)
            gp.output(EN2, True)  
            th1 = threading.Thread(target=self.run1)
            th1.start()
            print("v2 Camera started..")
            
        elif index == 2:
            self.i2c = "i2cset -y 1 0x70 0x00 0x07"
            os.system(self.i2c)
            gp.output(SEL, True)
            gp.output(EN1, True)
            gp.output(EN2, False)      
            th2 = threading.Thread(target=self.run2)
            th2.start()
            print("ir Camera started..")
            
    def stop(self):
        global running
        running = False        
        print("Stop..")
        
    def get_target(self):
        df = pd.read_csv(f"data/{self.camnumber}.csv")
        self.x = df["x"]
        self.y = df["y"]
        self.d = df["distance"]
            
    def img_capture(self, foldername: str):
        os.makedirs(os.path.join(f"{path}/{foldername}"))
        print("Please wait")
        self.i2c = "i2cset -y 1 0x70 0x00 0x05"
        os.system(self.i2c)
        gp.output(SEL, True)
        gp.output(EN1, False)
        gp.output(EN2, True)
        cmd = f"raspistill -hf -vf -e png -o {path}/{foldername}/v2.png"
        os.system(cmd)
        self.i2c = "i2cset -y 1 0x70 0x00 0x07"
        os.system(self.i2c)
        gp.output(SEL, True)
        gp.output(EN1, True)
        gp.output(EN2, False) 
        cmd = f"raspistill -hf -vf -e png -o {path}/{foldername}/ir.png"
        os.system(cmd)            
        print("Image Save")

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        # v2 camera on
        if e.key() == Qt.Key_Q:            
            self.stop()
            time.sleep(1)
            self.start(1)
        # ir camera on    
        elif e.key() == Qt.Key_W:
            self.stop()
            time.sleep(1)
            self.start(2)
        # cam close
        elif e.key() == Qt.Key_G:
            self.stop()
            self.close()
        # image capture and get target rgb    
        elif e.key() == Qt.Key_C:
            self.stop()
            time.sleep(1)
            epoch = int(time.time())            
            foldername = time.strftime("%Y%m%d%H", time.localtime(epoch))
            # img capture
            self.img_capture(foldername)
            # get target rgb
            rpi_image_get_rgb.get_rgb(foldername, "v2")
            rpi_image_get_rgb.get_rgb(foldername, "ir")
            gp.output(SEL, False)
            gp.output(EN1, False)
            gp.output(EN2, False) 

def main():
    app = QApplication(sys.argv)
    ex=pyqt_ipcam()
    # Default behavior is to read a v2 image
    ex.start(1)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()



