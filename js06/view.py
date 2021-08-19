#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

# # Set up backends of matplotlib
# from matplotlib.backends.qt_compat import QtCore
# if QtCore.qVersion() >= "5.":
#     from matplotlib.backends.backend_qt5agg import (
#         FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
# else:
#     from matplotlib.backends.backend_qt4agg import (
#         FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

import os
# import numpy as np
# import pandas as pd

from PyQt5.QtCore import QTimer, QUrl, Qt, pyqtSignal, pyqtSlot, \
    QPersistentModelIndex  # pylint: disable=no-name-in-module
from PyQt5.QtGui import QCloseEvent, QPen, QMouseEvent, QMoveEvent, QPixmap, QImage, QPainter
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem  # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QApplication, QDialog, QGraphicsRectItem, QGraphicsScene, \
    QGraphicsView, QMainWindow, QDockWidget, QMessageBox, QInputDialog, QVBoxLayout, \
    QWidget, QLabel, QSizePolicy  # pylint: disable=no-name-in-module
from PyQt5 import uic

# import cv2

from js06.controller import Js06MainCtrl


class Js06CameraView(QDialog):
    def __init__(self, controller: Js06MainCtrl):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "../resources/camera_view.ui")
        uic.loadUi(ui_path, self)

        self._ctrl = controller
        self._model = self._ctrl.get_camera_table_model()
        self.tableView.setModel(self._model)
        self.insertAbove.clicked.connect(self.insert_above)
        self.insertBelow.clicked.connect(self.insert_below)
        self.removeRows.clicked.connect(self.remove_rows)
        self.buttonBox.accepted.connect(self.save_cameras)

    # model = self._ctrl.get_camera_table_model()
    # self.tableView.setModel(model)
    # self.buttonBox.accepted.connect(self.accepted)
    # end of __init__

    def insert_above(self):
        selected = self.tableView.selectedIndexes()
        row = selected[0].row() if selected else 0
        self._model.insertRows(row, 1, None)
        # end of insert_above

    def insert_below(self):
        selected = self.tableView.selectedIndexes()
        row = selected[-1].row() if selected else self._model.rowCount(None)
        self._model.insertRows(row + 1, 1, None)
        # end of insert_below

    def remove_rows(self):
        selected = self.tableView.selectedIndexes()
        if selected:
            self._model.removeRows(selected[0].row(), len(selected), None)
        # end of remove_rows

    def save_cameras(self):
        cameras = self._model.get_data()
        self._ctrl.update_cameras(cameras)
        # end of save_cameras

    def accepted(self):
        index = self.tableView.currentIndex()
        NewIndex = self.tableView.model().index(index.row(), 6)
        add = NewIndex.data()
        print(f"Select uri: [{add}]")
        index_list = []
        for model_index in self.tableView.selectionModel().selectedRows():
            index = QPersistentModelIndex(model_index)
            index_list.append(index)

        self._ctrl.current_camera_changed.emit(add)
    # end of accepted


# end of Js06CameraView

