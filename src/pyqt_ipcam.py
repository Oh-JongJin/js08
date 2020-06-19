# 구글 파이썬 스타일 가이드를 적용해야된다.

import cv2
import threading
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QGridLayout


running = False
def run():
    global running
    # 웹캠으로 테스트
    cap = cv2.VideoCapture(0)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    label.resize(width, height)
    # 초기 사이즈 값을 저장한다. 
    prewidth = width
    preheight = height
    while running:
        ret, img = cap.read()
        if ret:
            # label 크기가 변하면 영상의 크기도 resize 시킨다. 
            # resize의 fx는 비율로 크기를 조절한다.
            if prewidth <= label.width() or preheight <= label.height():
                img = cv2.resize(img, dsize=(0, 0), fx=label.width()/width, fy=label.height()/height, interpolation=cv2.INTER_LINEAR)            
            elif prewidth > label.width() or preheight > label.height() :
                img = cv2.resize(img, dsize=(0, 0), fx=label.width()/width, fy=label.height()/height, interpolation=cv2.INTER_AREA)

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
            h,w,c = img.shape
            qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            label.setPixmap(pixmap)
            prewidth = label.width()
            preheight = label.height()
            print(label.width() , ", ",label.height())
            print(width, height)
        else:
            QtWidgets.QMessageBox.about(win, "Error", "Cannot read frame.")
            print("cannot read frame.")
            break
    cap.release()
    print("Thread end.")
# 영상 읽기를 중단한다.
def stop():
    global running
    running = False
    print("stoped..")

# 영상을 읽는다
# Thread로 실행한다.
def start():
    global running
    running = True
    th = threading.Thread(target=run)
    th.start()
    print("started..")
# 프로그램을 종료한다.
def onExit():
    print("exit")
    stop()

app = QtWidgets.QApplication([])
win = QtWidgets.QWidget()
# label의 사이즈에 따라 Widget의 크기를 변경한다. (위젯은 변하지만 영상의 크기는 안변하기 때문에 따로 설정해줘야 한다.)
grid = QGridLayout()
label = QtWidgets.QLabel()
btn_start = QtWidgets.QPushButton("Camera On")
btn_stop = QtWidgets.QPushButton("Camera Off")
grid.addWidget(label, 0, 0)
grid.addWidget(btn_start, 1, 0)
grid.addWidget(btn_stop, 2, 0)
win.setLayout(grid)
win.show()

btn_start.clicked.connect(start)
btn_stop.clicked.connect(stop)
app.aboutToQuit.connect(onExit)

sys.exit(app.exec_())