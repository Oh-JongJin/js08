#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

from PyQt5.QtCore import Qt, QUrl, pyqtSlot
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem

VIDEO_SRC1 = "rtsp://admin:sijung5520@d617.asuscomm.com:1554/profile2/media.smp"
VIDEO_SRC2 = "rtsp://admin:sijung5520@d617.asuscomm.com:2554/profile2/media.smp"
VIDEO_SRC3 = "rtsp://admin:sijung5520@d617.asuscomm.com:3554/profile2/media.smp"

class Js06VideoWidget2(QWidget):
    def __init__(self, parent=None):
        super(Js06VideoWidget2, self).__init__(parent)

        # self.blank_lbl = QLabel()
        self.scene = QGraphicsScene(self)
        self.graphicView = QGraphicsView(self.scene)
        self.graphicView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        # self.rect_item = QGraphicsRectItem(QRectF(50, 50, 40, 40), self.video_item)
        # self.rect_item.setBrush(QBrush(Qt.green))
        # self.rect_item.setPen(QPen(Qt.red))

        self._player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        # self._player.stateChanged.connect(self.onCameraChange)
        self._player.setVideoOutput(self.video_item)
        # self._player.setMedia(QMediaContent(QUrl(VIDEO_SRC3)))
        self._player.setPosition(0)

        layout = QVBoxLayout(self)
        layout.addWidget(self.graphicView)

        # self.qtimer = QTimer()
        # self.qtimer.setInterval(2000)
        # self.qtimer.timeout.connect(self.inference)
        # self.qtimer.start()
    # end of __init__

    @pyqtSlot(QMediaPlayer.State)
    def on_stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.view.fitInView(self.video_item, Qt.KeepAspectRatio)
    # end of on_stateChanged

    @pyqtSlot(str)
    def onCameraChange(self, url):
        self._player.setMedia(QMediaContent(QUrl(url)))
        self._player.play()
        # self.graphicView.fitInView(self.video_item)
    # end of onCameraChange

    def inference(self):
        self.graphicView.fitInView(self.video_item)
    # end fo inference

# end of VideoWidget2

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Js06VideoWidget2()
    window.show()
    sys.exit(app.exec_())

# end of video_widget_2.py