class Js06EditTarget(QDialog):
    def __init__(self, uri: str):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "../resources/edit_target.ui")
        uic.loadUi(ui_path, self)

        self.w = None
        self.h = None

        self.target = []
        self.prime_x = []
        self.prime_y = []
        self.target_x = []
        self.target_y = []
        self.label_x = []
        self.label_y = []
        self.distance = []
        self.oxlist = []
        self.target_process = False
        self.csv_path = None

        cap = cv2.VideoCapture(uri)
        ret, self.frame = cap.read()
        img = self.convert_cv(self.frame)
        self.image_label.setPixmap(img)

        self.blank_lbl = QLabel(self)

        self.blank_lbl.paintEvent = self.blank_paintEvent
        self.blank_lbl.mousePressEvent = self.blank_mousePressEvent
        self.blank_lbl.raise_()

    # end of __init__

    def convert_cv(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        self.h, self.w, c = rgb_image.shape
        convert_to_Qt_format = QImage(rgb_image.data, self.w, self.h, self.w * c, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.width(), self.height(),
                                        Qt.KeepAspectRatio, Qt.SmoothTransformation)

        return QPixmap.fromImage(p)

    # end of convert_cv

    def blank_paintEvent(self, event):
        self.painter = QPainter(self.blank_lbl)
        if self.target_x:
            for name, x, y in zip(self.target, self.label_x, self.label_y):
                self.painter.drawRect(x - (25 / 4), y - (25 / 4), 25 / 2, 25 / 2)
                self.painter.drawText(x - 4, y - 10, f"{name}")
        self.blank_lbl.setGeometry(self.image_label.geometry())

        self.painter.end()

    # end of paintEvent

    def blank_mousePressEvent(self, event):
        x = int(event.pos().x() / self.width() * self.w)
        y = int(event.pos().y() / self.height() * self.h)

        for i in range(len(self.target)):
            self.target[i] = i + 1
        for i in range(len(self.target)):
            if self.target_x[i] - 25 < x < self.target_x[i] + 25 and \
                    self.target_y[i] - 25 < y < self.target_y[i] + 25:
                if self.oxlist[i] == 0:
                    self.oxlist[i] = 1
                else:
                    self.oxlist[i] = 0
        # if not self.target_process:
        #     return
        if event.buttons() == Qt.LeftButton:
            text, ok = QInputDialog.getText(self, 'Add Target', 'Distance (km)')
            if ok and text:
                self.target_x.append(float(x))
                self.target_y.append(float(y))
                self.distance.append(float(text))
                self.target.append(str(len(self.target_x)))
                self.oxlist.append(0)
                print(f"Target position: {self.target_x[-1]}, {self.target_y[-1]}")
                self.coordinator()
                self.save_target()
                self.get_target()

        if event.buttons() == Qt.RightButton:
            # pylint: disable=invalid-name
            text, ok = QInputDialog.getText(self, 'Remove Target', 'Enter target number to remove')
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
                    print(f"[Target {text}] remove.")

    # end of label_mousePressEvent

    def coordinator(self):
        self.prime_y = [y / self.h for y in self.target_y]
        self.prime_x = [2 * x / self.w - 1 for x in self.target_x]

    # end of coordinator

    def restoration(self):
        self.target_x = [self.f2i((x + 1) * self.w / 2) for x in self.prime_x]
        self.target_y = [self.f2i(y * self.h) for y in self.prime_y]

    # end of restoration

    @staticmethod
    def f2i(num: float):
        return int(num + 0.5)

    # end of f2i

    def save_target(self):
        if self.prime_x:
            col = ["target", "x", "y", "label_x", "label_y", "distance", "discernment"]
            self.result = pd.DataFrame(columns=col)
            self.result["target"] = self.target
            self.result["x"] = self.prime_x
            self.result["y"] = self.prime_y
            self.result["label_x"] = [round(x * self.width() / self.w, 3) for x in self.target_x]
            self.result["label_y"] = [round(y * self.height() / self.h, 3) for y in self.target_y]
            self.result["distance"] = self.distance
            self.result["discernment"] = self.oxlist
            self.csv_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         f"../resources/test.csv")
            self.result.to_csv(self.csv_path, mode="w", index=False)

    # end of save_target

    def get_target(self):
        if os.path.isfile(self.csv_path):
            result = pd.read_csv(self.csv_path)
            self.target = result.target.tolist()
            self.prime_x = result.x.tolist()
            self.prime_y = result.y.tolist()
            self.label_x = result.label_x.tolist()
            self.label_y = result.label_y.tolist()
            self.distance = result.distance.tolist()
            self.oxlist = [0 for i in range(len(self.prime_x))]
        else:
            print("csv 파일을 불러올 수 없습니다.")

    # end of get_target


# end of Js06EditTarget

