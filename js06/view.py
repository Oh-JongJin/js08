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

from PyQt5.QtCore import QObject, QSize, QUrl, Qt, pyqtSignal, pyqtSlot, QPersistentModelIndex
from PyQt5.QtGui import QCloseEvent, QPen, QMouseEvent, QPixmap, QImage, QPainter, QResizeEvent, QTransform
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QVideoFrame, QVideoProbe
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import QDialog, QGraphicsRectItem, QGraphicsScene, \
    QGraphicsView, QMainWindow, QDockWidget, QMessageBox, QInputDialog, QVBoxLayout, \
    QWidget, QLabel
from PyQt5 import uic

from js06.controller import Js06MainCtrl
# from views.target_plot_widget_2 import Js06TargetPlotWidget2
# from views.time_series_plot_widget import Js06TimeSeriesPlotWidget

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
        self.buttonBox.accepted.connect(self.accepted)
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
        NewIndex = self.tableView.model().index(index.row(), 7)
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
    def __init__(self, controller: Js06MainCtrl):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "../resources/edit_target.ui")
        uic.loadUi(ui_path, self)
        self._ctrl = controller
        self._model = self._ctrl.get_target()
        self.cam_name = []

        self.target = []
        self.prime_x = []
        self.prime_y = []
        self.target_x = []
        self.target_y = []
        self.label_x = []
        self.label_y = []
        self.distance = []
        self.oxlist = []
        self.result = []

        # Rotate Edit
        transform = QTransform().rotate(-180)
        self.image = self._ctrl.image.mirrored(True, False)
        self.image_label.setPixmap(QPixmap.fromImage(self.image.transformed(transform)))
        self.image_label.setMaximumSize(self.width(), self.height())

        self.w = self.image.width()
        self.h = self.image.height()

        self.blank_lbl = QLabel(self)

        self.blank_lbl.paintEvent = self.blank_paintEvent
        self.blank_lbl.mousePressEvent = self.blank_mousePressEvent
        self.buttonBox.accepted.connect(self.save_targets)
        self.buttonBox.rejected.connect(self.rejected_btn)

        for i in range(len(self._ctrl.get_cameras())):
            self.cam_name.append(self._ctrl.get_cameras()[i]['model'])
        self.cameraCombo.addItems(self.cam_name)

        if Js06MainView.current_camera_model is not None and self._ctrl.get_camera_list() in self.cam_name:
            self.cameraCombo.setCurrentIndex(self.cam_name.index(Js06MainView.current_camera_model))
        elif self._ctrl.get_camera_list() in self.cam_name:
            self.cameraCombo.setCurrentIndex(self.cam_name.index(self._ctrl.get_camera_list()))

        self.numberCombo.currentIndexChanged.connect(self.combo_changed)
        self.cameraCombo.currentTextChanged.connect(self.camera_changed)

        # self.blank_lbl.raise_()
        self.get_target()
        self.combo_changed()
    # end of __init__

    def camera_changed(self):
        for i in range(len(self._ctrl.get_cameras())):
            if self.cameraCombo.currentText() == self._ctrl.get_cameras()[i]['model']:
                add = self._ctrl.get_cameras()[i]['uri']
        self._ctrl.current_camera_changed.emit(add)
        # self.image_label.setText("color: #7FFFD4")
        Js06MainView.current_camera_model = self.cameraCombo.currentText()

    # end of camera_changed

    def combo_changed(self):
        targets = self._model
        ordinalItems = [self.ordinalCombo.itemText(i) for i in range(self.ordinalCombo.count())]
        categoryItems = [self.categoryCombo.itemText(i) for i in range(self.categoryCombo.count())]

        for i in range(len(targets)):
            if self.numberCombo.currentText() == str(i + 1):
                self.labelEdit.setText(str(targets[i]['label']))
                self.distanceEdit.setText(str(targets[i]['distance']))
                self.point_x_Edit.setText(str(targets[i]['roi']['point'][0]))
                self.point_y_Edit.setText(str(targets[i]['roi']['point'][1]))
                self.size_x_Edit.setText(str(targets[i]['roi']['size'][0]))
                self.size_y_Edit.setText(str(targets[i]['roi']['size'][1]))

                if targets[i]['ordinal'] in ordinalItems:
                    self.ordinalCombo.setCurrentIndex(ordinalItems.index(targets[i]['ordinal']))

                if targets[i]['category'] in categoryItems:
                    self.categoryCombo.setCurrentIndex(categoryItems.index(targets[i]['category']))

    # end of combo_changed

    def save_targets(self):
        targets = self._model
        print("Save")
        self.close()
    # end of save_targets

    def save_cameras(self):
        cameras = self._model.get_data()
        self._ctrl.update_cameras(cameras)
    # end of save_cameras

    def rejected_btn(self):
        self.close()
    # end of rejected_btn

    def blank_paintEvent(self, event):
        self.painter = QPainter(self.blank_lbl)
        if self.target:
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
        # for i in range(len(self.target)):
        #     if self.target_x[i] - 25 < x < self.target_x[i] + 25 and \
        #             self.target_y[i] - 25 < y < self.target_y[i] + 25:
        #         if self.oxlist[i] == 0:
        #             self.oxlist[i] = 1
        #         else:
        #             self.oxlist[i] = 0
        if event.buttons() == Qt.LeftButton:
            # self.target = []
            text, ok = QInputDialog.getText(self, 'Add Target', 'Distance (km)')
            if ok and text:
                print(f"test: {text}")
                # self.target_x.append(float(x))
                # self.target_y.append(float(y))
                # self.distance.append(float(text))
                # self.target.append(str(len(self.target_x)))
                # self.oxlist.append(0)
                # print(f"Target position: {self.target_x[-1]}, {self.target_y[-1]}")
                # # self.coordinator()
                # self.save_target()
                # self.get_target()
                #
                # # self.numberCombo.clear()
                # self.numberCombo.update()
                # for i in range(len(self.target)):
                #     self.numberCombo.addItem(str(i + 1))
                #     self.numberCombo.setCurrentIndex(i)
                #     self.labelEdit.setText(f"t{i + 1}")
                # self.distanceEdit.setText(text)
                # self.ordinalEdit.setText("E")
                # self.categoryEdit.setText("single")
                # self.coordinate_x_Edit.setText(str(x))
                # self.coordinate_y_Edit.setText(str(y))

        if event.buttons() == Qt.RightButton:
            # pylint: disable=invalid-name
            text, ok = QInputDialog.getText(self, 'Remove Target', 'Enter target number to remove')
            if ok and text:
                if len(self.target) >= 1:
                    text = int(text)
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
        self.target_x = [int((x + 1) * self.w / 2) for x in self.prime_x]
        self.target_y = [int(y * self.h) for y in self.prime_y]
    # end of restoration

    def save_target(self):
        if self.target:
            for i in range(len(self.target)):
                self.result[i]['label'] = self.target[i]
                self.result[i]['label_x'] = [int(x * self.width() / self.w) for x in self.target_x][i]
                self.result[i]['label_y'] = [int(y * self.height() / self.h) for y in self.target_y][i]
                self.result[i]["distance"] = self.distance
    # end of save_target

    def get_target(self):
        targets = self._model

        self.numberCombo.clear()
        for i in range(len(targets)):
            self.numberCombo.addItem(str(i + 1))
        self.result = targets

        for i in range(len(targets)):
            self.target.append(self.result[i]['label'])
            self.label_x.append(self.result[i]['roi']['point'][0])
            self.label_y.append(self.result[i]['roi']['point'][1])
            self.distance.append(self.result[i]['distance'])
    # end of get_target

