#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

VIDEO_SRC1 = "rtsp://admin:sijung5520@d617.asuscomm.com:1554/profile2/media.smp"
VIDEO_SRC2 = "rtsp://admin:sijung5520@d617.asuscomm.com:2554/profile2/media.smp"
VIDEO_SRC3 = "rtsp://admin:sijung5520@d617.asuscomm.com:3554/profile2/media.smp"
VIDEO_SRC4 = "rtsp://admin:sijung5520@d617.asuscomm.com:4554/profile2/media.smp"
VIDEO_SRC5 = "rtsp://admin:sijung5520@d617.asuscomm.com:5554/profile2/media.smp"

class Js06VideoWidget(QWidget):
    """Video stream player using QVideoWidget
    """
    def __init__(self, parent=None):
        super(Js06VideoWidget, self).__init__(parent)
        self.viewer = QVideoWidget()  # self is required?
        self.player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.viewer)
        self.player.setPosition(0)  # Required?
        self.viewer.show()
        layout = QVBoxLayout(self)
        layout.addWidget(self.viewer)
        self.viewer.setGeometry(0, 0, 100, 100)

        self.viewer.mousePressEvent = self.viewer_mousePressEvent
    # end of __init__

    @pyqtSlot(str)
    def onCameraChange(self, url):
        self.player.setMedia(QMediaContent(QUrl(url)))
        self.player.play()
    # end of onCameraChange

    def viewer_mousePressEvent(self, event):
        print(event.pos())
        print(f"videoWidget: {self.viewer.sizeHint()}")
        # self.resize(self.viewer.sizeHint().width(), self.viewer.sizeHint().height())
        # self.resize(300, 300)
    # end of viewer_mousePressEvent

# end of VideoPlayer

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Js06VideoWidget()
    window.player.setMedia(QMediaContent(QUrl(VIDEO_SRC5)))
    window.player.play()
    window.show()
    sys.exit(app.exec_())

# end of video_widget.py
