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
path = 'images/2020070313/'
class pyqt_ipcam(QWidget):

    def __init__(self):
        super().__init__()
        self.setGeometry(0,50,750,600)        
        self.grid = QGridLayout()
        self.label1 = QLabel()
        self.grid.addWidget(self.label1, 0, 0)
        self.setLayout(self.grid)
        self.show()
        
        
    # image read   
    def run(self):
        
        self.get_target()
        
        x = [int(i/scale) for i in self.x]
        y = [int(i/scale) for i in self.y]
        while running:
            img = cv2.imread(f'images/2020070313_{self.camnumber}.png', cv2.IMREAD_COLOR)            
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
            # content text
            text_position = (50, h-40) 
            cv2.putText(img, 'Visibility', (text_position[0], text_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, 'PM10', (text_position[0]+180, text_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, 'Temp.', (text_position[0]+330, text_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, 'Humidity', (text_position[0]+460, text_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, 'Atm. Pres.', (text_position[0]+610, text_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            
            self.bottom_value()
            
            # value text
            value_position = (50, h-15)            
            cv2.putText(img, f'{self.vi} km', (value_position[0]+5, value_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, f'{self.md} ug/m3', (value_position[0]+160, value_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, f'{self.tm} C', (value_position[0]+335, value_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, f'{self.hm} %', (value_position[0]+480, value_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            cv2.putText(img, f'{self.br} hpa', (value_position[0]+620, value_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
            epoch = int(time.time())
            epoch = time.strftime("%Y.%m.%d %H:%M:%S :%z", time.localtime(epoch))            
            cv2.putText(img, epoch, (value_position[0]+830, value_position[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255))
            qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label1.setPixmap(pixmap)    
        print('Thread end')
    
        
    #video run    
    def start(self, index: int):
        global running
        running = True
        if index == 1:
            self.camnumber = 'nomal'
            th1 = threading.Thread(target=self.run)
            th1.start()
            print("nomal Camera started..")
        elif index == 2:
            self.camnumber = 'ir'
            th1 = threading.Thread(target=self.run)
            th1.start()
            print("ir Camera started..")
            
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
    def bottom_value(self):
        
        a = [0.1, 0.12, 0.21, 0.28, 0.91, 0.93, 0.33, 1.3, 2.0, 3.7, 5.4, 5.0, 6.5, 1.7]
        
        i = random.randint(0, len(a)-1)
        self.vi = str(a[i])        
        self.md = str(random.randint(20, 60))
        self.tm = str(random.randint(28, 33))
        self.hm = str(random.randint(40, 70))
        self.br = str(random.randint(990, 1000))
    def keyPressEvent(self, e: QtGui.QKeyEvent):
        print(type(e))
        # v2 image read
        if e.key() == Qt.Key_Q:            
            self.stop()
            # sleep
            time.sleep(1)            
            self.start(1)
            
        # noir image read
        elif e.key() == Qt.Key_W:
            self.stop()
            time.sleep(1)            
            self.start(2)
        # program end
        elif e.key() == Qt.Key_G:
            self.stop()
            self.close() 
            


def main():
    app = QApplication(sys.argv)
    ex=pyqt_ipcam()
    #Default v2 image read
    ex.start(1)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()




