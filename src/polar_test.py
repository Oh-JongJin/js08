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
import csv
import folium
import imgkit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PIL import ImageFont, ImageDraw, Image
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

# sys.setrecursionlimit(10000)
np.seterr(divide='ignore', invalid='ignore')

"""UI를 정의하는 클래스
키입력으로 바꿔서 적용하려면 클래스를 만들어서 해야함.
"""
class pyqt_ipcam(QWidget):
    def __init__(self):
        super().__init__()
        # 레이블의 크기에 따라 위젯의 크기를 변경한다. 위젯은 변하지만 영상의 크기는 고정되어 있기때문에 따로 설정 필요.
        global running
        running = False
        self.grid = QGridLayout()
        self.label = QLabel()
        # self.setGeometry(50, 50, 1820, 980)
        self.showFullScreen()
        self.grid.addWidget(self.label, 0, 0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)
        self.showNormal()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

    def run(self):
        global flag
        camname = self.camname
        if self.camname == "img":
            img = cv2.imread("test.png", cv2.IMREAD_COLOR)
            height, width, ch = img.shape
        else:
            self.cap = cv2.VideoCapture(self.ADD)
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f'''video size - {width}x{height}, Cam Name - "{self.camname}"''')
            # self.label.resize(width, height)

        # 초기 사이즈 값을 저장한다.
        prewidth = width
        preheight = height

        while running:
            # 마우스 트래킹 감지 False이면 클릭시 이동을 감지
            self.setMouseTracking(False)

            # camname이 이미지가 아닐 때 cap으로 읽기
            if not self.camname == "img":
                ret, img = self.cap.read()
                # TODO(성민): 윈도 크기를 작게 조정하는 기능이 작동하지 않습니다.
                # resize의 fx는 비율로 크기를 조절한다.
                # 레이블의 크기에 따라 영상 크기도 같이 변한다.
                # if prewidth <= self.label.width() or preheight <= self.label.height():
                #     img = cv2.resize(img, dsize=(0, 0), fx=mowidth, fy=moheight,
                #                         interpolation=cv2.INTER_LINEAR)
                if prewidth > self.label.width() or preheight > self.label.height():
                    img = cv2.resize(img, dsize=(0, 0),
                                     fx=self.label.width() / width,
                                     fy=self.label.height() / height,
                                     interpolation=cv2.INTER_AREA)

                    # camname이 이미지가 일 때 imread 메서드로 읽기
            else:
                img = cv2.imread("test.png", cv2.IMREAD_COLOR)
                img = cv2.resize(img, dsize=(self.label.width(), self.label.height()))
                ret = 1

            # 이미지를 읽어오면 실행
            if ret:
                # 30도 간격 선 그리기
                self.angle = []
                for i in range(1, 6):
                    degree = ["30", "60", "90", "120", "150"]
                    flag = int(self.width() / 6) * i
                    cv2.line(img, (flag, 0), (flag, 1080), (0, 0, 0), 1)
                    self.angle.append(flag)
                    cv2.putText(img, degree[i-1], (flag, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0))
                # print(self.angle)
                # 타겟들을 사각형으로 호출 get_target
                if len(self.x) >= 0:
                    try:
                        for i in range(len(self.x)):
                            upper_left = self.x[i] - 5, self.y[i] - 5
                            lower_right = self.x[i] + 5, self.y[i] + 5
                            cv2.rectangle(img, upper_left, lower_right, (0, 255, 0), 1)
                            # pixel = str(i + 1)
                            text_loc = self.x[i] + 3, self.y[i] - 10
                            cv2.putText(img, str(self.dis[i]) + " km", text_loc, cv2.FONT_HERSHEY_COMPLEX,
                                        0.5, (0, 0, 255))
                    except Exception as e:
                        print("error : ", e)
                        pass
                else:
                    pass
                h, w, c = img.shape

                # 하단 컨텐츠 소스
                # Dark background for the textual contents on the bottom
                subimg = img.copy()
                # cv2.rectangle(subimg, (0, h - 100), (w, h), (0, 0, 0), -1)
                img = cv2.addWeighted(img, 0.5, subimg, 0.5, 1)

                # GUI에 작업한 이미지 출력
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, c = img.shape
                qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.label.setPixmap(pixmap)
                cv2.waitKey(0)
            else:
                print("Cannot read frame.")
                break

        self.cap.release()

        # 타겟 정보 저장.
        if len(self.x) >= 0:
            for i in range(len(self.x)):
                print(self.x[i], ", ", self.y[i], ", ", self.dis[i], ", ", self.ang[i])
                self.ang[i] = (int(self.x[i]) * 180) / 1920
            col = ["x", "y", "dis", "ang"]
            result = pd.DataFrame(columns=col)
            result["x"] = self.x
            result["y"] = self.y
            result["dis"] = self.dis
            result["ang"] = self.ang
            result.to_csv(f"target/{self.camname}.csv", mode="w", index=False)
            print("target이 저장되었습니다.")

        print("Thread end.")

    # 임의 타겟들을 정함 get_target
    def get_target(self):
        self.x = []
        self.y = []
        self.dis = []
        self.ang = []
        if os.path.isfile(f"target/{self.camname}.csv"):
            result = pd.read_csv(f"target/{self.camname}.csv")
            self.x = result.x.tolist()
            self.y = result.y.tolist()
            self.dis = result.dis.tolist()
            self.ang = result.ang.tolist()
            print("target을 불러옵니다.")

    # 영상을 읽는다
    # Thread로 실행한다.
    def start(self):
        global running
        running = True
        th = threading.Thread(target=self.run)
        th.start()
        # 임의 타겟들을 정함 get_target
        self.get_target()
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
            plt.close()
        elif e.key() == Qt.Key_F:
            # self.showMaximized()
            self.showFullScreen()
        elif e.key() == Qt.Key_N:
            self.showNormal()
        elif e.key() == Qt.Key_1:
            self.stop()
            self.camname = "HANHWA Panoramic Camera"
            self.ADD = "rtsp://admin:sijung5520@192.168.100.121/profile2/media.smp"
            self.start()
        elif e.key() == Qt.Key_2:
            self.stop()
            self.camname = "HANHWA IP Camera"
            self.ADD = "rtsp://admin:G85^mdPzCXr2@192.168.100.115/profile2/media.smp"
            # self.ADD_HANHWA = "rtsp://admin:G85^mdPzCXr2@192.168.100.115:554/1/1"
            self.start()
        elif e.key() == Qt.Key_3:
            self.stop()
            self.camname = "img"
            self.start()
        elif e.key() == Qt.Key_Delete:
            if len(self.x) >= 1:
                del self.x[-1]
                del self.y[-1]
                del self.dis[-1]
                print("타겟을 제거했습니다.")
                time.sleep(1)
            else:
                pass
                print("제거할 타겟이 없습니다.")
        elif e.key() == Qt.Key_R:
            print(running)
        elif e.key() == Qt.Key_M:
            print(f"width:{self.width()}, height:{self.height()}")

    # 마우스 왼쪽 버튼을 누르면 타겟을 추가, 오른쪽 버튼은 최근에 추가된 타겟을 제거.
    def mousePressEvent(self, e):
        if running:
            if e.button() == Qt.LeftButton:
                text, ok = QInputDialog.getText(self, '타겟거리입력', '거리(km)')
                if ok:
                    self.dis.append(str(text))
                    self.x.append(e.x())
                    self.y.append(e.y())
                    print("타겟위치:", e.x(), ", ", e.y())
                    time.sleep(1)

    def mouseReleaseEvent(self, e):
        return super().mouseReleaseEvent(e)

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        add_cam_action = menu.addAction("카메라 설정")
        map_action = menu.addAction("위치 설정")
        polar_action = menu.addAction("Polar 그래프 출력")
        quit_action = menu.addAction("종료하기")
        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action == quit_action:
            self.onExit()
            qApp.quit()
        elif action == add_cam_action:
            self.cam_win = camera_window()
            self.cam_win.show()
        elif action == map_action:
            self.map_win = map_window()
            self.map_win.show()
        elif action == polar_action:
            self.polar_win = polar_window()
            self.polar_win.showMaximized()


