#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import os

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPainter, QPen
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QActionGroup, QMessageBox, QInputDialog, QLabel
from PyQt5 import uic

# js06 modules
import resources

from video_widget_2 import Js06VideoWidget2
from target_plot_widget import Js06TargetPlotWidget
from time_series_plot_widget import Js06TimeSeriesPlotWidget
from video_thread import VideoThread
from tflite_thread import TfliteThread
from settings import Js06Settings
from save_db import SaveDB

class Js06MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "designer/js06_form.ui")
        uic.loadUi(ui_path, self)

        app_icon = QIcon(":icon/logo.png")
        self.setWindowIcon(app_icon)
        # self.showFullScreen()
        self.setGeometry(400, 50, 1500, 1000)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)

        # Check the last shutdown status
        shutdown_status = Js06Settings.get('normal_shutdown')
        if not shutdown_status:
            response = QMessageBox.question(
                self,
                'JS-06 Restore to defaults',
                'The JS-06 exited abnormally. '
                'Do you want to restore the factory default?',
            )
            if response == QMessageBox.Yes:
                Js06Settings.restore_defaults()
        Js06Settings.set('normal_shutdown', False)

        # video dock
        self.video_dock = QDockWidget("Video", self)
        self.video_dock.setFeatures(
            QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
        self.video_widget = Js06VideoWidget2(self)
        self.video_dock.setWidget(self.video_widget)
        self.setCentralWidget(self.video_dock)

        # To drawing target box in blank label
        self.blank_lbl = QLabel(self.video_widget)
        self.blank_lbl.mousePressEvent = self.lbl_mousePressEvent
        self.blank_lbl.paintEvent = self.lbl_paintEvent

        VIDEO_SRC1 = "rtsp://admin:sijung5520@d617.asuscomm.com:2554/profile2/media.smp"
        VIDEO_SRC2 = "rtsp://admin:sijung5520@d617.asuscomm.com:1554/profile2/media.smp"
        VIDEO_SRC3 = "rtsp://admin:sijung5520@d617.asuscomm.com:3554/profile2/media.smp"

        self.actionCamera_1.triggered.connect(lambda: self.video_widget.onCameraChange(VIDEO_SRC1))
        self.actionCamera_1.triggered.connect(lambda: Js06Settings.set('camera', 1))
        self.actionCamera_2.triggered.connect(lambda: self.video_widget.onCameraChange(VIDEO_SRC2))
        self.actionCamera_2.triggered.connect(lambda: Js06Settings.set('camera', 2))
        self.actionCamera_3.triggered.connect(lambda: self.video_widget.onCameraChange(VIDEO_SRC3))
        self.actionCamera_3.triggered.connect(lambda: Js06Settings.set('camera', 3))

        self.actionEdit_target.triggered.connect(self.target_mode)
        self.actionOpen_with_RTSP.triggered.connect(self.open_with_rtsp)

        action_group = QActionGroup(self)
        action_group.addAction(self.actionCamera_1)
        action_group.addAction(self.actionCamera_2)
        action_group.addAction(self.actionCamera_3)

        camera_choice = Js06Settings.get('camera')
        if camera_choice == 1:
            # QND-8020R
            self.actionCamera_1.triggered.emit()
            self.actionCamera_1.setChecked(True)
        elif camera_choice == 2:
            # PNM-9030V
            self.actionCamera_2.triggered.emit()
            self.actionCamera_2.setChecked(True)
        elif camera_choice == 3:
            # XNO-8080R
            self.actionCamera_3.triggered.emit()
            self.actionCamera_3.setChecked(True)

        # target plot dock
        self.target_plot_dock = QDockWidget("Target plot", self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.target_plot_dock)
        self.target_plot_dock.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.target_plot_widget = Js06TargetPlotWidget(self)
        self.target_plot_dock.setWidget(self.target_plot_widget)

        # grafana dock 1
        self.web_dock_1 = QDockWidget("Grafana plot 1", self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.target_plot_dock)
        self.web_dock_1.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.web_view_1 = Js06TimeSeriesPlotWidget()
        self.web_dock_1.setWidget(self.web_view_1)

        self.tabifyDockWidget(self.target_plot_dock, self.web_dock_1)

        self.qtimer = QTimer()
        self.qtimer.setInterval(2000)
        self.qtimer.timeout.connect(self.inference)
        self.qtimer.start()
    # end of __init__

    def closeEvent(self, event):
        Js06Settings.set('normal_shutdown', True)
        event.accept()
    # end of closeEvent

    def inference(self):
        self.video_widget.graphicView.fitInView(self.video_widget.video_item)
        self.blank_lbl.setGeometry(self.video_widget.graphicView.geometry())

        self.horizontal_y1 = self.blank_lbl.height() * (1 / 4)
        self.horizontal_y2 = self.blank_lbl.height() * (1 / 2)
        self.horizontal_y3 = self.blank_lbl.height() * (3 / 4)
    # end of inference

    def target_mode(self):
        """Set target image modification mode"""
        if self.actionEdit_target.isChecked():
            print("Edit target select.")
    # end of target_mode

    def lbl_mousePressEvent(self, event):
        if self.actionEdit_target.isChecked():
            print('draw target this position')
    # end of lbl_mousePressEvent

    def lbl_paintEvent(self, event):
        painter = QPainter(self.blank_lbl)
        if self.actionEdit_target.isChecked():
            painter.setPen(QPen(Qt.black, 2, Qt.DotLine))
            x1 = painter.drawLine(self.blank_lbl.width() * (1 / 4), 0, self.blank_lbl.width() * (1 / 4), self.blank_lbl.height())
            x2 = painter.drawLine(self.blank_lbl.width() * (1 / 2), 0, self.blank_lbl.width() * (1 / 2), self.blank_lbl.height())
            x3 = painter.drawLine(self.blank_lbl.width() * (3 / 4), 0, self.blank_lbl.width() * (3 / 4), self.blank_lbl.height())

            y1 = painter.drawLine(0, self.horizontal_y1, self.blank_lbl.width(), self.horizontal_y1)
            y2 = painter.drawLine(0, self.horizontal_y2, self.blank_lbl.width(), self.horizontal_y2)
            y3 = painter.drawLine(0, self.horizontal_y3, self.blank_lbl.width(), self.horizontal_y3)
        else:
            x1 = None
            x2 = None
            x3 = None
            y1 = None
            y2 = None
            y3 = None
        painter.end()
    # end of lbl_paintEvent

    def open_with_rtsp(self):
        text, ok = QInputDialog.getText(self, "Input RTSP", "Only Hanwha Camera")
        if ok:
            print(text)
    # end of open_with_rtsp

# end of Js06MainWindow


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Js06MainWindow()
    window.show()
    sys.exit(app.exec_())

# end of js06.py
