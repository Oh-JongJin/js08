#!/usr/bin/env python3

import sys
# from builtins import __namedtuple

from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt, QObject, QRect, QPoint, pyqtSignal, QThread
from PyQt5.QtWidgets import QWidget
from PyQt5.QtMultimedia import QAbstractVideoSurface, QVideoSurfaceFormat, QAbstractVideoBuffer, QVideoFrame


# class VideoSaveFrame(QThread):
class VideoSaveFrame(QAbstractVideoSurface):
    frameAvailable = pyqtSignal(QImage)

    def __init__(self, widget: QWidget, parent: QObject):
        super().__init__(parent)

        self.widget = widget
        self.currentFrame = None

    def supportedPixelFormats(self, handleType):
        return [QVideoFrame.Format_ARGB32, QVideoFrame.Format_ARGB32_Premultiplied,
                QVideoFrame.Format_RGB32, QVideoFrame.Format_RGB24, QVideoFrame.Format_RGB565,
                QVideoFrame.Format_RGB555, QVideoFrame.Format_ARGB8565_Premultiplied,
                QVideoFrame.Format_BGRA32, QVideoFrame.Format_BGRA32_Premultiplied, QVideoFrame.Format_BGR32,
                QVideoFrame.Format_BGR24, QVideoFrame.Format_BGR565, QVideoFrame.Format_BGR555,
                QVideoFrame.Format_BGRA5658_Premultiplied, QVideoFrame.Format_AYUV444,
                QVideoFrame.Format_AYUV444_Premultiplied, QVideoFrame.Format_YUV444,
                QVideoFrame.Format_YUV420P, QVideoFrame.Format_YV12, QVideoFrame.Format_UYVY,
                QVideoFrame.Format_YUYV, QVideoFrame.Format_NV12, QVideoFrame.Format_NV21,
                QVideoFrame.Format_IMC1, QVideoFrame.Format_IMC2, QVideoFrame.Format_IMC3,
                QVideoFrame.Format_IMC4, QVideoFrame.Format_Y8, QVideoFrame.Format_Y16,
                QVideoFrame.Format_Jpeg, QVideoFrame.Format_CameraRaw, QVideoFrame.Format_AdobeDng]

    def isFormatSupported(self, format):
        imageFormat = QVideoFrame.imageFormatFromPixelFormat(format.pixelFormat())
        size = format.frameSize()

        return imageFormat != QImage.Format_Invalid and not size.isEmpty() and \
               format.handleType() == QAbstractVideoBuffer.NoHandle

    def start(self, format: QVideoSurfaceFormat):
        print(1)
        imageFormat = QVideoFrame.imageFormatFromPixelFormat(format.pixelFormat())
        print(2)
        size = format.frameSize()
        print(3)

        if imageFormat != QImage.Format_Invalid and not size.isEmpty():
            print(4)
            self.imageFormat = imageFormat
            print(5)
            self.imageSize = size
            print(6)
            self.sourceRect = format.viewport()
            print(7)

            # super().start(format)

            self.widget.updateGeometry()
            print(8)
            self.updateVideoRect()
            print(9)

            return True
        else:
            print(10)
            return False

    def stop(self):
        self.currentFrame = QVideoFrame()
        self.targetRect = QRect()

        self.widget.update()
        self.frameAvailable = None

        VideoSaveFrame.stop(self)

    def present(self, frame):
        print("present")
        if frame.isValid():
            cloneFrame = QVideoFrame(frame)
            cloneFrame.map(QAbstractVideoBuffer.ReadOnly)
            image = QImage(cloneFrame.bits(), cloneFrame.width(), cloneFrame.height(),
                           QVideoFrame.imageFormatFromPixelFormat(cloneFrame.pixelFormat()))
            self.frameAvailable.emit(image)  # this is very important
            cloneFrame.unmap()

        if self.surfaceFormat().pixelFormat() != frame.pixelFormat() or \
                self.surfaceFormat().frameSize() != frame.size():
            self.setError(QAbstractVideoSurface.IncorrectFormatError)

            return False
        else:
            self.currentFrame = frame
            self.widget.repaint(self.targetRect)
            return True

    def updateVideoRect(self):
        print("updatevideoRect")
        size = self.surfaceFormat().sizeHint()
        print("updatevideoRect 1")
        size.scale(self.widget.size().boundedTo(size), Qt.KeepAspectRatio)
        print("updatevideoRect 2")

        self.targetRect = QRect(QPoint(0, 0), size)
        print("updatevideoRect 3")
        self.targetRect.moveCenter(self.widget.rect().center())
        print("updatevideoRect 4")

    def paint(self, painter):
        print("paint")
        if self.currentFrame.map(QAbstractVideoBuffer.ReadOnly):
            oldTransform = self.painter.transform()

        if self.surfaceFormat().scanLineDirection() == QVideoSurfaceFormat.BottomToTop:
            self.painter.scale(1, -1)
            self.painter.translate(0, -self.widget.height())

        image = QImage(self.currentFrame.bits(), self.currentFrame.width(), self.currentFrame.height(),
                       self.currentFrame.bytesPerLine(), self.imageFormat)

        self.painter.drawImage(self.targetRect, image, self.sourceRect)

        self.painter.setTransform(oldTransform)

        self.currentFrame.unmap()
