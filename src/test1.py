

import cv2
import threading
import sys
import math
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsView, QLabel, QGridLayout, QWidget
from PyQt5.QtCore import Qt
 
class Shufti(QWidget):
    running = True
    def __init__(self):
        super().__init__()
        # 모든 생성자들을 생성할 때는 self.를 꼭 선언해줘야 한다.
        # label의 사이즈에 따라 Widget의 크기를 변경한다. (위젯은 변하지만 영상의 크기는 안변하기 때문에 따로 설정해줘야 한다.)
        self.grid = QGridLayout()
        self.scene = QGraphicsScene()      
        self.view = QGraphicsView(self.scene, self)
        self.zoom = 1        
        self.setWindowTitle("shufti")        
        self.view = QGraphicsView(self.scene, self)              
        self.grid.addWidget(self.view, 0, 0)
        self.setGeometry(200,200,self.view.width(),self.view.height())
        running = True 


    def run(self):               
        # 웹캠으로 테스트
        cap = cv2.VideoCapture(0)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.view.resize(width,height)
        while running:
            ret, img = cap.read()
            if ret:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
                h,w,c = img.shape
                qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.scene.addPixmap(pixmap)
            else:                
                print("cannot read frame.")
                break
        cap.release()
        print("Thread end.")      
 
    # def initUI(self):               
    #     # self.label = QLabel()

    #     self.img = QPixmap(sys.argv[1])
    #     # self.label.setPixmap(self.img)        
    #     self.scene = QGraphicsScene()
    #     # self.scene.addWidget(self.img)    

    #     self.grid.addWidget(self.view, 0, 0)
    #     # self.view.resize(self.img.width() + 2, self.img.height() + 2)

 
    def toggleFullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

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
 
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F11 or event.key() == QtCore.Qt.Key_F:
            self.toggleFullscreen()
        if event.key() == Qt.Key_T:     
            self.start()
        elif event.key() == Qt.Key_Space:
            self.stop()
        elif event.key() == Qt.Key_Q:
            self.onExit()
        elif event.key() == Qt.Key_N:
            self.showNormal()
 
    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            self.zoom += event.angleDelta().y()/2400
        
        self.view.scale(self.zoom, self.zoom)
 
def main():
    #모든 PyQT Application들은 항상 Application Object를 생성해야 한다.
    #파라미터로 Shell에서 넘긴 값 sys.argv를 받고 있다. []를 넘겨서 안 받아도 된다.
    app = QApplication(sys.argv)
    #위에서 정의한 pyqt_ipcam 객체를 생성한다.
    ex=Shufti()
    #Widget은 일단 메모리에 적재된 뒤 show 메소드로 화면에 보여준다.
    ex.show()
    ex.start()
    #Application의 Mainloop에 들어가게 된다.
    #Mainloop가 종료되려면 sys.exit()를 선언하거나 Mian Widget이 죽어야 된다.
    #exec_는 Python에서 exec를 이미 사용하고 있다.
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()