#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import time
import os
import traceback

import cv2
import numpy as np
import pandas as pd
from video_thread import VideoThread

from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QUrl, pyqtSlot, QTimer
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QVBoxLayout, QLabel
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem

VIDEO_SRC1 = "rtsp://admin:sijung5520@d617.asuscomm.com:1554/profile2/media.smp"
VIDEO_SRC2 = "rtsp://admin:sijung5520@d617.asuscomm.com:2554/profile2/media.smp"
VIDEO_SRC3 = "rtsp://admin:sijung5520@d617.asuscomm.com:3554/profile2/media.smp"
VIDEO_SRC4 = "rtsp://admin:sijung5520@d617.asuscomm.com:4554/profile2/media.smp"
VIDEO_SRC5 = "rtsp://admin:sijung5520@d617.asuscomm.com:5554/profile2/media.smp"


class Js06VideoWidget2(QWidget):
    """Video stream player using QGraphicsVideoItem
    """
    def __init__(self, parent=None):
        super(Js06VideoWidget2, self).__init__(parent)

        self.target = []
        self.prime_x = []
        self.prime_y = []
        self.target_x = []
        self.target_y = []
        self.label_x = []
        self.label_y = []
        self.distance = []
        self.oxlist = []

        self.scene = QGraphicsScene(self)
        self.graphicView = QGraphicsView(self.scene)
        self.graphicView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)

        self.player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.video_item)
        self.player.setPosition(0)

        layout = QVBoxLayout(self)
        layout.addWidget(self.graphicView)
        self.camera_name = None

        self.crop_imagelist100 = None
        self.horizontal_flag = False

        self.blank_lbl = QLabel(self)

        self.qtimer = QTimer()
        self.qtimer.setInterval(2000)
        self.qtimer.timeout.connect(self.inference_clicked)
        self.qtimer.start()

        self.filepath = os.path.join(os.getcwd(), "target")
        try:
            os.makedirs(self.filepath, exist_ok=True)
        except OSError:
            pass
    # end of __init__

    def paintEvent(self, event):
        qp = QPainter(self.blank_lbl)
        if self.target_x:
            for name, x, y in zip(self.target, self.label_x, self.label_y):
                if self.oxlist[self.label_x.index(x)] == 0:
                    qp.setPen(QPen(Qt.red, 2))
                else:
                    qp.setPen(QPen(Qt.green, 2))
                qp.drawRect(int(x - (25 / 4)), int(y - (25 / 4)), 25 / 2, 25 / 2)
                qp.drawText(x - 4, y - 10, f"{int(name) - 1}")
    # end of paintEvent

    @pyqtSlot(QMediaPlayer.State)
    def on_stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.view.fitInView(self.video_item, Qt.KeepAspectRatio)
    # end of on_stateChanged

    @pyqtSlot(str)
    def onCameraChange(self, url):
        self.player.setMedia(QMediaContent(QUrl(url)))
        self.player.play()
        self.blank_lbl.paintEvent = self.paintEvent
        self.blank_lbl.raise_()

        if url == VIDEO_SRC3:
            self.camera_name = "XNO-8080R"
        print(self.camera_name)
        self.get_target()

        self.video_thread = VideoThread(url)
        self.video_thread.update_pixmap_signal.connect(self.convert_cv_qt)
        self.video_thread.start()
    # end of onCameraChange

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        self.epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        self.restoration()

        if self.epoch[-2:] == "00":
            self.save_frame(cv_img, self.epoch)
    # end of conver_cv_qt

    def get_target(self):
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
    # end of get_target

    def save_target(self):
        if self.prime_x:
            col = ["target", "x", "y", "label_x", "label_y", "distance", "discernment"]
            self.result = pd.DataFrame(columns=col)
            self.result["target"] = self.target
            self.result["x"] = self.prime_x
            self.result["y"] = self.prime_y
            self.result["label_x"] = [round(x * self.graphicView.geometry().width() /
                                            self.video_item.nativeSize().width(), 3) for x in self.target_x]
            self.result["label_y"] = [round(y * self.graphicView.geometry().height() /
                                            self.video_item.nativeSize().height(), 3) for y in self.target_y]
            self.result["distance"] = self.distance
            self.result["discernment"] = self.oxlist
            self.result.to_csv(f"{self.filepath}/{self.camera_name}.csv", mode="w", index=False)
    # end of save_target

    def save_frame(self, image: np.ndarray, epoch: str):
        image_path = os.path.join(self.filepath, "image", f"{self.camera_name}", f"{epoch[2:6]}")
        file_name = f"{epoch}"
        if not os.path.isdir(image_path):
            os.makedirs(image_path)
        if not os.path.isfile(f"{image_path}/{file_name}.jpg"):
            cv2.imwrite(f"{image_path}/{file_name}.jpg", image)
        del image
        del image_path
        cv2.destroyAllWindows()
    # end of save_frame

    def save_target_frame(self, epoch: str):
        for i in range(len(self.target_x)):
            image_path = os.path.join(self.filepath, "image", "100x100", f"target{i + 1}")
            if not os.path.isdir(image_path):
                os.makedirs(image_path)
            if not os.path.isfile(f"{image_path}/target_{i + 1}_{epoch}.jpg"):
                b, g, r = cv2.split(self.crop_imagelist100[i])
                if self.oxlist[i] == 1:
                    cv2.imwrite(f"{image_path}/target_{i + 1}_{epoch}_Y.jpg", cv2.merge([r, g, b]))
                else:
                    cv2.imwrite(f"{image_path}/target_{i + 1}_{epoch}_N.jpg", cv2.merge([r, g, b]))
        del self.crop_imagelist100
        cv2.destroyAllWindows()
    # end of save_target_frame

    def crop_image(self, image: np.ndarray):
        new_crop_image = []
        for i in range(len(self.target_x)):
            crop_img = image[int(self.target_y[i] - 50): int(self.target_y[i] + 50),
                            int(self.target_x[i] - 50): int(self.target_x[i] + 50)]
            new_crop_image.append(crop_img)
        self.crop_imagelist100 = new_crop_image
        del image
    # end of crop_image

    def inference_clicked(self):
        self.graphicView.fitInView(self.video_item)
        self.blank_lbl.resize(self.graphicView.geometry().width(),
                              self.graphicView.geometry().height())
    # end of inference_clicked

    def coordinator(self):
        self.prime_x = [2 * x / self.video_item.nativeSize().width() - 1 for x in self.target_x]
        self.prime_y = [y / self.video_item.nativeSize().height() for y in self.target_y]
    # end of coordinator

    def restoration(self):
        try:
            if self.target:
                self.target_x = [self.f2i((x + 1) * self.video_item.nativeSize().width() / 2) for x in self.prime_x]
                self.target_y = [self.f2i(y * self.video_item.nativeSize().height()) for y in self.prime_y]
        except:
            print(traceback.format_exc())
            sys.exit()

    # end of restoration

    @staticmethod
    def f2i(num: float):
        return int(num + 0.5)
    # end of f2i

# end of VideoWidget2


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    # sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    # from ..src.video_thread import VideoThread
    # from video_thread import VideoThread

    app = QApplication(sys.argv)
    window = Js06VideoWidget2()
    window.onCameraChange(VIDEO_SRC3)
    window.show()
    sys.exit(app.exec_())

# end of video_widget_2.py
