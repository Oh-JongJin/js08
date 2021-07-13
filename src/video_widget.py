# !/usr/bin/env python3
#
# Copyright 2020-21 Sijung Co., Ltd.
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)


from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import QRectF, Qt, QUrl, pyqtSlot
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem, QVideoWidget

VIDEO_SRC1 = "rtsp://admin:sijung5520@d617.asuscomm.com:1554/profile2/media.smp"
VIDEO_SRC2 = "rtsp://admin:sijung5520@d617.asuscomm.com:2554/profile2/media.smp"
VIDEO_SRC3 = "rtsp://admin:sijung5520@d617.asuscomm.com:3554/profile2/media.smp"

class Js06VideoWidget2(QWidget):
    def __init__(self, parent=None):
        super(Js06VideoWidget2, self).__init__(parent)
        
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        self.rect_item = QGraphicsRectItem(QRectF(50, 50, 40, 40), self.video_item)
        self.rect_item.setBrush(QBrush(Qt.green))
        self.rect_item.setPen(QPen(Qt.red))

        self.player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self.player.stateChanged.connect(self.on_stateChanged)
        self.player.setVideoOutput(self.video_item)
        self.player.setMedia(QMediaContent(QUrl(VIDEO_SRC2)))
        self.player.setPosition(0)
        self.player.play()

        self.resize(640, 480)
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
    # end of __init__

    @pyqtSlot(QMediaPlayer.State)
    def on_stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.view.fitInView(self.video_item, Qt.KeepAspectRatio)
    # end of on_stateChanged
# end of VideoWidget2

class Js06VideoWidget(QWidget):
    def __init__(self, parent=None):
        super(Js06VideoWidget, self).__init__(parent)
        self._viewer = QVideoWidget() # self is required?
        self._player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self._player.setVideoOutput(self._viewer)
        # self._player.setMedia(QMediaContent(QUrl(VIDEO_SRC3)))
        self._player.setPosition(0) # Required?
        self._viewer.show()
        # self._player.play()
        layout = QVBoxLayout(self)
        layout.addWidget(self._viewer)
    # end of __init__

    @pyqtSlot(str)
    def onCameraChange(self, url):
        self._player.setMedia(QMediaContent(QUrl(url)))
        self._player.play()
    # end of onCameraChange
# end of VideoPlayer

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Js06VideoWidget()
    window.show()
    sys.exit(app.exec_())
# end of video_widget.py