# end of Js06EditTarget


class Js06VideoWidget(QWidget):
    """Video stream player using QGraphicsVideoItem
    """
    grabImage = pyqtSignal(QImage)

    def __init__(self, parent: QObject):
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

        self.probe = QVideoProbe(self)
        self.probe.videoFrameProbed.connect(self.on_videoFrameProbed)
        self.probe.setSource(self.player)
    # end of __init__

    ############
    ## Events ##
    ############
    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.graphicView.fitInView(self._video_item, Qt.KeepAspectRatio)
        return super().resizeEvent(a0)
    # end of resizeEvent

    # end of events

    ###########
    ## Slots ##
    ###########
    @pyqtSlot(QVideoFrame)
    def on_videoFrameProbed(self, frame: QVideoFrame):
        self.grabImage.emit(frame.image())
    # end of on_videoFrameProbed

    @pyqtSlot(str)
    def on_camera_change(self, uri):
        print("DEBUG:", uri)
        self.player.setMedia(QMediaContent(QUrl(uri)))
        self.player.play()
    # end of on_camera_change

    # end of slots

    def draw_roi(self, point: tuple, size: tuple):
        """Draw a boundary rectangle of ROI
        Parameters:
          point: the upper left point of ROI in canonical coordinates
          size: the width and height of ROI in canonical coordinates
        """
        rectangle = QGraphicsRectItem(*point, *size, self._video_item)
        rectangle.setPen(QPen(Qt.blue))
    # end of draw_roi
    
    @property
    def video_item(self):
        return self._video_item
    # end of video_item