class Js06VideoWidget(QWidget):
    """Video stream player using QGraphicsVideoItem
    """

    def __init__(self, parent=None):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.graphicView = QGraphicsView(self.scene)
        self.graphicView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._video_item = QGraphicsVideoItem()
        self.scene.addItem(self._video_item)

        self.player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self._video_item)
        self.player.setPosition(0)

        layout = QVBoxLayout(self)
        layout.addWidget(self.graphicView)
        self.uri = None
        self.cam_name = None

    # end of __init__

    def mousePressEvent(self, event: QMouseEvent):
        self.graphicView.fitInView(self._video_item)

    # end of mousePressEvent

    def draw_roi(self, point: tuple, size: tuple):
        """Draw a boundary rectangle of ROI
        Parameters:
          point: the upper left point of ROI in canonical coordinates
          size: the width and height of ROI in canonical coordinates
        """
        rectangle = QGraphicsRectItem(*point, *size, self._video_item)
        rectangle.setPen(QPen(Qt.blue))

    # end of draw_roi

    @pyqtSlot(QMediaPlayer.State)
    def on_stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.view.fitInView(self._video_item, Qt.KeepAspectRatio)

    # end of on_stateChanged

    @pyqtSlot(str)
    def on_camera_change(self, uri):
        print("DEBUG:", uri)
        self.uri = uri
        self.player.setMedia(QMediaContent(QUrl(uri)))
        self.player.play()

        # self.graphicView.fitInView(self._video_item)

        # self.blank_lbl.paintEvent = self.paintEvent
        # self.blank_lbl.raise_()

        # if url == VIDEO_SRC3:
        #     self.camera_name = "XNO-8080R"
        # print(self.camera_name)
        # self.get_target()

        # self.video_thread = VideoThread(url)
        # self.video_thread.update_pixmap_signal.connect(self.convert_cv_qt)
        # self.video_thread.start()

    # def convert_cv_qt(self, cv_img):
    #     rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    #     self.epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    #     self.restoration()

    #     if self.epoch[-2:] == "00":
    #         self.save_frame(cv_img, self.epoch)
    # # end of conver_cv_qt

    # def get_target(self):
    #     if os.path.isfile(f"target/{self.camera_name}.csv"):
    #         result = pd.read_csv(f"target/{self.camera_name}.csv")
    #         self.target = result.target.tolist()
    #         self.prime_x = result.x.tolist()
    #         self.prime_y = result.y.tolist()
    #         self.label_x = result.label_x.tolist()
    #         self.label_y = result.label_y.tolist()
    #         self.distance = result.distance.tolist()
    #         self.oxlist = [0 for i in range(len(self.prime_x))]
    #         print("영상목표를 불러옵니다.")
    #     else:
    #         print("csv 파일을 불러올 수 없습니다.")
    # # end of get_target

    # def save_target(self):
    #     if self.prime_x:
    #         col = ["target", "x", "y", "label_x", "label_y", "distance", "discernment"]
    #         self.result = pd.DataFrame(columns=col)
    #         self.result["target"] = self.target
    #         self.result["x"] = self.prime_x
    #         self.result["y"] = self.prime_y
    #         self.result["label_x"] = [round(x * self.graphicView.geometry().width() /
    #                                         self.video_item.nativeSize().width(), 3) for x in self.target_x]
    #         self.result["label_y"] = [round(y * self.graphicView.geometry().height() /
    #                                         self.video_item.nativeSize().height(), 3) for y in self.target_y]
    #         self.result["distance"] = self.distance
    #         self.result["discernment"] = self.oxlist
    #         self.result.to_csv(f"{self.filepath}/{self.camera_name}.csv", mode="w", index=False)
    # # end of save_target

    # def save_frame(self, image: np.ndarray, epoch: str):
    #     image_path = os.path.join(self.filepath, "image", f"{self.camera_name}", f"{epoch[2:6]}")
    #     file_name = f"{epoch}"
    #     if not os.path.isdir(image_path):
    #         os.makedirs(image_path)
    #     if not os.path.isfile(f"{image_path}/{file_name}.jpg"):
    #         cv2.imwrite(f"{image_path}/{file_name}.jpg", image)
    #     del image
    #     del image_path
    #     cv2.destroyAllWindows()
    # # end of save_frame

    # def save_target_frame(self, epoch: str):
    #     for i in range(len(self.target_x)):
    #         image_path = os.path.join(self.filepath, "image", "100x100", f"target{i + 1}")
    #         if not os.path.isdir(image_path):
    #             os.makedirs(image_path)
    #         if not os.path.isfile(f"{image_path}/target_{i + 1}_{epoch}.jpg"):
    #             b, g, r = cv2.split(self.crop_imagelist100[i])
    #             if self.oxlist[i] == 1:
    #                 cv2.imwrite(f"{image_path}/target_{i + 1}_{epoch}_Y.jpg", cv2.merge([r, g, b]))
    #             else:
    #                 cv2.imwrite(f"{image_path}/target_{i + 1}_{epoch}_N.jpg", cv2.merge([r, g, b]))
    #     del self.crop_imagelist100
    #     cv2.destroyAllWindows()
    # # end of save_target_frame

    # def crop_image(self, image: np.ndarray):
    #     new_crop_image = []
    #     for i in range(len(self.target_x)):
    #         crop_img = image[int(self.target_y[i] - 50): int(self.target_y[i] + 50),
    #                         int(self.target_x[i] - 50): int(self.target_x[i] + 50)]
    #         new_crop_image.append(crop_img)
    #     self.crop_imagelist100 = new_crop_image
    #     del image
    # # end of crop_image

    def inference_clicked(self):
        # self.graphicView.fitInView(self._video_item)
        # self.blank_lbl.resize(self.graphicView.geometry().width(),
        #                       self.graphicView.geometry().height())
        pass

    # # end of inference_clicked

    # def coordinator(self):
    #     self.prime_x = [2 * x / self.video_item.nativeSize().width() - 1 for x in self.target_x]
    #     self.prime_y = [y / self.video_item.nativeSize().height() for y in self.target_y]
    # # end of coordinator

    # def restoration(self):
    #     try:
    #         if self.target:
    #             self.target_x = [self.f2i((x + 1) * self.video_item.nativeSize().width() / 2) for x in self.prime_x]
    #             self.target_y = [self.f2i(y * self.video_item.nativeSize().height()) for y in self.prime_y]
    #     except:
    #         print(traceback.format_exc())
    #         sys.exit()

    # end of restoration

    # @staticmethod
    # def f2i(num: float):
    #     """Convert float to the nearest int"""
    #     return int(num + 0.5)
    # # end of f2i
    @property
    def video_item(self):
        return self._video_item


