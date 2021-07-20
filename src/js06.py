#!/usr/bin/env python3
#
# Copyright 2020-21 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)


import os
# import time
# import atexit
# import traceback

# import numpy as np
# import pandas as pd

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QActionGroup, QMessageBox, QInputDialog
from PyQt5 import uic


# js06 modules
import resources
from video_widget import Js06VideoWidget, Js06VideoWidget2
from target_plot_widget import Js06TargetPlotWidget, Js06TargetPlotWidget2
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
                'The last exit status of JS-06 was recorded as abnormal. '
                'Do you want to restore to the factory default?',
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

        # self.splitDockWidget(self.target_plot_dock, self.web_dock_1, Qt.Horizontal)
        self.tabifyDockWidget(self.target_plot_dock, self.web_dock_1)

        self.qtimer = QTimer()
        self.qtimer.setInterval(2000)
        self.qtimer.timeout.connect(self.inference)
        self.qtimer.start()

    # end of __init__

    def closeEvent(self, event):
        Js06Settings.set('normal_shutdown', True)
        event.accept()

    def inference(self):
        # self.video_dock.setGeometry(0, 0, self.width(), self.height() / 2)
        # self.target_plot_dock.setGeometry(self.width(), self.height() / 2, self.width() / 2, self.height() / 2)
        # self.web_dock_1.setGeometry(self.width() / 2, self.height() / 2, self.width() / 2, self.height() / 2)
        # print(self.video_dock.size())
        self.video_widget.graphicView.fitInView(self.video_widget.video_item)

    def target_mode(self):
        """Set target image modification mode"""
        # self.save_target()
        if self.target_process:
            print(self.target_process)

    def open_with_rtsp(self):
        text, ok = QInputDialog.getText(self, "Input RTSP", "Only Hanwha Camera")
        if ok:
            print(text)

    # end of closeEvent


# end of Js06MainWindow


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Js06MainWindow()
    window.show()
    sys.exit(app.exec_())
# end of js06.py
