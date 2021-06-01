# !/usr/bin/env python3
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

from pytest import ExitCode
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from cv2 import imwrite, destroyAllWindows, cvtColor, COLOR_BGR2RGB, split, merge

from save_db import SaveDB
from video_thread import VideoThread
from main_window import Ui_MainWindow
from tflite_thread import TfliteThread


def error_log(error: str):
    """If occur error, run this function"""
    current_time = time.strftime("%Y.%m.%d/%H:%M:%S", time.localtime(time.time()))
    cur_day = time.strftime("%m%d", time.localtime(time.time()))
    with open(f"Log/{cur_day}.txt", "a") as txt:
        txt.write(f"[{current_time}] - {error}\n")


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
        self.video_thread = None
        self.crop_imagelist100 = []
        self.target_process = False
        self.tflite_thread = None
        self.visibility = 0
        self.qtimer = None
        self.vis_km = 0
        self.vis_m = 0
        self.result = None
        self.crop_img = None

        self.save_db = None

        self.epoch = None
        self.list_flag = False

        # Draw target
        self.painter = None

        # Required for Target Plot function
        self._plot_ref_red = None
        self._plot_ref_green = None
        self.annotate = None
        self.ylabel = None
        self.xlabel = None

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
                    "http://localhost:3000/d/TWQ9hKoGz/visibility?orgId=1&from=now-3h&to=now&refresh=5s&kiosk"
                ))
            self.open_cam()
            self.update_plot()

            self.actionEdit_target.triggered.connect(self.target_mode)
            self.horizontalLayout.addWidget(self.canvas, 0)
            self.horizontalLayout.addWidget(self.webEngineView, 1)

            # Event
            self.blank_lbl.mousePressEvent = self.mousePressEvent
            self.blank_lbl.mouseDoubleClickEvent = self.test
            self.blank_lbl.paintEvent = self.paintEvent
        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    def list_btn_click(self):
        try:
            print(self.graphicView.geometry().width(), self.graphicView.geometry().height())
            if self.list_flag is False:
                self.list_btn.setGeometry(1440, 40, 60, 30)
                self.list_btn.setText("List")
                self.tableWidget.setVisible(True)
                self.graphicView.resize(1920, 578)
                self.list_flag = True

            elif self.list_flag is True:
                self.list_btn.setGeometry(1836, 40, 60, 30)
                self.list_btn.setText("Hide")
                self.tableWidget.setVisible(True)
                self.list_flag = False
        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    def test(self, event):
        try:
            QMessageBox.information(self.centralwidget, 'Info',
                                    f'QGraphicsView.size:               {self.graphicView.size().width(), self.graphicView.size().height()}\n'
                                    f'QGraphicsVideoItem.size:          {self.videoWidget.size().width(), self.videoWidget.size().height()}\n'
                                    f'QGraphicsVideoItem.nativeSize:    {self.videoWidget.nativeSize().width(), self.videoWidget.nativeSize().height()}')
        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    def update_plot(self):
        """Update Target Plot with read information."""
        try:
            plot_x = np.array(self.prime_x) * np.pi / 2

            # Clear Target Plot canvas and redraw.
            self.axes.clear()
            self.plot_canvas()

            # pylint: disable=invalid-name
            for i, xy in enumerate(zip(plot_x, self.distance), start=0):
                if self.oxlist[i] == 0:
                    self._plot_ref_red, = self.axes.plot(plot_x[i], self.distance[i], 'ro')
                else:
                    self._plot_ref_green, = self.axes.plot(plot_x[i], self.distance[i], 'go')

            self.canvas.draw()

            if self.save_db is not None:
                self.save_db.c_visibility = self.vis_m

        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

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
        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    def open_cam(self):
        """Get video from Hanwha PNM-9030V"""
        self.camera_name = "PNM-9030V"

        # Create the video capture thread
        self.player.setMedia(QMediaContent(QUrl("rtsp://admin:sijung5520@192.168.100.100/profile2/media.smp")))
        self.player.play()
        self.blank_lbl.raise_()

        self.video_thread = VideoThread("rtsp://admin:sijung5520@192.168.100.100/profile2/media.smp")
        self.video_thread.update_pixmap_signal.connect(self.convert_cv_qt)
        self.video_thread.start()

        self.get_target()

        self.qtimer = QTimer()
        self.qtimer.setInterval(2000)
        self.qtimer.timeout.connect(self.inference_clicked)
        self.qtimer.start()

    def convert_cv_qt(self, cv_img):
        try:
            rpg_image = cvtColor(cv_img, COLOR_BGR2RGB)
            self.crop_image(rpg_image)
            self.epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            self.restoration()

            if self.epoch[-2:] == "00":
                self.save_frame(cv_img, self.epoch)
                self.save_target_frame(self.epoch)
        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    def paintEvent(self, event):
        self.painter = QPainter(self.blank_lbl)
        self.draw_rect(self.painter)
        self.painter.end()

    def draw_rect(self, qp):
        if self.target_x:
            for name, x, y in zip(self.target, self.label_x, self.label_y):
                if self.oxlist[self.label_x.index(x)] == 0:
                    qp.setPen(QPen(Qt.red, 2))
                else:
                    qp.setPen(QPen(Qt.green, 2))
                qp.drawRect(x - (25 / 4), y - (25 / 4), 25 / 2, 25 / 2)
                qp.drawText(x - 4, y - 10, f"{name}")

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
                # pylint: disable=invalid-name
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
                        print(f"타겟 {text}번을 제거했습니다.")
                        self.save_target()

                    else:
                        print("제거할 영상목표가 없습니다.")

        except AttributeError:
            pass

        except ValueError:
            print("거리 입력 값이 잘못되었습니다.")

    def target_mode(self):
        """목표 영상 수정 모드를 설정한다."""
        try:
            if self.target_process:
                self.target_process = False
                self.save_target()

            else:
                self.target_process = True
                self.actionInference.setChecked(False)
                if self.tflite_thread is not None:
                    self.tflite_thread.stop()
                    self.tflite_thread = None
                print("타겟 설정 모드로 전환합니다.")
                self.save_target()

            return self.target_process

        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    def get_target(self):
        """Read target information from a file"""
        try:
            if os.path.isfile(f"target/{self.camera_name}.csv"):
                print(self.camera_name)
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
            error_log(str(err))

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
        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    def coordinator(self):
        """영상목표의 좌표값을 -1~1 값으로 정규화한다."""
        try:
            self.prime_y = [y / self.videoWidget.nativeSize().height() for y in self.target_y]
            self.prime_x = [2 * x / self.videoWidget.nativeSize().width() - 1 for x in self.target_x]
        except:
            err = traceback.format_exc()
            error_log(str(err))

    def restoration(self):
        """정규화한 값을 다시 복구한다."""
        try:
            self.target_x = [self.f2i((x + 1) * self.videoWidget.nativeSize().width() / 2) for x in self.prime_x]
            self.target_y = [self.f2i(y * self.videoWidget.nativeSize().height()) for y in self.prime_y]
        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    @staticmethod
    def f2i(num: float):
        """float형 숫자를 0.5를 더하고 정수형으로 바꿔준다."""
        try:
            return int(num + 0.5)
        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    def save_target_frame(self, epoch: str):
        """Save 100x100 target frame in camera image"""
        try:
            for i in range(len(self.target_x)):
                print(i)
                image_path = os.path.join(self.filepath, "image", "100x100", f"target{i + 1}")
                if not os.path.isdir(image_path):
                    os.makedirs(image_path)
                if not os.path.isfile(f"{image_path}/target_{i + 1}_{epoch}.jpg"):
                    b, g, r = split(self.crop_imagelist100[i])
                    if self.oxlist[i] == 1:
                        imwrite(f"{image_path}/target_{i + 1}_{epoch}_Y.jpg", merge([r, g, b]))
                    else:
                        imwrite(f"{image_path}/target_{i + 1}_{epoch}_N.jpg", merge([r, g, b]))
            del self.crop_imagelist100
            destroyAllWindows()
        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    def save_frame(self, image: np.ndarray, epoch: str):
        """Save frame in camera image"""
        try:
            image_path = os.path.join(self.filepath, "image", "PNM", f"{epoch[2:6]}")
            file_name = f"{epoch}_{self.vis_m}"
            if not os.path.isdir(image_path):
                os.makedirs(image_path)
            if not os.path.isfile(f"{image_path}/{file_name}.jpg"):
                imwrite(f'{image_path}/{file_name}.jpg', image)
            del image
            del image_path
            destroyAllWindows()

        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    def crop_image(self, image: np.ndarray):
        """영상목표를 100x100으로 잘라내 리스트로 저장하고, 리스트를 tflite_thread 에 업데이트 한다."""
        try:
            new_crop_image = []
            # 영상목표를 100x100으로 잘라 리스트에 저장한다.
            for i in range(len(self.target_x)):
                self.crop_img = image[self.target_y[i] - 50: self.target_y[i] + 50,
                                self.target_x[i] - 50: self.target_x[i] + 50]
                new_crop_image.append(self.crop_img)

            self.crop_imagelist100 = new_crop_image

            # tflite_thread가 작동시 tflite_thread에 영상목표 리스트를 업데이트한다.
            if self.actionInference.isChecked() and self.tflite_thread is not None:
                self.tflite_thread.crop_imagelist100 = new_crop_image
            del image
        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    def inference_clicked(self):
        """모델 쓰레드를 제어한다."""
        try:
            self.graphicView.fitInView(self.videoWidget)
            self.blank_lbl.resize(self.graphicView.geometry().width(), self.graphicView.geometry().height())

            if self.actionInference.isChecked():
                self.actionEdit_target.setChecked(False)
                self.update_plot()

                self.target_process = False

                if self.tflite_thread is None:
                    if not self.prime_x:
                        return
                    print("모델적용을 시작합니다.")
                    self.tflite_thread = TfliteThread(self.crop_imagelist100)
                    self.tflite_thread.run_flag = True
                    self.tflite_thread.update_oxlist_signal.connect(self.get_visibility)
                    self.tflite_thread.start()

                    self.save_db = SaveDB()
                    if not self.save_db.flag:
                        self.save_db.flag = True
                        self.save_db.start()

            else:
                if self.tflite_thread is None:
                    return
                if self.tflite_thread.run_flag:
                    print("모델적용을 중지합니다.")
                    self.tflite_thread.stop()
                    self.tflite_thread = False

                    if self.save_db.flag:
                        self.save_db.stop()
                        self.save_db.flag = False
                        self.save_db = None

        except:  # pylint: disable=bare-except
            err = traceback.format_exc()
            error_log(str(err))

    def get_visibility(self, oxlist):
        """크롭한 이미지들을 모델에 돌려 결과를 저장하고 보이는것들 중 가장 먼 거리를 출력한다."""
        try:
            res = [self.distance[x] for x, y in enumerate(oxlist) if y == 1]
            self.vis_km = max(res)

            if res is None:
                self.vis_km = 0
            elif res:
                self.vis_km = round(max(res), 2)
                self.vis_m = int(self.vis_km * 1000)
                self.visibility = str(self.vis_km) + " km"

            self.oxlist = oxlist
            self.save_target()

            return self.oxlist

        except ValueError:
            err = traceback.format_exc()
            error_log(str(err))
            pass


def close_func():
    os.system("TASKKILL /F /IM influxd.exe")


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 5:
        session.exitstatus = 10


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Js06MainWindow()  # pylint: disable-msg=I1101
    ui.setupUi(MainWindow)
    MainWindow.show()
    atexit.register(close_func)
    sys.exit(app.exec_())