class polar_window(QWidget):
    def __init__(self):
        super().__init__()

        self.path_dir = 'target'
        self.file_list = os.listdir(self.path_dir)
        fig1, self.ax1 = plt.subplots(1, 1, subplot_kw={'projection': 'polar'})
        self.ax1.set_thetamin(0)
        self.ax1.set_thetamax(np.pi * 180 / np.pi)

        self.ax1.plot(0, 0)
        self.ax1.set_ylim([0, 6])
        self.ax1.set_xlabel("Visibility", fontsize=15)
        self.ax1.set_ylabel("Angels", fontsize=15)

        fig1.set_tight_layout(True)
        canvas = FigureCanvas(fig1)
        # canvas.draw()
        lay = QHBoxLayout()
        self.setLayout(lay)
        lay.addWidget(canvas)
        # canvas.set_window_title("HIHI")


class map_window(QWidget):
    def __init__(self):
        super().__init__()
        self.latitude_label = QLabel(self)
        self.latitude_label.setText("위도")
        self.latitude_label.setGeometry(QtCore.QRect(20, 20, 40, 40))
        self.longitude_label = QLabel(self)
        self.longitude_label.setText("경도")
        self.longitude_label.setGeometry(QtCore.QRect(20, 60, 40, 40))

        self.latitude_input = QLineEdit(self)
        self.latitude_input.setGeometry(QtCore.QRect(60, 30, 100, 20))
        self.longitude_input = QLineEdit(self)
        self.longitude_input.setGeometry(QtCore.QRect(60, 70, 100, 20))

        self.select_btn = QPushButton(self)
        self.select_btn.setText("확인")
        self.select_btn.setGeometry(QtCore.QRect(60, 120, 80, 50))
        self.select_btn.clicked.connect(self.select_btn_click)

        self.setWindowTitle("Map Setting")
        self.setGeometry(900, 450, 200, 200)

    def select_btn_click(self):
        self.lat = self.latitude_input.text()
        self.long = self.longitude_input.text()
        print(f"위도:{self.lat}, 경도:{self.long}")

        map_osm = folium.Map(location=[float(self.lat), float(self.long)], zoom_start=14)
        map_osm.save('data/sijung.html')
        imgkit.from_file('data/sijung.html', 'out.jpg')

        self.close()