# end of VideoWidget

class Js06MainView(QMainWindow):
    restore_defaults_requested = pyqtSignal()
    main_view_closed = pyqtSignal()
    select_camera_requested = pyqtSignal()

    def __init__(self, controller: Js06MainCtrl):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "../resources/main_view.ui")
        uic.loadUi(ui_path, self)
        self._ctrl = controller

        # Connect signals and slots
        self.restore_defaults_requested.connect(self._ctrl.restore_defaults)
        self.actionSelect_Camera.triggered.connect(self.select_camera)

        # Check the exit status
        normal_exit = self._ctrl.check_exit_status()
        if not normal_exit:
            self.ask_restore_default()

        # self.showFullScreen()
        # self.setGeometry(400, 50, 1500, 1000)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)

        self.actionEdit_Target.triggered.connect(self.edit_target)
        # self.actionSelect_Camera.triggered.connect(self.select_camera_triggered)

        self.video_dock = QDockWidget("Video", self)
        self.video_dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
        self.video_widget = Js06VideoWidget(self)
        self.video_dock.setWidget(self.video_widget)
        self.setCentralWidget(self.video_dock)

        self._ctrl.current_camera_changed.connect(self.video_widget.on_camera_change)
        self._ctrl.current_camera_changed.emit(self._ctrl.get_current_camera_uri())

        # The parameters in the following codes is for the test purposes. 
        # They should be changed to use canonical coordinates.
        self.video_widget.draw_roi((50, 50), (40, 40))

    # end of __init__

    # self.qtimer = QTimer()
    # self.qtimer.setInterval(2000)
    # self.qtimer.timeout.connect(self.video_widget.inference_clicked)
    # self.qtimer.start()

    # # target plot dock
    # self.target_plot_dock = QDockWidget("Target plot", self)
    # self.addDockWidget(Qt.BottomDockWidgetArea, self.target_plot_dock)
    # self.target_plot_dock.setFeatures(
    #     QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
    # self.target_plot_widget = Js06TargetPlotWidget2(self)
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

    # def select_camera(self):
    #     text, ok = QInputDialog.getItem(self, "Select Camera",
    #                                     "Select Camera Manufacturer", ["H", "C", "F"], 0, False)
    #     text1, ok1 = QInputDialog.getText(self, "Select Camera", "Input Camera URI")
    #     print(text1)
    #     if ok and ok1:
    #         if text == "H" and text1 is not None:
    #             SRC = f"rtsp://admin:sijung5520@{text1}/profile2/media.smp"
    #             self.video_widget.onCameraChange(SRC)
    # # end of select_cam

    def moveEvent(self, event: QMoveEvent):
        # print(self.geometry())
        pass

    def edit_target(self):
        self.video_widget.player.stop()

        uri = self._ctrl.get_current_camera_uri()

        dlg = Js06EditTarget(uri)
        dlg.exec_()
        self.video_widget.player.play()

    # end of edit_target

    @pyqtSlot()
    def select_camera(self):
        dlg = Js06CameraView(self._ctrl)
        dlg.exec_()

    # end of select_cameara

    def ask_restore_default(self):
        # Check the last shutdown status
        response = QMessageBox.question(
            self,
            'JS-06 Restore to defaults',
            'The JS-06 exited abnormally.'
            'Do you want to restore the factory default?',
        )
        if response == QMessageBox.Yes:
            self.restore_defaults_requested.emit()

    # end of ask_restore_default

    # TODO(kwchun): its better to emit signal and process at the controller
    def closeEvent(self, event: QCloseEvent):
        self._ctrl.set_normal_shutdown()
        # event.accept()

    # end of closeEvent

    # def inference(self):
    #     self.video_widget.graphicView.fitInView(self.video_widget.video_item)

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

# if __name__ == '__main__':
#     import sys
#     from PyQt5.QtWidgets import QApplication  # pylint: disable=no-name-in-module

#     app = QApplication(sys.argv)
#     window = Js06MainView()
#     window.show()
#     sys.exit(app.exec_())

# end of view.py
