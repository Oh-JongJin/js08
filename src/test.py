# 구글 파이썬 스타일 가이드를 적용해야된다.

import cv2
import threading
import sys
from random import *
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout


# 키입력으로 바꿔서 적용하려면 클래스를 만들어서 해야함.
# 클래스 안에 생성자에서 사용할 클래스는 parent 자리에 입력해준다.
# 모든 생성자들을 생성할 때는 self.를 꼭 선언해줘야 한다.
class pyqt_ipcam(QWidget):

    def __init__(self):
        super().__init__()
        # 모든 생성자들을 생성할 때는 self.를 꼭 선언해줘야 한다.
        # label의 사이즈에 따라 Widget의 크기를 변경한다. (위젯은 변하지만 영상의 크기는 안변하기 때문에 따로 설정해줘야 한다.)
        self.grid = QGridLayout()
        self.label = QLabel()
        self.grid.addWidget(self.label, 0, 0)       
        self.setLayout(self.grid)
        
    def run(self):
        
        # 웹캠으로 테스트
        cap = cv2.VideoCapture(0)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)                
        self.label.resize(width, height)

        # 초기 사이즈 값을 저장한다. 
        prewidth = width
        preheight = height

        # 임의 타겟들을 정함 get_target   
        self.get_target()

        self.setMouseTracking(True)

        while running:
            ret, img = cap.read()
            if ret:
                mowidth = self.label.width()/width
                moheight = self.label.height()/height
                

                # 타겟들을 사각형으로 호출 get_target
                for i in range(10):
                    cv2.rectangle(img,(self.x[i]-5,self.y[i]-5),(self.x[i]+5,self.y[i]+5),(0,255,0),1)
                    pixel = f"(target{i})"
                    mpixel = f"x : {self.mx}, y : {self.my}"
                    cv2.putText(img, pixel, (self.x[i] + 3, self.y[i] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))
            
                # resize의 fx는 비율로 크기를 조절한다.
                # 레이블의 크기에 따라 영상 크기도 같이 변한다.
                if prewidth <= self.label.width() or preheight <= self.label.height():
                    img = cv2.resize(img, dsize=(0, 0), fx=mowidth, fy=moheight, interpolation=cv2.INTER_LINEAR)           
                # elif prewidth > self.label.width() or preheight > self.label.height() :
                #     img = cv2.resize(img, dsize=(0, 0), fx=self.label.width()/width, fy=self.label.height()/height, interpolation=cv2.INTER_AREA)

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
                h,w,c = img.shape
                qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.label.setPixmap(pixmap)
                prewidth = self.label.width()
                preheight = self.label.height()
            else:                
                print("cannot read frame.")
                break
        cap.release()
        print("Thread end.")


    def mouseMoveEvent(self, event):
        self.mx = event.x()
        self.my = event.y()

    # 임의 타겟들을 정함 get_target    
    def get_target(self):
        self.x = []
        self.y = []
        for i in range(10):
            self.x.append(randrange(10,620))
            self.y.append(randrange(10,460))
    
    # 영상 읽기를 중단한다.
    def stop(self):
        global running
        running = False
        print("stoped..")

    # 영상을 읽는다
    # Thread로 실행한다.
    def start(self):
        global running
        running = True
        th = threading.Thread(target=self.run)
        th.start()
        print("started..")

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
            self.showFullScreen()
        elif e.key() == Qt.Key_N:
            self.showNormal()

def main():
    app = QApplication(sys.argv)
    ex=pyqt_ipcam()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()