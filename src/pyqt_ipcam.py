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
    4 : Read Hanhwa camera 
Mouse event:
    
    Left click : Add target
    Right click : Remove recently created target
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
from PyQt5.QtWidgets import QGridLayout, QWidget, QLabel, QApplication, QLineEdit, QInputDialog
import inference
import model_read

# UI를 정의하는 클래스
# 키, 마우스 입력을 받으려면 QWidget 클래스를 상속 받아야 한다.
class pyqt_ipcam(QWidget):

    def __init__(self):
        super().__init__()              
        self.grid = QGridLayout()        
        self.label = QLabel()        
        self.setGeometry(0, 150, 1920, 800)       
        self.grid.addWidget(self.label, 0, 0)
        self.grid.setContentsMargins(0, 0, 0, 0)   
        self.setLayout(self.grid)
        self.show()
        # 모델을 미리 저장한다
        self.model = model_read.read_model()        
        
    def run(self):
        if self.camname == "img":
            img = cv2.imread("test.png", cv2.IMREAD_COLOR)
            height, width, ch = img.shape
        else:            
            self.cap = cv2.VideoCapture(self.ADD)
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)          
        oxlist = []
        visivlity = "0.0 km"
        while self.running:
            
            # 시간 저장
            epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))

            #마우스 트래킹 감지 False이면 클릭시 이동을 감지
            self.setMouseTracking(False)            
            # camname이 이미지가 아닐 때 cap으로 읽기
            if not self.camname == "img":
                ret, img = self.cap.read()
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # camname이 이미지가 일 때 imread 메서드로 읽기        
            else:
                img = cv2.imread("test.png", cv2.IMREAD_COLOR)
                img = cv2.resize(img, dsize=(self.label.width(), self.label.height()))
                ret = 1
            
            # 이미지를 읽어오면 실행
            if ret:
                # 영상 목표들을 사각형으로 호출 get_target
                if len(self.x) >= 0:
                    
                    for i in range(len(self.x)):
                        if epoch[-3:] == "500" or epoch[-3:] == "000":
                            try:
                                if not(os.path.isdir(f"target/target{i+1}")):
                                    os.makedirs(os.path.join(f"target/target{i+1}"))

                                if not(os.path.isfile(f"target/target{i+1}/{epoch}.png")):
                                    # 모델에 넣을 이미지 추출
                                    crop_img = img[self.y[i] - 112 : self.y[i] + 112 , self.x[i] - 112 : self.x[i] + 112]
                                    # cv로 저장할 때는 bgr 순서로 되어 있기 때문에 rgb로 바꿔줌.
                                    b, g, r = cv2.split(cropimg)
                                    # 영상 목표의 각 폴더에 크롭한 이미지 저장
                                    cv2.imwrite(f"target/target{i+1}/{epoch}.png", cv2.merge([r, g, b]))
                            except OSError as e:
                                if e.errno != errno.EEXIST:    
                                    pass
                            result = inference.inference(self.model, f"target/target{i+1}")
                            oxlist.append(result[-1])                             
                        else:
                            pass                            
                        # UI 이미지에 사각형으로 표시
                        upper_left = self.x[i] - 50, self.y[i] - 50
                        lower_right = self.x[i] + 50, self.y[i] + 50
                        cv2.rectangle(img, upper_left, lower_right, (0, 255, 0), 5)
                        pixel = str(i+1)
                        text_loc = self.x[i] + 45, self.y[i] - 55
                        cv2.putText(img, str(self.dis[i]) + " km", text_loc, cv2.FONT_HERSHEY_COMPLEX, 
                                    1.5, (255, 0, 0), 3)
                else:
                    pass
                h, w, c=  img.shape

                # Dark background for the textual contents on the bottom
                subimg = img.copy()
                cv2.rectangle(subimg, (0, h - 400), (w, h), (0, 0, 0), -1)
                img = cv2.addWeighted(img, 0.5, subimg, 0.5, 1)

                # 시정값 표시
                # 보이는 영상 목표들 중 거리가 가장 높은 것을 시정값으로 지정한다.
                if len(oxlist) > 0:
                    res = [self.dis[x] for x, y in enumerate(oxlist) if y == 1]
                    visivlity = str(max(res)) + " km"
                    oxlist = []
                
                cv2.putText(img, visivlity, (200, h - 80),  
                            cv2.FONT_HERSHEY_COMPLEX, 1.8, (255, 255, 255), 2)

                # 시계 표시
                clock = time.strftime("%Y.%m.%d %H:%M:%S :%z", time.localtime(time.time()))                       
                cv2.putText(img, clock, (w - 1000, h - 80),  
                            cv2.FONT_HERSHEY_COMPLEX, 1.8, (255, 255, 255), 2)

                # GUI에 작업한 이미지 출력
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

        # 종료될 때 영상 목표 정보를 실행된 카메라에 맞춰서 저장
        if len(self.x) >= 0:
            for i in range(len(self.x)):
                print(self.x[i], ", ", self.y[i], ", ", self.dis[i])
            col = ["x","y","dis"]
            result = pd.DataFrame(columns=col)
            result["x"] = self.x
            result["y"] = self.y
            result["dis"] = self.dis
            result.to_csv(f"target/{self.camname}.csv", mode="w", index=False)
            print("영상 목표가 저장되었습니다.")
        
        print("Thread end.")

    # 임의 타겟들을 정함 get_target    
    def get_target(self):
        self.x = []
        self.y = []
        self.dis = []
        if os.path.isfile(f"target/{self.camname}.csv") == True:
            result = pd.read_csv(f"target/{self.camname}.csv")
            self.x = result.x.tolist()
            self.y = result.y.tolist()
            self.dis = result.dis.tolist()
            print("영상 목표를 불러옵니다.")

    # QWidget Layout의 사이즈가 변환될 때 호출되는 메서드
    # label 위젯의 크기를 변환하기 위해 재정의한다.
    def resizeEvent(self, event):
        print(self.width(), ", ", self.height())
        self.label.resize(self.width(), self.height())
    
    # 영상을 읽는다
    # Thread로 실행한다.
    def start(self):
        self.running = True
        th = threading.Thread(target=self.run)
        th.start()
        # 임의 영상 목표들을 정함 get_target   
        self.get_target()                
        print("started..")
    
    # 영상 읽기를 중단한다.
    def stop(self):
        self.running = False               
        print("stoped..")
        time.sleep(1)

    # 프로그램을 종료한다.
    def onExit(self):
        print("exit")
        self.stop()
        self.close()

    # 키보드 입력 이벤트
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_T:
            self.start()
        elif e.key() == Qt.Key_Space:
            self.stop()
        elif e.key() == Qt.Key_Q:
            self.onExit()
        elif e.key() == Qt.Key_F:
            self.showMaximized()
        elif e.key() == Qt.Key_N:
            self.showNormal()
        elif e.key() == Qt.Key_1:
            self.stop()
            self.camname = "hanhwa"
            self.ADD = "rtsp://admin:sijung5520@192.168.100.121/profile2/media.smp"
            self.start()
        elif e.key() == Qt.Key_2:
            self.stop()
            self.camname = "commax"
            self.ADD = "rtsp://admin:1234@192.168.100.251:554/1/1"
            self.start()
        elif e.key() == Qt.Key_3:
            self.stop()
            self.camname = "img"            
            self.start()
        elif e.key() == Qt.Key_4:
            self.stop()
            self.camname = "hanhwa"
            self.ADD = "rtsp://admin:G85^mdPzCXr2@192.168.100.115/profile2/media.smp"
            self.start()
        
    # 마우스 이벤트
    def mousePressEvent(self, e):
        # 마우스 왼쪽 버튼을 누르면 영상 목표를 추가
        if e.button() == Qt.LeftButton:
            text, ok = QInputDialog.getText(self, '타겟거리입력', '거리(km)')
            if ok:
                self.dis.append(str(text))
                # Label의 크기와 카메라 원본 이미지 해상도의 차이를 고려해 계산한다. 약 3.175배
                self.x.append(int(e.x() * 3.175))
                self.y.append(int(e.y() * 3.175))
                print("영상 목표위치:", int(e.x() * 3.175),", ", int(e.y() * 3.175))
                time.sleep(1)
        # 오른쪽 버튼을 누르면 최근에 추가된 영상 목표를 제거.
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
    a = "arar"    
    app = QApplication(sys.argv)
    ex = pyqt_ipcam()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    