# end of VideoWidget


class Js06MainView(QMainWindow):
    restore_defaults_requested = pyqtSignal()
    main_view_closed = pyqtSignal()
    select_camera_requested = pyqtSignal()
    current_camera_model = None

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

        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)

        self.actionEdit_Target.triggered.connect(self.edit_target)

        self.video_dock = QDockWidget("Video", self)
        self.video_dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
        self.video_widget = Js06VideoWidget(self)
        self.video_dock.setWidget(self.video_widget)
        self.setCentralWidget(self.video_dock)
        self.video_widget.grabImage.connect(self._ctrl.update_image)
        self._ctrl.current_camera_changed.connect(self.video_widget.on_camera_change)
        self._ctrl.current_camera_changed.emit(self._ctrl.get_current_camera_uri())
        self.video_dock.setMinimumSize(self.width(), self.height() / 2)

        # The parameters in the following codes is for the test purposes.
        # They should be changed to use canonical coordinates.
        # self.video_widget.draw_roi((50, 50), (40, 40))

        # # target plot dock
        # self.target_plot_dock = QDockWidget("Target plot", self)
        # self.addDockWidget(Qt.BottomDockWidgetArea, self.target_plot_dock)
        # self.target_plot_dock.setFeatures(
        #     QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        # self.target_plot_widget = Js06TargetPlotWidget2(self)
        # self.target_plot_dock.setWidget(self.target_plot_widget)
        #
        # # grafana dock 1
        # self.web_dock_1 = QDockWidget("Grafana plot 1", self)
        # self.addDockWidget(Qt.BottomDockWidgetArea, self.web_dock_1)
        # self.web_dock_1.setFeatures(
        #     QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        # self.web_view_1 = Js06TimeSeriesPlotWidget()
        # self.web_dock_1.setWidget(self.web_view_1)

        # self.splitDockWidget(self.target_plot_dock, self.web_dock_1, Qt.Horizontal)
        # self.tabifyDockWidget(self.target_plot_dock, self.web_dock_1)
    # end of __init__

    def edit_target(self):
        self.video_widget.player.stop()
        dlg = Js06EditTarget(self._ctrl)
        dlg.exec_()
        self.video_widget.player.play()
    # end of edit_target

    @pyqtSlot()
    def select_camera(self):
        dlg = Js06CameraView(self._ctrl)
        dlg.exec_()
    # end of select_camera

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
