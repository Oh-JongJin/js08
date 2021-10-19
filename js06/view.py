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
from PyQt5.QtCore import (QDateTime, QObject, QPointF, Qt, QTimer, QUrl,
                          pyqtSignal, pyqtSlot)
from PyQt5.QtGui import (QCloseEvent, QColor, QPainter, QPaintEvent, QPen,
                         QPixmap, QResizeEvent)
from PyQt5.QtMultimedia import (QMediaContent, QMediaPlayer, QVideoFrame,
                                QVideoProbe)
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import (QDialog, QGraphicsRectItem, QGraphicsScene,
                             QGraphicsView, QLabel, QMainWindow, QMessageBox,
                             QVBoxLayout, QWidget)

from .model import Js06Settings

from .controller import Js06MainCtrl


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
        axis_x.setRange(0, 360)
        axis_x.setLabelFormat('%d')
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
        print('DEBUG(Js06DiscernmentView.refresh_stats)')
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
            elif cam['placement'] == 'rear':
                uri = cam['uri']
                self._ctrl.rear_camera_changed.emit(uri)
                rear_cam = cam

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
        self._model = self._ctrl.get_target()
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
        self.image_label.setPixmap(QPixmap.fromImage(self.image))
        self.image_label.setMaximumSize(self.width(), self.height())

        self.w = self.image.width()
        self.h = self.image.height()

        self.blank_lbl = QLabel(self)

        self.blank_lbl.mousePressEvent = self.blank_mousePressEvent
        self.buttonBox.accepted.connect(self.save_btn)
        self.buttonBox.rejected.connect(self.rejected_btn)
        self.switch_btn.clicked.connect(self.switch_button)

        # for i in range(len(self._ctrl.get_cameras())):
        #     self.cam_name.append(self._ctrl.get_cameras()[i]['model'])
        # self.cameraCombo.addItems(self.cam_name)

        # if self._ctrl.get_camera_models() in self.cam_name:
        #     self.cameraCombo.setCurrentIndex(self.cam_name.index(self._ctrl.get_camera_models()))

        self.numberCombo.currentIndexChanged.connect(self.combo_changed)
        self.combo_changed()
        self.blank_lbl.raise_()

    def switch_button(self):
        # image = self._ctrl.get_front_image()
        # image.convertToFormat(QImage.Format_Grayscale8)
        print(self.image.size())
        print(self.image_label.size())
        print(self.blank_lbl.size())

    def combo_changed(self) -> None:
        self.blank_lbl.paintEvent = self.blank_paintEvent
        ordinalItems = [self.ordinalCombo.itemText(i) for i in range(self.ordinalCombo.count())]
        categoryItems = [self.categoryCombo.itemText(i) for i in range(self.categoryCombo.count())]

        for i in range(len(self.target)):
            if self.numberCombo.currentText() == str(i + 1):
                self.labelEdit.setText(str(self.target[i]))
                self.distanceEdit.setText(str(self.distance[i]))
                self.point_x_Edit.setText(str(self.point_x[i]))
                self.point_y_Edit.setText(str(self.point_y[i]))
                self.size_x_Edit.setText(str(self.size_x[i]))
                self.size_y_Edit.setText(str(self.size_y[i]))

                if self.ordinal[i] in ordinalItems:
                    self.ordinalCombo.setCurrentIndex(ordinalItems.index(self.ordinal[i]))
                if self.category[i] in categoryItems:
                    self.categoryCombo.setCurrentIndex(categoryItems.index(self.category[i]))
                break
            else:
                self.labelEdit.setText('')
                self.distanceEdit.setText('')
                self.point_x_Edit.setText('')
                self.point_y_Edit.setText('')
                self.size_x_Edit.setText('')
                self.size_y_Edit.setText('')
                self.ordinalCombo.setCurrentIndex(-1)
                self.categoryCombo.setCurrentIndex(-1)

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
                           'ordinal': f'{self.ordinalCombo.currentText()}',
                           'category': f'{self.categoryCombo.currentText()}',
                           'roi': {
                               'point': [int(self.point_x_Edit.text()), int(self.point_y_Edit.text())],
                               'size': [int(self.size_x_Edit.text()), int(self.size_y_Edit.text())]
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

    def blank_paintEvent(self, event: QPaintEvent) -> None:
        self.painter = QPainter(self.blank_lbl)

        self.painter.setPen(QPen(Qt.black, 1, Qt.DotLine))
        x1 = self.painter.drawLine(self.blank_lbl.width() * (1 / 4), 0,
                                   self.blank_lbl.width() * (1 / 4), self.blank_lbl.height())
        x2 = self.painter.drawLine(self.blank_lbl.width() * (1 / 2), 0,
                                   self.blank_lbl.width() * (1 / 2), self.blank_lbl.height())
        x3 = self.painter.drawLine(self.blank_lbl.width() * (3 / 4), 0,
                                   self.blank_lbl.width() * (3 / 4), self.blank_lbl.height())

        self.painter.setPen(QPen(Qt.black, 2))
        for name, x, y in zip(self.target, self.point_x, self.point_y):
            self.painter.drawRect(int(x - (25 / 4)), int(y - (25 / 4)), 25 / 2, 25 / 2)
            self.painter.drawText(x - 4, y - 10, f"{name}")
        self.blank_lbl.resize(self.image_label.size())

        self.painter.end()

    def blank_mousePressEvent(self, event) -> None:
        self.update()

        x = int(event.pos().x() / self.width() * self.w)
        y = int(event.pos().y() / self.height() * self.h)

        for i in range(len(self.target)):
            self.target[i] = i + 1

        if event.buttons() == Qt.LeftButton:
            maxVal = max(self.target)

            self.numberCombo.addItem(str(maxVal + 1))
            self.numberCombo.setCurrentIndex(maxVal)

            self.point_x.append(int(x))
            self.point_y.append(int(y))
            self.size_x.append(0.3)
            self.size_y.append(0.3)
            self.target.append(len(self.point_x))
            self.distance.append(0)
            self.ordinal.append('E')
            self.category.append('Single')

            self.combo_changed()

            print("mousePressEvent - ", len(self.target))
            self.save_target()
            self.get_target()

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

        if self.target:
            for i in range(len(self.target)):
                pass
                # self.result[i]['label'] = self.target
                # # self.result[i]['label_x'] = [int(x * self.width() / self.w) for x in self.target_x][i]
                # # self.result[i]['label_y'] = [int(y * self.height() / self.h) for y in self.target_y][i]
                # self.result[i]['roi']['point'][0] = self.label_x
                # self.result[i]['roi']['point'][1] = self.label_y
                # self.result[i]['distance'] = self.distance
                # # print(self.target[i])
                # # print(self.label_x[i])
                # # print(self.label_y[i])
                # # print(self.distance[i])

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
            self.size_x.append(self.result[i]['roi']['size'][0])
            self.size_y.append(self.result[i]['roi']['size'][1])
            self.distance.append(self.result[i]['distance'])
            self.ordinal.append(self.result[i]['ordinal'])
            self.category.append(self.result[i]['category'])


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
    """Video stream player using QGraphicsVideoItem
    """
    video_frame_prepared = pyqtSignal(QVideoFrame)

    def __init__(self, parent: QObject) -> None:
        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.graphicView = QGraphicsView(self.scene)
        self.graphicView.setStyleSheet('background: #000000')
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

        self.uri = None
        self.frame_received = False
        self.recover_timer = QTimer(self)
        recover_interval = Js06Settings.get('media_recover_interval')
        self.recover_timer.setInterval(recover_interval * 1000)
        self.recover_timer.timeout.connect(self.recover_media)
        self.recover_timer.start()

    def recover_media(self):
        """Try to reconnect if we can not receive video stream
        """
        if self.uri is None:
            return
        
        if self.frame_received:
            return
        
        print(f'DEBUG: Try to recover video stream from {self.uri}')
        self.on_camera_change(self.uri)
        self.frame_recevied = False

    def fit_in_view(self) -> None:
        self.graphicView.fitInView(self._video_item, Qt.KeepAspectRatio)

    def resizeEvent(self, a0: QResizeEvent):
        self.fit_in_view()
        return super().resizeEvent(a0)

    @pyqtSlot(QVideoFrame)
    def on_videoFrameProbed(self, frame: QVideoFrame) -> None:
        self.frame_received = True
        self.video_frame_prepared.emit(frame)

    @pyqtSlot(str)
    def on_camera_change(self, uri: str) -> None:
        self.uri = uri
        self.player.setMedia(QMediaContent(QUrl(uri)))
        self.player.play()

        # Wait till the video stream arrives before fitting the video
        for i in range(500, 5000, 500):
            QTimer.singleShot(i, self.fit_in_view)

    def draw_roi(self, point: tuple, size: tuple) -> None:
        """Draw a boundary rectangle of ROI
        Parameters:
          point: the upper left point of ROI in canonical coordinates
          size: the width and height of ROI in canonical coordinates
        """
        rectangle = QGraphicsRectItem(*point, *size, self._video_item)
        rectangle.setPen(QPen(Qt.blue))


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

        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)

        self.actionEdit_Camera.triggered.connect(self.edit_camera)
        self.actionEdit_Target.triggered.connect(self.edit_target)
        self.actionAbout.triggered.connect(self.about_view)

        # Front video
        # self.front_video_dock.setTitleBarWidget(QWidget(self))
        self.front_video_widget = Js06VideoWidget(self)
        # self.front_video_widget.moveToThread(self._ctrl.video_thread)
        self.front_video_dock.setWidget(self.front_video_widget)
        self.front_video_widget.video_frame_prepared.connect(self._ctrl.update_front_video_frame)
        self._ctrl.front_camera_changed.connect(self.front_video_widget.on_camera_change)
        self._ctrl.front_camera_changed.emit(self._ctrl.get_front_camera_uri())
        # self._ctrl.video_thread.start()

        # Rear video
        # self.rear_video_dock.setTitleBarWidget(QWidget(self))
        self.rear_video_widget = Js06VideoWidget(self)
        # self.rear_video_widget.moveToThread(self._ctrl.video_thread)
        self.rear_video_dock.setWidget(self.rear_video_widget)
        self.rear_video_widget.video_frame_prepared.connect(self._ctrl.update_rear_video_frame)
        self._ctrl.rear_camera_changed.connect(self.rear_video_widget.on_camera_change)
        self._ctrl.rear_camera_changed.emit(self._ctrl.get_rear_camera_uri())
        # self._ctrl.video_thread.start()

        # Discernment status
        self.discernment_widget = Js06DiscernmentView(self)
        # self.discernment_widget.moveToThread(self._ctrl.plot_thread)
        self.discernment_dock.setWidget(self.discernment_widget)
        self._ctrl.target_assorted.connect(self.discernment_widget.refresh_stats)

        # Prevailing visibility
        self.visibility_widget = Js06VisibilityView(self, 1440)
        # self.visibility_widget.moveToThread(self._ctrl.plot_thread)
        self.visibility_dock.setWidget(self.visibility_widget)
        self._ctrl.wedge_vis_ready.connect(self.visibility_widget.refresh_stats)
        # self._ctrl.plot_thread.start()

        self.show()

    def edit_target(self) -> None:
        dlg = Js06TargetView(self)
        dlg.resize(self.width(), self.height())
        dlg.exec()

        # self.setWindowOpacity(0.1)

    def about_view(self) -> None:
        dlg = Js06AboutView()
        dlg.exec()

    @pyqtSlot()
    def edit_camera(self) -> None:
        dlg = Js06CameraView(self)
        dlg.exec()

    def ask_restore_default(self) -> None:
        # Check the last shutdown status
        response = QMessageBox.question(
            self,
            'JS-06 Restore to defaults',
            'The JS-06 exited abnormally.'
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
