#!/usr/bin/env python3
"""
A sample implementation of a main window for JS-06.
"""
#
# This example illustrates the following techniques:
# * Layout design using Qt Designer
# * Open RTSP video source
#
#
#
# Reference: https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1

# pylint: disable=line-too-long
# pylint: disable-msg=E0611, E1101

import os
import time
import atexit
import traceback

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt

from PIL import Image
from numpy import asarray

from PyQt5.QtGui import QColor, QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QTimer, QUrl, QPoint
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QTableWidget, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from cv2 import VideoCapture, imwrite, destroyAllWindows

# from save_db import SaveDB
from main_window import Ui_MainWindow
from tflite_thread import TfliteThread
from videoframe_saver import VideoSaveFrame


def ErrorLog(error: str):
    current_time = time.strftime("%Y.%m.%d/%H:%M:%S", time.localtime(time.time()))
    cur_day = time.strftime("%m%d", time.localtime(time.time()))
    with open(f"Log/{cur_day}.txt", "a") as f:
        f.write(f"[{current_time}] - {error}\n")


class Js06MainWindow(Ui_MainWindow):
    """JS06 main window"""

    def __init__(self):
        super().__init__()
        self.target = []
        self.prime_x = []
        self.prime_y = []
        self.target_x = []
        self.target_y = []
        self.label_x = []
        self.label_y = []
        self.distance = []
        self.oxlist = []

        self.camera_name = ""
        self.crop_imagelist100 = []
        self.target_process = False
        self.tflite_thread = None
        self.visibility = 0
        self.qtimer = None
        self.vis_km = 0
        self.result = None
        self.crop_img = None

        self.save_DB = None

        self.epoch = None

        # Draw target
        self.painter = None

        # Required for Target Plot function
        self._plot_ref_red = None
        self._plot_ref_green = None
        self.annotate = None
        self.ylabel = None
        self.xlabel = None

        self.fig = None
        self.canvas = None
        self.axes = None

        # TODO(Kyungwon): Set adequate action for the exception.
        self.filepath = os.path.join(os.getcwd(), "target")
        self.filepath_log = os.path.join(os.getcwd(), "Log")
        try:
            os.startfile("influxd.exe")
            os.makedirs(self.filepath, exist_ok=True)
            os.makedirs(self.filepath_log, exist_ok=True)
        except OSError:
            pass

    def setupUi(self, MainWindow: QMainWindow):
        try:
            super().setupUi(MainWindow)
            # webEngineView 위젯에 아래의 주소(Grafana)로 이동
            self.webEngineView.load(
                QUrl(
                    "http://localhost:3000/d/TWQ9hKoGz/visibility?orgId=1&from=now-2h-30m&to=now%2B5m&refresh=5s&kiosk"
                ))
            self.open_PNM()
            self.update_plot()

            self.actionEdit_target.triggered.connect(self.target_mode)
            self.horizontalLayout.addWidget(self.canvas, 0)
            self.horizontalLayout.addWidget(self.webEngineView, 1)

            # Event
            self.blank_lbl.raise_()

            # self.blank_lbl.wheelEvent = self.wheelEvent
            self.blank_lbl.mousePressEvent = self.mousePressEvent
            self.blank_lbl.paintEvent = self.paintEvent

            self.actionSaveframe.triggered.connect(self.save_frame)

        except:
            err = traceback.format_exc()
            ErrorLog(str(err))

    def update_plot(self):
        """Update Target Plot with read information."""
        try:
            self.fig = plt.Figure(figsize=(5, 4), dpi=100, facecolor=(0.9686, 0.9725, 0.9803), tight_layout=False)
            self.fig.suptitle("Target Distribution")
            self.canvas = FigureCanvas(self.fig)
            self.axes = self.fig.add_subplot(111, projection='polar')
            pi = np.pi
            self.axes.set_thetamin(-90)
            self.axes.set_thetamax(90)
            self.axes.set_xticks([-pi / 2, -pi / 6, -pi / 3, 0, pi / 6, pi / 3, pi / 2])
            self.axes.set_theta_zero_location("N")
            self.axes.set_theta_direction(-1)
            self.ylabel = self.axes.set_ylabel("(km)", fontsize=7)
            self.ylabel.set_position((2, 0.2))
            self.ylabel.set_rotation(45)
            plt.rcParams.update({'font.size': 7})

            plot_x = np.array(self.prime_x) * np.pi / 2

            # Clear Target Plot canvas and redraw.
            self.axes.clear()
            self.plot_canvas()

            for i, xy in enumerate(zip(plot_x, self.distance), start=0):
                self.annotate = self.axes.annotate(i + 1, xy)
                if self.oxlist[i] == 0:
                    self._plot_ref_red, = self.axes.plot(plot_x[i], self.distance[i], 'ro')
                else:
                    self._plot_ref_green, = self.axes.plot(plot_x[i], self.distance[i], 'go')

            self.canvas.draw()

        except Exception:
            err = traceback.format_exc()
            ErrorLog(str(err))

    def plot_canvas(self):
        """Target Plot Axes"""
        try:
            pi = np.pi

            self.axes.set_thetamin(-90)
            self.axes.set_thetamax(90)
            self.axes.set_xticks([-pi / 2, -pi / 6, -pi / 3, 0, pi / 6, pi / 3, pi / 2])
            self.axes.set_theta_zero_location("N")
            self.axes.set_theta_direction(-1)
            self.ylabel = self.axes.set_ylabel("(km)", fontsize=7)
            self.ylabel.set_position((2, 0.2))
            self.ylabel.set_rotation(45)
            self.xlabel = self.axes.set_xlabel(f"Visibility: {self.visibility}", fontsize=20)
            plt.rcParams.update({'font.size': 7})
        except:
            err = traceback.format_exc()
            ErrorLog(str(err))

    def closeEvent(self, event):
        """Window close event"""
        print("DEBUG: ", type(event))
        event.accept()

    def open_PNM(self):
        """Get video from Hanwha PNM-9030V"""
        self.camera_name = "PNM-9030V"

        # create the video capture thread
        self.player.setMedia(QMediaContent(QUrl("rtsp://admin:sijung5520@192.168.100.100/profile2/media.smp")))
        self.player.play()
        # self.blank_lbl.setStyleSheet("background-color: #000000")
        # self.blank_lbl.raise_()
        self.menubar.raise_()

        self.get_target()

        self.qtimer = QTimer()
        self.qtimer.setInterval(1000)
        self.qtimer.timeout.connect(self.inference_clicked)
        self.qtimer.start()

    def wheelEvent(self, event):
        print("wheel")
        event.ignore()

    def paintEvent(self, event):
        self.painter = QPainter(self.blank_lbl)
        self.draw_rect(self.painter)
        self.painter.end()

    def draw_rect(self, qp):
        if self.target_x:
            # qp = qp1
            qp.setPen(QPen(Qt.red, 1.5))
            for name, x, y in zip(self.target, self.label_x, self.label_y):
                qp.drawRect(x - (25 / 4), y - (25 / 4), 25 / 2, 25 / 2)
                # qp1.drawText(QPoint(x - (25 / 8), y), "12")

    def mousePressEvent(self, event):
        try:
            x = int(event.pos().x() / self.graphicView.geometry().width() * self.videoWidget.nativeSize().width())
            y = int(event.pos().y() / self.graphicView.geometry().height() * self.videoWidget.nativeSize().height())

            for i in range(len(self.target)):
                self.target[i] = i + 1

            if not self.target_process:
                return

            if event.buttons() == Qt.LeftButton:
                text, ok = QInputDialog.getText(self.centralwidget, '거리 입력', '거리 (km)')
                if ok:
                    self.target_x.append(x)
                    self.target_y.append(y)
                    self.distance.append(float(text))
                    self.target.append(str(len(self.target_x)))
                    self.oxlist.append(0)
                    print(f"영상목표 위치: {self.target_x[-1]}, {self.target_y[-1]}")
                    self.coordinator()
                    self.save_target()
                    self.get_target()

            if event.buttons() == Qt.RightButton:
                text, ok = QInputDialog.getText(self.centralwidget, '타겟 입력', '제거할 타겟 번호 입력')
                text = int(text)
                if ok:
                    if len(self.prime_x) >= 1:
                        del self.target[text - 1]
                        del self.prime_x[text - 1]
                        del self.prime_y[text - 1]
                        del self.label_x[text - 1]
                        del self.label_y[text - 1]
                        del self.distance[text - 1]
                        del self.oxlist[text - 1]
                        self.save_target()
                        self.get_target()
                        print(f"타겟 {text}번을 제거했습니다.")

        except AttributeError:
            pass

        except ValueError:
            print("거리 입력 값이 잘못되었습니다.")
            pass

    def target_mode(self):
        """목표 영상 수정 모드를 설정한다."""
        try:
            if self.target_process:
                self.target_process = False

            else:
                self.target_process = True
                self.actionInference.setChecked(False)
                if self.tflite_thread is not None:
                    self.tflite_thread.stop()
                    self.tflite_thread = None
                print("타겟 설정 모드로 전환합니다.")
                self.save_target()

            return self.target_process

        except:
            err = traceback.format_exc()
            ErrorLog(str(err))

    def get_target(self):
        """Read target information from a file"""
        try:
            # self.target = []
            # self.prime_x = []
            # self.prime_y = []
            # self.target_x = []
            # self.target_y = []
            # self.distance = []
            # self.oxlist = []

            if os.path.isfile(f"target/{self.camera_name}.csv"):
                result = pd.read_csv(f"target/{self.camera_name}.csv")
                self.target = result.target.tolist()
                self.prime_x = result.x.tolist()
                self.prime_y = result.y.tolist()
                self.label_x = result.label_x.tolist()
                self.label_y = result.label_y.tolist()
                self.distance = result.distance.tolist()
                self.oxlist = [0 for i in range(len(self.prime_x))]
                print("영상목표를 불러옵니다.")
            else:
                print("csv 파일을 불러올 수 없습니다.")

        except AttributeError:
            err = traceback.format_exc()
            ErrorLog(str(err))

            # TODO: This code have to delete after catch errors.
            # os.remove(f"target/{self.camera_name}.csv")

    def save_target(self):
        """Save the target information for each camera."""
        try:
            if self.prime_x:
                col = ["target", "x", "y", "label_x", "label_y", "distance", "discernment"]
                self.result = pd.DataFrame(columns=col)
                self.result["target"] = self.target
                self.result["x"] = self.prime_x
                self.result["y"] = self.prime_y
                self.result["label_x"] = [round(x * self.graphicView.geometry().width() /
                                          self.videoWidget.nativeSize().width(), 3) for x in self.target_x]
                self.result["label_y"] = [round(y * self.graphicView.geometry().height() /
                                          self.videoWidget.nativeSize().height(), 3) for y in self.target_y]
                self.result["distance"] = self.distance
                self.result["discernment"] = self.oxlist
                self.result.to_csv(f"{self.filepath}/{self.camera_name}.csv", mode="w", index=False)
        except:
            err = traceback.format_exc()
            ErrorLog(str(err))

    def coordinator(self):
        """영상목표의 좌표값을 -1~1 값으로 정규화한다."""
        try:
            self.prime_y = [y / self.videoWidget.nativeSize().height() for y in self.target_y]
            self.prime_x = [2 * x / self.videoWidget.nativeSize().width() - 1 for x in self.target_x]
        except:
            err = traceback.format_exc()
            ErrorLog(str(err))

    def restoration(self):
        """정규화한 값을 다시 복구한다."""
        try:
            self.target_x = [self.f2i((x + 1) * self.videoWidget.nativeSize().width() / 2) for x in self.prime_x]
            self.target_y = [self.f2i(y * self.videoWidget.nativeSize().height()) for y in self.prime_y]
        except:
            err = traceback.format_exc()
            ErrorLog(str(err))

    def conversion(self):
        """Label 좌표 값을 저장한다."""
        try:
            # self.label_x = []
            pass
        except:
            err = traceback.format_exc()
            ErrorLog(str(err))

    @staticmethod
    def f2i(num: float):
        """float형 숫자를 0.5를 더하고 정수형으로 바꿔준다."""
        try:
            return int(num + 0.5)
        except:
            err = traceback.format_exc()
            ErrorLog(str(err))

    def mqtt_send(self, msg: str):
        """MQTT를 사용하여 원격 시정 서버에 메시지를 보낸다."""
        try:
            send = mqtt.Client("test")
            send.connect("121.159.74.131", 1883)
            send.publish('sitemqtt', msg)
            send.loop_stop()
            send.disconnect()
            time.sleep(1)
        except Exception as e:
            print(e)

    def save_frame(self):
        try:
            image_path = os.path.join(self.filepath, "image", "PNM", f"{self.epoch[2:6]}")
            fileName = f"{self.epoch}"

            cap = VideoCapture('rtsp://admin:sijung5520@192.168.100.100/profile2/media.smp')
            if not cap.isOpened():
                sys.exit()
            ret, img = cap.read()
            if not os.path.isdir(image_path):
                os.makedirs(image_path)
            if not os.path.isfile(f"{image_path}/{fileName}.png"):
                imwrite(f'{image_path}/{fileName}.png', img)
            cap.release()
            destroyAllWindows()
        except Exception:
            err = traceback.format_exc()
            print(err)
            sys.exit()

    def crop_image(self):
        """영상목표를 100x100으로 잘라내 리스트로 저장하고, 리스트를 tflite_thread 에 업데이트 한다."""
        try:
            new_crop_image = []
            # 영상목표를 100x100으로 잘라 리스트에 저장한다.
            for i in range(len(self.target_x)):
                pass
                # self.crop_img = image[self.target_y[i] - 50: self.target_y[i] + 50,
                #                 self.target_x[i] - 50: self.target_x[i] + 50]
                # new_crop_image.append(self.crop_img)

            self.crop_imagelist100 = new_crop_image

            # tflite_thread가 작동시 tflite_thread에 영상목표 리스트를 업데이트한다.
            if self.actionInference.isChecked() and self.tflite_thread is not None:
                self.tflite_thread.crop_imagelist100 = new_crop_image
        except:
            err = traceback.format_exc()
            # ErrorLog(str(err))
            print(err)

    def inference_clicked(self):
        """모델 쓰레드를 제어한다."""
        try:
            self.epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            if self.epoch[-2:] == "00":
                self.save_frame()
            self.graphicView.fitInView(self.videoWidget)
            self.update_plot()
            self.restoration()
            self.crop_image()
            self.blank_lbl.resize(self.graphicView.geometry().width(), self.graphicView.geometry().height())

            # print("blank_lbl size: ", self.blank_lbl.width(), self.blank_lbl.height())

            if self.actionInference.isChecked():
                self.actionEdit_target.setChecked(False)
                self.target_process = False

                if self.tflite_thread is None:
                    if not self.prime_x:
                        return
                    print("모델적용을 시작합니다.")
                    self.tflite_thread = TfliteThread(self.crop_imagelist100)
                    self.tflite_thread.run_flag = True
                    self.tflite_thread.update_oxlist_signal.connect(self.get_visiblity)
                    self.tflite_thread.start()

            else:
                if self.tflite_thread is None:
                    return
                if self.tflite_thread.run_flag:
                    print("모델적용을 중지합니다.")
                    self.tflite_thread.stop()
                    self.tflite_thread = None

        except:
            err = traceback.format_exc()
            ErrorLog(str(err))

    def get_visiblity(self, oxlist):
        """크롭한 이미지들을 모델에 돌려 결과를 저장하고 보이는것들 중 가장 먼 거리를 출력한다."""
        try:
            res = [self.distance[x] for x, y in enumerate(oxlist) if y == 1]
            self.vis_km = max(res)

            if res is None:
                self.vis_km = 0
            elif res:
                self.vis_km = round(max(res), 2)
                self.visibility = str(self.vis_km) + " km"

            self.oxlist = oxlist
            self.save_target()

            return self.oxlist

        except ValueError:
            err = traceback.format_exc()
            ErrorLog(str(err))
            pass


def Bye():
    os.system("TASKKILL /F /IM influxd.exe")


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Js06MainWindow()  # pylint: disable-msg=I1101
    ui.setupUi(MainWindow)
    MainWindow.show()
    atexit.register(Bye)
    sys.exit(app.exec_())
