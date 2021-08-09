#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)


import os

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCloseEvent  # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QActionGroup, QMessageBox, QInputDialog  # pylint: disable=no-name-in-module
from PyQt5 import uic

# js06 modules
# from views.target_plot_widget import Js06TargetPlotWidget
# from views.time_series_plot_widget import Js06TimeSeriesPlotWidget
# from video_thread import VideoThread
# from tflite_thread import TfliteThread
# from save_db import SaveDB

from js06.model import Js06Settings

class Js06MainView(QMainWindow):
    camera_changed = pyqtSignal(int)
    restore_defaults_requested = pyqtSignal()
    main_view_closed = pyqtSignal()

    def __init__(self):
        super().__init__()

        ui_path = os.path.join(os.paths.dirname(os.path.realpath(__file__)),
                               "../resources/main_view.ui")
        uic.loadUi(ui_path, self)

        # self.showFullScreen()
        self.setGeometry(400, 50, 1500, 1000)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        
        # # video dock
        # self.video_dock = QDockWidget("Video", self)
        # self.video_dock.setFeatures(
        #     QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
        # self.video_widget = Js06VideoWidget2(self)
        # self.video_dock.setWidget(self.video_widget)
        # self.setCentralWidget(self.video_dock)

        # VIDEO_SRC1 = "rtsp://admin:sijung5520@d617.asuscomm.com:2554/profile2/media.smp"
        # VIDEO_SRC2 = "rtsp://admin:sijung5520@d617.asuscomm.com:1554/profile2/media.smp"
        # VIDEO_SRC3 = "rtsp://admin:sijung5520@d617.asuscomm.com:3554/profile2/media.smp"

        # self.actionCamera_1.triggered.connect(lambda: self.video_widget.onCameraChange(VIDEO_SRC1))
        # self.actionCamera_1.triggered.connect(lambda: self.camera_changed.emit(1))
        # self.actionCamera_2.triggered.connect(lambda: self.video_widget.onCameraChange(VIDEO_SRC2))
        # self.actionCamera_2.triggered.connect(lambda: self.camera_changed.emit(2))
        # self.actionCamera_3.triggered.connect(lambda: self.video_widget.onCameraChange(VIDEO_SRC3))
        # self.actionCamera_3.triggered.connect(lambda: self.camera_changed.emit(3))

        # self.actionEdit_target.triggered.connect(self.target_mode)
        # self.actionOpen_with_RTSP.triggered.connect(self.open_with_rtsp)

        # action_group = QActionGroup(self)
        # action_group.addAction(self.actionCamera_1)
        # action_group.addAction(self.actionCamera_2)
        # action_group.addAction(self.actionCamera_3)

        # camera_choice = Js06Settings.get('camera')
        # if camera_choice == 1:
        #     # QND-8020R
        #     self.actionCamera_1.triggered.emit()
        #     self.actionCamera_1.setChecked(True)
        # elif camera_choice == 2:
        #     # PNM-9030V
        #     self.actionCamera_2.triggered.emit()
        #     self.actionCamera_2.setChecked(True)
        # elif camera_choice == 3:
        #     # XNO-8080R
        #     self.actionCamera_3.triggered.emit()
        #     self.actionCamera_3.setChecked(True)

        # # target plot dock
        # self.target_plot_dock = QDockWidget("Target plot", self)
        # self.addDockWidget(Qt.BottomDockWidgetArea, self.target_plot_dock)
        # self.target_plot_dock.setFeatures(
        #     QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        # self.target_plot_widget = Js06TargetPlotWidget(self)
        # self.target_plot_dock.setWidget(self.target_plot_widget)

        # # grafana dock 1
        # self.web_dock_1 = QDockWidget("Grafana plot 1", self)
        # self.addDockWidget(Qt.BottomDockWidgetArea, self.target_plot_dock)
        # self.web_dock_1.setFeatures(
        #     QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        # self.web_view_1 = Js06TimeSeriesPlotWidget()
        # self.web_dock_1.setWidget(self.web_view_1)

        # self.splitDockWidget(self.target_plot_dock, self.web_dock_1, Qt.Horizontal)
        # self.tabifyDockWidget(self.target_plot_dock, self.web_dock_1)
    # end of __init__

    @pyqtSlot()
    def ask_restore_default(self):
        # Check the last shutdown status
        response = QMessageBox.question(
            self,
            'JS-06 Restore to defaults',
            'The JS-06 exited abnormally. '
            'Do you want to restore the factory default?',
        )
        if response == QMessageBox.Yes:
            self.restore_defaults_requested.emit()
    # end of ask_restore_default

    # TODO(kwchun): its better to emit signal and process at the controller
    def closeEvent(self, event:QCloseEvent):
        Js06Settings.set('normal_shutdown', True)
        event.accept()
    # end of closeEvent

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

# end of Js06MainView

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication  # pylint: disable=no-name-in-module

    app = QApplication(sys.argv)
    window = Js06MainView()
    window.show()
    sys.exit(app.exec_())

# end of view.py
