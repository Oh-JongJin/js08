#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import collections
import os
import sys

from PyQt5 import uic
from PyQt5.QtChart import (QChart, QChartView, QDateTimeAxis, QLegend,
                           QLineSeries, QPolarChart, QScatterSeries,
                           QValueAxis)
from PyQt5.QtCore import (QDateTime, QObject, QPointF, Qt, QUrl, pyqtSignal,
                          pyqtSlot)
from PyQt5.QtGui import QCloseEvent, QColor, QPainter, QPen, QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QVideoFrame
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QDialog, QLabel, QMainWindow, QMessageBox,
                             QVBoxLayout, QWidget)

from .controller import Js06MainCtrl
from .model import Js06Settings


class Js06DiscernmentView(QChartView):
    def __init__(self, parent: QWidget, title: str = None):
        super().__init__(parent)

        self.setRenderHint(QPainter.Antialiasing)

        chart = QPolarChart(title=title)
        chart.legend().setAlignment(Qt.AlignRight)
        chart.legend().setMarkerShape(QLegend.MarkerShapeCircle)
        self.setChart(chart)

        self.positives = QScatterSeries(name='Positive')
        self.negatives = QScatterSeries(name='Negative')
        self.positives.setColor(QColor('green'))
        self.negatives.setColor(QColor('red'))
        self.positives.setMarkerSize(10)
        self.negatives.setMarkerSize(10)
        chart.addSeries(self.positives)
        chart.addSeries(self.negatives)

        axis_x = QValueAxis()
        axis_x.setTickCount(9)
        axis_x.setRange(0, 360)
        axis_x.setLabelFormat('%d \xc2\xb0')
        axis_x.setTitleText('Azimuth (deg)')
        axis_x.setTitleVisible(False)
        chart.setAxisX(axis_x, self.positives)
        chart.setAxisX(axis_x, self.negatives)

        axis_y = QValueAxis()
        axis_y.setRange(0, 20)
        axis_y.setLabelFormat('%d')
        axis_y.setTitleText('Distance (km)')
        axis_y.setTitleVisible(False)
        chart.setAxisY(axis_y, self.positives)
        chart.setAxisY(axis_y, self.negatives)

    def keyPressEvent(self, event):
        keymap = {
            Qt.Key_Up: lambda: self.chart().scroll(0, -10),
            Qt.Key_Down: lambda: self.chart().scroll(0, 10),
            Qt.Key_Right: lambda: self.chart().scroll(-10, 0),
            Qt.Key_Left: lambda: self.chart().scroll(10, 0),
            Qt.Key_Greater: lambda: self.chart().zoonIn,
            Qt.Key_Less: lambda: self.chart().zoonOut,
        }
        callback = keymap.get(event.key())
        if callback:
            callback()

    @pyqtSlot(list, list)
    def refresh_stats(self, positives: list, negatives: list):
        pos_point = [QPointF(a, d) for a, d in positives]
        self.positives.replace(pos_point)
        neg_point = [QPointF(a, d) for a, d in negatives]
        self.negatives.replace(neg_point)