class camera_window(QWidget):
    def __init__(self):
        super().__init__()

        self.cam_combo = QComboBox(self)
        self.cam_combo.addItems(["카메라를 선택하세요.", "한화 파노라마 카메라", "한화 IP카메라", "코맥스 PTZ 카메라"])
        self.cam_combo.setGeometry(QtCore.QRect(20, 20, 150, 20))

        self.ip_label = QLabel(self)
        self.ip_label.setText("IP")
        self.ip_label.setGeometry(QtCore.QRect(20, 60, 40, 40))

        self.ip_input = QLineEdit(self)
        self.ip_input.setGeometry(QtCore.QRect(60, 70, 100, 20))

        self.select_btn = QPushButton(self)
        self.select_btn.setText("확인")
        self.select_btn.setGeometry(QtCore.QRect(60, 120, 80, 50))
        self.select_btn.clicked.connect(self.ip_select)

        self.setWindowTitle("Camera Setting")
        self.setGeometry(900, 450, 200, 200)

    def ip_select(self):
        if self.cam_combo.currentText() == "한화 파노라마 카메라":
            self.ADD = "rtsp://admin:sijung5520@192.168.100.121/profile2/media.smp"
            self.camname = "HANHWA Panoramic Camera"
            print(f"Success! \nADD = {self.ADD}\nCamera name = {self.camname}")
        if self.cam_combo.currentText() == "한화 IP카메라":
            self.ADD = "rtsp://admin:G85^mdPzCXr2@192.168.100.115/profile2/media.smp"
            self.camname = "HANHWA IP Camera"
            print(f"Success! \nADD = {self.ADD}\nCamera name = {self.camname}")
        if self.cam_combo.currentText() == "코맥스 PTZ 카메라":
            self.ADD = "rtsp://admin:1234@192.168.100.251/profile2/media.smp"
            self.camname = "COMMAX PTZ Camara"
            print(f"Success! \nADD = {self.ADD}\nCamera name = {self.camname}")
        self.close()


def main():
    app = QApplication(sys.argv)
    ex = pyqt_ipcam()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