class Js06VisibilityView(QChartView):
    def __init__(self, parent: QWidget, maxlen: int, title: str = None):
        super().__init__(parent)

        now = QDateTime.currentSecsSinceEpoch()
        zeros = [(t * 1000, -1) for t in range(now - maxlen * 60, now, 60)]
        self.data = collections.deque(zeros, maxlen=maxlen)

        self.setRenderHint(QPainter.Antialiasing)

        chart = QChart(title=title)
        chart.legend().setVisible(False)
        self.setChart(chart)
        self.series = QLineSeries(name='Prevailing Visibility')
        chart.addSeries(self.series)

        axis_x = QDateTimeAxis()
        axis_x.setFormat('hh:mm')
        axis_x.setTitleText('Time')
        left = QDateTime.fromMSecsSinceEpoch(self.data[0][0])
        right = QDateTime.fromMSecsSinceEpoch(self.data[-1][0])
        axis_x.setRange(left, right)
        chart.setAxisX(axis_x, self.series)

        axis_y = QValueAxis()
        axis_y.setRange(0, 20)
        axis_y.setLabelFormat('%d')
        axis_y.setTitleText('Distance (km)')
        chart.setAxisY(axis_y, self.series)

        data_point = [QPointF(t, v) for t, v in self.data]
        self.series.append(data_point)

    def keyPressEvent(self, event):
        keymap = {
            Qt.Key_Up: lambda: self.chart().scroll(0, -10),
            Qt.Key_Down: lambda: self.chart().scroll(0, 10),
            Qt.Key_Right: lambda: self.chart().scroll(-10, 0),
            Qt.Key_Left: lambda: self.chart().scroll(10, 0),
            Qt.Key_Greater: lambda: self.chart().zoonIn,
            Qt.Key_Less: lambda: self.chart().zoonOut,
        }
        callback = keymap.get(event.key())
        if callback:
            callback()

    @pyqtSlot(int, dict)
    def refresh_stats(self, epoch: int, wedge_vis: dict):
        wedge_vis_list = list(wedge_vis.values())
        prev_vis = self.prevailing_visibility(wedge_vis_list)
        self.data.append((epoch * 1000, prev_vis))

        left = QDateTime.fromMSecsSinceEpoch(self.data[0][0])
        right = QDateTime.fromMSecsSinceEpoch(self.data[-1][0])
        self.chart().axisX().setRange(left, right)

        data_point = [QPointF(t, v) for t, v in self.data]
        self.series.replace(data_point)

    def prevailing_visibility(self, wedge_vis: list) -> float:
        if None in wedge_vis:
            return 0
        sorted_vis = sorted(wedge_vis, reverse=True)
        prevailing = sorted_vis[(len(sorted_vis) - 1) // 2]
        return prevailing


class Js06CameraView(QDialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setModal(True)

        if getattr(sys, 'frozen', False):
            directory = sys._MEIPASS
        else:
            directory = os.path.dirname(__file__)
        ui_path = os.path.join(directory, 'resources', 'camera_view.ui')
        uic.loadUi(ui_path, self)

        self._ctrl = parent._ctrl
        self._model = self._ctrl.get_camera_table_model()
        self.tableView.setModel(self._model)
        self.insertAbove.clicked.connect(self.insert_above)
        self.insertBelow.clicked.connect(self.insert_below)
        self.removeRows.clicked.connect(self.remove_rows)
        self.buttonBox.accepted.connect(self.accepted)

    def insert_above(self) -> None:
        selected = self.tableView.selectedIndexes()
        row = selected[0].row() if selected else 0
        self._model.insertRows(row, 1, None)

    def insert_below(self) -> None:
        selected = self.tableView.selectedIndexes()
        row = selected[-1].row() if selected else self._model.rowCount(None)
        self._model.insertRows(row + 1, 1, None)

    def remove_rows(self) -> None:
        selected = self.tableView.selectedIndexes()
        if selected:
            self._model.removeRows(selected[0].row(), len(selected), None)

    def accepted(self) -> None:
        # Update camera db
        cameras = self._model.get_data()
        # print(f'DEBUG: {cameras}')
        self._ctrl.update_cameras(cameras, update_target=False)

        # Insert a new attr document, with new front_cam and rear_cam.
        front_cam = {}
        rear_cam = {}
        for cam in cameras:
            if cam['placement'] == 'front':
                uri = cam['uri']
                self._ctrl.front_camera_changed.emit(uri)
                front_cam = cam
                front_cam['camera_id'] = front_cam.pop('_id')
            elif cam['placement'] == 'rear':
                uri = cam['uri']
                self._ctrl.rear_camera_changed.emit(uri)
                rear_cam = cam
                rear_cam['camera_id'] = rear_cam.pop('_id')

        attr = self._ctrl.get_attr()
        attr['front_camera'] = front_cam
        attr['rear_camera'] = rear_cam
        del attr['_id']
        self._ctrl.insert_attr(attr)
        self._ctrl.front_camera_changed.emit(self._ctrl.get_front_camera_uri())
        self._ctrl.rear_camera_changed.emit(self._ctrl.get_rear_camera_uri())


class Js06TargetView(QDialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setModal(True)

        if getattr(sys, 'frozen', False):
            directory = sys._MEIPASS
        else:
            directory = os.path.dirname(__file__)
        ui_path = os.path.join(directory, 'resources', 'target_view.ui')
        uic.loadUi(ui_path, self)
        self._ctrl = parent._ctrl
        self._model = self._ctrl.get_front_target()
        self.cam_name = []

        self.target = []
        self.target_x = []
        self.target_y = []
        self.point_x = []
        self.point_y = []
        self.size_x = []
        self.size_y = []
        self.ordinal = []
        self.category = []
        self.distance = []
        self.oxlist = []
        self.result = []

        self.get_target()

        self.image = self._ctrl.front_video_frame.image().mirrored(False, True)
        self.w = self.image.width()
        self.h = self.image.height()
        self.image_label.setPixmap(QPixmap.fromImage(self.image).scaled(self.w, self.h, Qt.KeepAspectRatio))
        self.image_label.setMaximumSize(self.width(), self.height())
        # self.image_label.setMaximumHeight(self.height())

        # self.groupBox.setMaximumHeight(self.height() / 2)

        self.blank_lbl = QLabel(self)

        self.blank_lbl.mousePressEvent = self.blank_mousePressEvent
        self.buttonBox.accepted.connect(self.save_btn)
        self.buttonBox.rejected.connect(self.rejected_btn)
        self.switch_btn.clicked.connect(self.switch_button)
        self.azimuth_check.stateChanged.connect(self.check)

        # for i in range(len(self._ctrl.get_cameras())):
        #     self.cam_name.append(self._ctrl.get_cameras()[i]['model'])
        # self.cameraCombo.addItems(self.cam_name)

        # if self._ctrl.get_camera_models() in self.cam_name:
        #     self.cameraCombo.setCurrentIndex(self.cam_name.index(self._ctrl.get_camera_models()))

        self.numberCombo.currentIndexChanged.connect(self.combo_changed)
        self.combo_changed()
        self.blank_lbl.raise_()

    def check(self) -> None:
        self.update()

    def switch_button(self):
        # image = self._ctrl.get_front_image()
        # image.convertToFormat(QImage.Format_Grayscale8)
        self.update()

    def combo_changed(self) -> None:
        self.blank_lbl.paintEvent = self.blank_paintEvent

        for i in range(len(self.target)):
            if self.numberCombo.currentText() == str(i + 1):
                self.labelEdit.setText(str(self.target[i]))
                self.distanceEdit.setText(str(self.distance[i]))
                self.point_x_Edit.setText(str(self.point_x[i]))
                self.point_y_Edit.setText(str(self.point_y[i]))
                break
            else:
                self.labelEdit.setText("")
                self.distanceEdit.setText("")
                self.point_x_Edit.setText("")
                self.point_y_Edit.setText("")

    @pyqtSlot()
    def save_btn(self) -> None:
        result = []
        # for i in range(len(self._ctrl.get_cameras())):
        #     if self.cameraCombo.currentText() == self._ctrl.get_cameras()[i]['model']:
        #         address = self._ctrl.get_cameras()[i]['uri']
        # self._ctrl.current_camera_changed.emit(address)

        for i in range(self.numberCombo.count()):
            self.numberCombo.setCurrentIndex(i)
            result.append({'label': f'{self.labelEdit.text()}',
                           'distance': f'{float(self.distanceEdit.text())}',
                           'roi': {
                               'point': [int(self.point_x_Edit.text()), int(self.point_y_Edit.text())]
                           }})

        # TODO(Kyungwon): update camera db only, the current camera selection is
        # performed at camera view
        # Save Target through controller
        self._ctrl.set_attr(result)

        self.close()

    def save_cameras(self) -> None:
        cameras = self._model.get_data()
        self._ctrl.update_cameras(cameras)

    def rejected_btn(self) -> None:
        self.close()

    def blank_paintEvent(self, event):
        self.painter = QPainter(self.blank_lbl)

        self.painter.setPen(QPen(Qt.white, 1, Qt.DotLine))
        if self.azimuth_check.isChecked():
            x1 = self.painter.drawLine(self.blank_lbl.width() * (1 / 4), 0,
                                       self.blank_lbl.width() * (1 / 4), self.blank_lbl.height())
            x2 = self.painter.drawLine(self.blank_lbl.width() * (1 / 2), 0,
                                       self.blank_lbl.width() * (1 / 2), self.blank_lbl.height())
            x3 = self.painter.drawLine(self.blank_lbl.width() * (3 / 4), 0,
                                       self.blank_lbl.width() * (3 / 4), self.blank_lbl.height())

        self.painter.setPen(QPen(Qt.red, 2))
        for name, x, y in zip(self.target, self.point_x, self.point_y):
            self.painter.drawRect(int(x - (25 / 4)), int(y - (25 / 4)), 25 / 2, 25 / 2)
            self.painter.drawText(x - 4, y - 10, f"{name}")

        print("numberCombo - ", self.numberCombo.currentText())
        # self.blank_lbl.resize(self.image_label.size())
        self.blank_lbl.setGeometry(self.image_label.geometry())
        print("Paint")

        self.painter.end()

    def blank_mousePressEvent(self, event) -> None:
        self.update()

        x = int(event.pos().x() / self.blank_lbl.width() * self.image.width())
        y = int(event.pos().y() / self.blank_lbl.height() * self.image.height())

        for i in range(len(self.target)):
            self.target[i] = i + 1

        if event.buttons() == Qt.LeftButton:
            maxVal = max(self.target)

            self.numberCombo.addItem(str(maxVal + 1))
            self.numberCombo.setCurrentIndex(maxVal)

            self.point_x.append(int(event.pos().x()))
            self.point_y.append(int(event.pos().y()))

            self.target.append(len(self.point_x))
            self.distance.append(0)

            self.combo_changed()
            self.coordinator()

            print("mousePressEvent - ", len(self.target))
            # self.save_target()
            # self.get_target()

        if event.buttons() == Qt.RightButton:
            deleteIndex = self.numberCombo.currentIndex() + 1
            reply = QMessageBox.question(self, 'Delete Target',
                                         f'Are you sure delete target [{deleteIndex}] ?')
            if reply == QMessageBox.Yes:
                self.numberCombo.removeItem(deleteIndex - 1)
                self.numberCombo.setCurrentIndex(deleteIndex - 2)

                del self.point_x[deleteIndex - 1]
                del self.point_y[deleteIndex - 1]
                del self.target[deleteIndex - 1]
                self.combo_changed()

    def coordinator(self) -> None:
        self.prime_y = [y / self.h for y in self.target_y]
        self.prime_x = [2 * x / self.w - 1 for x in self.target_x]

    def restoration(self) -> None:
        self.target_x = [int((x + 1) * self.w / 2) for x in self.prime_x]
        self.target_y = [int(y * self.h) for y in self.prime_y]

    def save_target(self) -> None:
        # targets = self._model

        print(self.result)
        print()
        print(self.target)
        print(self.point_x)
        print(self.point_y)
        print(self.distance)
        sys.exit()

        if self.target:
            for i in range(len(self.target)):
                self.result[i]['label'] = self.target
                self.result[i]['roi']['point'][0] = self.point_x
                self.result[i]['roi']['point'][1] = self.point_y
                self.result[i]["distance"] = self.distance

    def get_target(self) -> None:
        targets = self._model

        self.numberCombo.clear()
        for i in range(len(targets)):
            self.numberCombo.addItem(str(i + 1))
        self.result = targets

        for i in range(len(targets)):
            self.target.append(self.result[i]['label'])
            self.point_x.append(self.result[i]['roi']['point'][0])
            self.point_y.append(self.result[i]['roi']['point'][1])
            self.distance.append(self.result[i]['distance'])


class Js06AboutView(QDialog):
    def __init__(self) -> None:
        super().__init__()

        if getattr(sys, 'frozen', False):
            directory = sys._MEIPASS
        else:
            directory = os.path.dirname(__file__)
        ui_path = os.path.join(directory, 'resources', 'about_view.ui')
        uic.loadUi(ui_path, self)


class Js06VideoWidget(QWidget):
    """Video stream player using QVideoWidget
    """
    video_frame_prepared = pyqtSignal(QVideoFrame)

    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)
        
        self.viewer = QVideoWidget()
        self.player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.viewer)
        layout = QVBoxLayout(self)
        layout.addWidget(self.viewer)
        # self.viewer.setGeometry(0, 0, 300, 300)
        # self.viewer.setMinimumSize(600, 250)

    @pyqtSlot(str)
    def on_camera_change(self, uri: str) -> None:
        self.uri = uri
        self.player.setMedia(QMediaContent(QUrl(uri)))
        self.player.play()

    @pyqtSlot(QVideoFrame)
    def on_videoFrameProbed(self, frame: QVideoFrame) -> None:
        self.frame_received = True
        self.video_frame_prepared.emit(frame)


class Js06MainView(QMainWindow):
    restore_defaults_requested = pyqtSignal()
    main_view_closed = pyqtSignal()
    select_camera_requested = pyqtSignal()

    def __init__(self, controller: Js06MainCtrl) -> None:
        super().__init__()

        if getattr(sys, 'frozen', False):
            directory = sys._MEIPASS
        else:
            directory = os.path.dirname(__file__)
        ui_path = os.path.join(directory, 'resources', 'main_view.ui')
        uic.loadUi(ui_path, self)
        self._ctrl = controller

        # Connect signals and slots
        self.restore_defaults_requested.connect(self._ctrl.restore_defaults)

        # Check the exit status
        normal_exit = self._ctrl.check_exit_status()
        if not normal_exit:
            self.ask_restore_default()

        self.actionEdit_Camera.triggered.connect(self.edit_camera)
        self.actionEdit_Target.triggered.connect(self.edit_target)
        self.actionAbout.triggered.connect(self.about_view)

        # Front video
        self.front_video_widget = Js06VideoWidget(self)
        self.front_vertical.addWidget(self.front_video_widget, 1)
        self._ctrl.front_camera_changed.connect(self.front_video_widget.on_camera_change)
        self._ctrl.front_camera_changed.emit(self._ctrl.get_front_camera_uri())

        # Rear video
        self.rear_video_widget = Js06VideoWidget(self)
        self.rear_vertical.addWidget(self.rear_video_widget, 1)
        self._ctrl.rear_camera_changed.connect(self.rear_video_widget.on_camera_change)
        self._ctrl.rear_camera_changed.emit(self._ctrl.get_rear_camera_uri())

        # Discernment status
        self.discernment_widget = Js06DiscernmentView(self)
        self.discernment_vertical.addWidget(self.discernment_widget)
        self._ctrl.target_assorted.connect(self.discernment_widget.refresh_stats)

        # Prevailing visibility
        self.visibility_widget = Js06VisibilityView(self, 1440)
        self.visibility_vertical.addWidget(self.visibility_widget)
        self._ctrl.wedge_vis_ready.connect(self.visibility_widget.refresh_stats)

        self.show()

    def edit_target(self) -> None:
        dlg = Js06TargetView(self)
        dlg.resize(self.width(), self.height())
        dlg.exec_()

    def about_view(self) -> None:
        dlg = Js06AboutView()
        dlg.exec_()

    @pyqtSlot()
    def edit_camera(self) -> None:
        dlg = Js06CameraView(self)
        dlg.exec()

    def ask_restore_default(self) -> None:
        # Check the last shutdown status
        response = QMessageBox.question(
            self,
            'Restore to defaults',
            'The JS-06 exited abnormally. '
            'Do you want to restore the factory default?',
        )
        if response == QMessageBox.Yes:
            self.restore_defaults_requested.emit()

    # TODO(kwchun): its better to emit signal and process at the controller
    def closeEvent(self, event: QCloseEvent) -> None:
        self._ctrl.set_normal_shutdown()


if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Js06MainView(Js06MainCtrl)
    sys.exit(app.exec())
