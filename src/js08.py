#!/usr/bin/env python3
#
# Copyright 2021-2022 Sijung Co., Ltd.
#
# Authors:
#     cotjdals5450@gmail.com (Seong Min Chae)
#     5jx2oh@gmail.com (Jongjin Oh)

import os
import sys
import vlc
import time

import numpy as np
import pandas as pd
import multiprocessing as mp
from multiprocessing import Process, Queue

from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (QMainWindow, QWidget, QFrame, QMessageBox)
from PySide6.QtCore import (Qt, Slot, QRect,
                            QTimer, QObject, QDateTime)

from login_view import LoginWindow
from video_thread_mp import producer
from js08_settings import JS08SettingWidget
from model import JS08Settings
from curve_thread import CurveThread
from clock import clockclock
from consumer import Consumer
from thumbnail_view import ThumbnailView

from visibility_view import VisibilityView
from discernment_view import DiscernmentView

# UI
from resources.main_window import Ui_MainWindow

# Warning Message ignore
import warnings
warnings.filterwarnings('ignore')


class JS08MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, q, _q):
        super(JS08MainWindow, self).__init__()

        self.mp_flag = False

        # if JS08Settings.get('login_flag'):
        #     login_window = LoginWindow()
        #     login_window.sijunglogo.setIcon(QIcon('resources/asset/f_logo.png'))
        #     login_window.exec()
        self.mp_flag = True
            # JS08Settings.set('login_flag', False)

        self.setupUi(self)

        self.q_list = []
        self.q_list_scale = 1440

        self._plot = VisibilityView(self, self.q_list_scale)
        self._polar = DiscernmentView(self)

        self.view = None
        self.km_mile_convert = False

        self.visibility = None
        self.visibility_front = 0
        self.visibility_rear = 0
        self.prevailing_visibility = None

        self.year_date = None
        self.data_date = []
        self.data_time = []
        self.data_vis = []

        self.front_video_widget = VideoWidget(self)
        self.front_video_widget.on_camera_change(JS08Settings.get('front_main'))

        self.rear_video_widget = VideoWidget(self)
        self.rear_video_widget.on_camera_change(JS08Settings.get('rear_main'))

        self.video_horizontalLayout.addWidget(self.front_video_widget.video_frame)
        self.video_horizontalLayout.addWidget(self.rear_video_widget.video_frame)

        self.graph_horizontalLayout.addWidget(self._plot)
        self.polar_horizontalLayout.addWidget(self._polar)

        self.setting_button.setIcon(QIcon('resources/asset/settings.png'))
        self.setting_button.enterEvent = self.btn_on
        self.setting_button.leaveEvent = self.btn_off

        self.time_button.setIcon(QIcon('resources/asset/clock.png'))
        self.timeseries_button_2.setIcon(QIcon('resources/asset/graph.png'))
        self.timeseries_button.setIcon(QIcon('resources/asset/polar.png'))
        self.prevailing_vis_button.setIcon(QIcon('resources/asset/vis.png'))
        self.button.setIcon(QIcon('resources/asset/pre_vis_1.png'))
        self.maxfev_alert.setIcon(QIcon('resources/asset/alert.png'))
        self.maxfev_alert.setToolTip('Optimal parameters not found: Number of calls to function has reached max fev = 5000.')
        self.maxfev_alert.setVisible(JS08Settings.get('maxfev_flag'))

        if self.mp_flag:
            _producer = producer

            p = Process(name='clock', target=clockclock, args=(q,), daemon=True)
            _p = Process(name='producer', target=producer, args=(_q,), daemon=True)

            p.start()
            _p.start()

            self.consumer = Consumer(q)
            self.consumer.poped.connect(self.clock)
            self.consumer.start()

            self.video_thread = CurveThread(_q)
            self.video_thread.poped.connect(self.print_data)
            self.video_thread.start()

        self.click_style = 'border: 1px solid red;'

        self.alert.clicked.connect(self.alert_test)

        self.c_vis_label.mousePressEvent = self.unit_convert
        self.p_vis_label.mousePressEvent = self.unit_convert

        self.label_1hour.mouseDoubleClickEvent = self.thumbnail_click1
        self.label_2hour.mouseDoubleClickEvent = self.thumbnail_click2
        self.label_3hour.mouseDoubleClickEvent = self.thumbnail_click3
        self.label_4hour.mouseDoubleClickEvent = self.thumbnail_click4
        self.label_5hour.mouseDoubleClickEvent = self.thumbnail_click5
        self.label_6hour.mouseDoubleClickEvent = self.thumbnail_click6

        self.setting_button.clicked.connect(self.setting_btn_click)

        JS08Settings.restore_value('maxfev_count')

        self.show()

    def alert_test(self):
        self.alert.setIcon(QIcon('resources/asset/red.png'))
        try:
            strFormat = '%-20s%-10s\n'
            strOut = strFormat % ('Azimuth', 'Visibility (m)')
            for k, v in self.visibility.items():
                v = str(float(v))
                strOut += strFormat % (k, v)
        except AttributeError:
            strOut = 'It has not measured yet.'
            pass
        vis = QMessageBox()
        vis.setStyleSheet('color:rgb(0,0,0);')
        vis.about(self, '8-Way Visibility', f'{strOut}')

    def reset_StyleSheet(self):
        self.label_1hour.setStyleSheet('')
        self.label_2hour.setStyleSheet('')
        self.label_3hour.setStyleSheet('')
        self.label_4hour.setStyleSheet('')
        self.label_5hour.setStyleSheet('')
        self.label_6hour.setStyleSheet('')

    def thumbnail_view(self, file_name: str):
        self.view = ThumbnailView(file_name, int(file_name[2:8]))
        self.view.setGeometry(QRect(self.video_horizontalLayout.geometry().x(),
                                    self.video_horizontalLayout.geometry().y(),
                                    self.video_horizontalLayout.geometry().width(),
                                    self.video_horizontalLayout.geometry().height()))
        self.view.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.view.setWindowModality(Qt.ApplicationModal)
        self.view.show()
        self.view.raise_()

    def thumbnail_show(self):
        self.monitoring_label.setStyleSheet('color: #1c88e3; background-color: #1b3146')
        self.monitoring_label.setText('   Monitoring')
        self.reset_StyleSheet()
        self.view.close()

    @Slot()
    def setting_btn_click(self):
        self.front_video_widget.media_player.stop()
        self.rear_video_widget.media_player.stop()
        self.consumer.pause()

        dlg = JS08SettingWidget()
        dlg.show()
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.exec()

        self.front_video_widget.media_player.play()
        self.rear_video_widget.media_player.play()
        self.consumer.resume()
        self.consumer.start()

    def get_data(self, year, month_day):

        save_path = os.path.join(f'{JS08Settings.get("data_csv_path")}/{JS08Settings.get("front_camera_name")}/{year}')

        if os.path.isfile(f'{save_path}/{month_day}.csv'):
            result = pd.read_csv(f'{save_path}/{month_day}.csv')
            data_datetime = result['date'].tolist()
            data_epoch = result['epoch'].tolist()
            data_visibility = result['visibility'].tolist()

            return data_datetime, data_epoch, data_visibility

        else:
            return [], [], []

    @Slot(str)
    def print_data(self, visibility: dict):
        """
        A function that runs every minute, updating data such as visibility values

        :param visibility: 8-degree Visibility value
        """

        self.convert_visibility(visibility)
        visibility_front = round(float(visibility.get('visibility_front')), 3)
        visibility_rear = round(float(visibility.get('visibility_rear')), 3)

        epoch = QDateTime.currentSecsSinceEpoch()
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))
        year = current_time[:4]
        md = current_time[5:7] + current_time[8:10]

        get_date, get_epoch, self.q_list = self.get_data(year, md)

        if len(self.q_list) == 0 or self.q_list_scale != len(self.q_list):
            self.q_list = []
            for i in range(self.q_list_scale):
                self.q_list.append(visibility_front)
            result_vis = np.mean(self.q_list)
        else:
            self.q_list.pop(0)
            self.q_list.append(visibility_front)
            result_vis = np.mean(self.q_list)

        if len(self.data_date) >= self.q_list_scale or len(self.data_vis) >= self.q_list_scale:
            self.data_date.pop(0)
            self.data_time.pop(0)
            self.data_vis.pop(0)

        self.data_date.append(current_time)
        self.data_time.append(epoch * 1000.0)
        self.data_vis.append(visibility_front)

        save_path_front = os.path.join(
            f'{JS08Settings.get("data_csv_path")}/{JS08Settings.get("front_camera_name")}/{year}')
        save_path_rear = os.path.join(
            f'{JS08Settings.get("data_csv_path")}/{JS08Settings.get("rear_camera_name")}/{year}')
        file_front = f'{save_path_front}/{md}.csv'
        file_rear = f'{save_path_rear}/{md}.csv'

        result_front = pd.DataFrame(columns=['date', 'epoch', 'visibility', 'NE', 'EN', 'ES', 'SE'])
        result_rear = pd.DataFrame(columns=['date', 'epoch', 'visibility', 'SW', 'WS', 'WN', 'NW'])

        if os.path.isfile(f'{file_front}') is False or os.path.isfile(f'{file_rear}') is False:
            os.makedirs(f'{save_path_front}', exist_ok=True)
            os.makedirs(f'{save_path_rear}', exist_ok=True)
            result_front.to_csv(f'{file_front}', mode='w', index=False)
            result_rear.to_csv(f'{file_rear}', mode='w', index=False)

        try:
            result_front['date'] = [self.data_date[-1]]
            result_front['epoch'] = [self.data_time[-1]]
            result_front['visibility'] = visibility_front
            result_front['NE'] = round(float(visibility.get('NE')), 3)
            result_front['EN'] = round(float(visibility.get('EN')), 3)
            result_front['ES'] = round(float(visibility.get('ES')), 3)
            result_front['SE'] = round(float(visibility.get('SE')), 3)

            result_rear['date'] = [self.data_date[-1]]
            result_rear['epoch'] = [self.data_time[-1]]
            result_rear['visibility'] = visibility_rear
            result_rear['SW'] = round(float(visibility.get('SW')), 3)
            result_rear['WS'] = round(float(visibility.get('WS')), 3)
            result_rear['WN'] = round(float(visibility.get('WN')), 3)
            result_rear['NW'] = round(float(visibility.get('NW')), 3)

        except TypeError as e:
            print(f'Occurred error ({current_time}) -\n{e}')

        result_rear.to_csv(f'{file_rear}', mode='a', index=False, header=False)
        result_front.to_csv(f'{file_front}', mode='a', index=False, header=False)

        self.visibility_front = round(float(result_vis), 3)

        self._plot.refresh_stats(self.data_time[-1], self.q_list)
        self._polar.refresh_stats(visibility)

        self.maxfev_alert.setVisible(JS08Settings.get('maxfev_flag'))

    @Slot(str)
    def clock(self, data):

        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(data)))
        self.year_date = current_time[2:4] + current_time[5:7] + current_time[8:10]
        self.real_time_label.setText(current_time)

        try:
            if self.km_mile_convert:
                # self.c_vis_label.setText(f'{format(round(self.visibility_front / 1.609, 2), ",")} mile')
                self.c_vis_label.setText(f'{format(round(self.prevailing_visibility / 1609, 2), ",")} mile')

            elif self.km_mile_convert is False:
                if self.visibility is not None:
                    self.c_vis_label.setText(
                        # f'{format(int(self.visibility.get("visibility_front") * 1000), ",")} m')
                        f'{format(int(self.prevailing_visibility), ",")} m')
        except TypeError:
            pass

        if current_time[-1:] == '0':
            self.thumbnail_refresh()

        if int(self.visibility_front * 1000) <= JS08Settings.get('visibility_alert_limit'):
            self.alert.setIcon(QIcon('resources/asset/red.png'))
        else:
            self.alert.setIcon(QIcon('resources/asset/green.png'))

    def convert_visibility(self, data: dict):
        """
        Function with airstrip visibility unit conversion algorithm applied.
        Currently, 'JS-08' stores visibility values in dict format. It can be converted at once.

        Notes
        --------
        - If visibility ranging from 0 m to less than 400 m, mark it in units of 25 m.
        - If visibility ranging from 400 m to less than 800 m, mark it in units of 50 m.
        .. math:: q (10 ^ { size - 1 } ) + re

        - If the visibility is more than 800 m, mark it in units of 25 m.
        .. math:: q (10 ^{ 2 } ) + re

        Examples
        --------
        >>> Visibility = {'A': 1263, 'B': 695, 'C': 341}
        >>> convert_visibility(Visibility)
        {'A': 1200, 'B': 650, 'C': 325}

        :param data: Visibility data in form of dict
        :return: Visibility data in Converted form of dict
        """

        keys = list(data.keys())
        values = []

        for i in keys:
            if type(data.get(i)) is bool:
                continue
            value = int(float(data.get(i)) * 1000)

            q, re = divmod(value, 100)
            size = len(str(value))

            if value < 400:
                if 0 <= re < 25:
                    re = 0
                elif 25 <= re < 50:
                    re = 25
                elif 50 <= re < 75:
                    re = 50
                elif 75 <= re < 100:
                    re = 75
                data[i] = (q * (10 ** (size - 1)) + re) / 1000

            elif 400 <= value < 800:
                if 0 <= re < 50:
                    re = 0
                elif 50 <= re < 100:
                    re = 50
                data[i] = (q * (10 ** (size - 1)) + re) / 1000

            elif 800 <= value:
                data[i] = (q * (10 ** 2)) / 1000

        self.visibility = data
        disposable = self.visibility.copy()
        del disposable['visibility_front']
        del disposable['visibility_rear']
        for i in disposable.keys():
            values.append(int(disposable.get(i) * 1000))

        values.sort(reverse=True)
        self.prevailing_visibility = values[3]

    def thumbnail_refresh(self):
        one_hour_ago = time.strftime('%Y%m%d%H%M00', time.localtime(time.time() - 3600))
        two_hour_ago = time.strftime('%Y%m%d%H%M00', time.localtime(time.time() - 3600 * 2))
        three_hour_ago = time.strftime('%Y%m%d%H%M00', time.localtime(time.time() - 3600 * 3))
        four_hour_ago = time.strftime('%Y%m%d%H%M00', time.localtime(time.time() - 3600 * 4))
        five_hour_ago = time.strftime('%Y%m%d%H%M00', time.localtime(time.time() - 3600 * 5))
        six_hour_ago = time.strftime('%Y%m%d%H%M00', time.localtime(time.time() - 3600 * 6))

        # one_min_ago = time.strftime('%Y%m%d%H%M00', time.localtime(time.time() - 60))
        # two_min_ago = time.strftime('%Y%m%d%H%M00', time.localtime(time.time() - 60 * 2))
        # three_min_ago = time.strftime('%Y%m%d%H%M00', time.localtime(time.time() - 60 * 3))
        # four_min_ago = time.strftime('%Y%m%d%H%M00', time.localtime(time.time() - 60 * 4))
        # five_min_ago = time.strftime('%Y%m%d%H%M00', time.localtime(time.time() - 60 * 5))
        # six_min_ago = time.strftime('%Y%m%d%H%M00', time.localtime(time.time() - 60 * 6))

        self.label_1hour_time.setText(time.strftime('%H:%M', time.localtime(time.time() - 3600)))
        self.label_2hour_time.setText(time.strftime('%H:%M', time.localtime(time.time() - 3600 * 2)))
        self.label_3hour_time.setText(time.strftime('%H:%M', time.localtime(time.time() - 3600 * 3)))
        self.label_4hour_time.setText(time.strftime('%H:%M', time.localtime(time.time() - 3600 * 4)))
        self.label_5hour_time.setText(time.strftime('%H:%M', time.localtime(time.time() - 3600 * 5)))
        self.label_6hour_time.setText(time.strftime('%H:%M', time.localtime(time.time() - 3600 * 6)))

        # self.label_1hour_time.setText(time.strftime('%H:%M', time.localtime(time.time() - 60)))
        # self.label_2hour_time.setText(time.strftime('%H:%M', time.localtime(time.time() - 60 * 2)))
        # self.label_3hour_time.setText(time.strftime('%H:%M', time.localtime(time.time() - 60 * 3)))
        # self.label_4hour_time.setText(time.strftime('%H:%M', time.localtime(time.time() - 60 * 4)))
        # self.label_5hour_time.setText(time.strftime('%H:%M', time.localtime(time.time() - 60 * 5)))
        # self.label_6hour_time.setText(time.strftime('%H:%M', time.localtime(time.time() - 60 * 6)))

        if os.path.isfile(
                f'{JS08Settings.get("image_save_path")}/thumbnail/'
                f'{JS08Settings.get("front_camera_name")}/{self.year_date}/{one_hour_ago}.jpg'):
            self.label_1hour.setPixmap(
                QPixmap(f'{JS08Settings.get("image_save_path")}/thumbnail/'
                        f'{JS08Settings.get("front_camera_name")}/{self.year_date}/{one_hour_ago}.jpg')
                    .scaled(self.label_1hour.width(), self.label_1hour.height(), Qt.IgnoreAspectRatio))

        if os.path.isfile(
                f'{JS08Settings.get("image_save_path")}/thumbnail/'
                f'{JS08Settings.get("front_camera_name")}/{self.year_date}/{two_hour_ago}.jpg'):
            self.label_2hour.setPixmap(
                QPixmap(f'{JS08Settings.get("image_save_path")}/thumbnail/'
                        f'{JS08Settings.get("front_camera_name")}/{self.year_date}/{two_hour_ago}.jpg')
                    .scaled(self.label_2hour.width(), self.label_2hour.height(), Qt.IgnoreAspectRatio))

        if os.path.isfile(
                f'{JS08Settings.get("image_save_path")}/thumbnail/'
                f'{JS08Settings.get("front_camera_name")}/{self.year_date}/{three_hour_ago}.jpg'):
            self.label_3hour.setPixmap(
                QPixmap(f'{JS08Settings.get("image_save_path")}/thumbnail/'
                        f'{JS08Settings.get("front_camera_name")}/{self.year_date}/{three_hour_ago}.jpg')
                    .scaled(self.label_3hour.width(), self.label_3hour.height(), Qt.IgnoreAspectRatio))

        if os.path.isfile(
                f'{JS08Settings.get("image_save_path")}/thumbnail/'
                f'{JS08Settings.get("front_camera_name")}/{self.year_date}/{four_hour_ago}.jpg'):
            self.label_4hour.setPixmap(
                QPixmap(f'{JS08Settings.get("image_save_path")}/thumbnail/'
                        f'{JS08Settings.get("front_camera_name")}/{self.year_date}/{four_hour_ago}.jpg')
                    .scaled(self.label_4hour.width(), self.label_4hour.height(), Qt.IgnoreAspectRatio))

        if os.path.isfile(
                f'{JS08Settings.get("image_save_path")}/thumbnail/'
                f'{JS08Settings.get("front_camera_name")}/{self.year_date}/{five_hour_ago}.jpg'):
            self.label_5hour.setPixmap(
                QPixmap(f'{JS08Settings.get("image_save_path")}/thumbnail/'
                        f'{JS08Settings.get("front_camera_name")}/{self.year_date}/{five_hour_ago}.jpg')
                    .scaled(self.label_5hour.width(), self.label_5hour.height(), Qt.IgnoreAspectRatio))

        if os.path.isfile(
                f'{JS08Settings.get("image_save_path")}/thumbnail/'
                f'{JS08Settings.get("front_camera_name")}/{self.year_date}/{six_hour_ago}.jpg'):
            self.label_6hour.setPixmap(
                QPixmap(f'{JS08Settings.get("image_save_path")}/thumbnail/'
                        f'{JS08Settings.get("front_camera_name")}/{self.year_date}/{six_hour_ago}.jpg')
                    .scaled(self.label_6hour.width(), self.label_6hour.height(), Qt.IgnoreAspectRatio))
        self.update()

    # Event
    def thumbnail_click1(self, e):
        name = self.label_1hour_time.text()[:2] + self.label_1hour_time.text()[3:]
        epoch = time.strftime('%Y%m%d', time.localtime(time.time()))
        self.thumbnail_view(epoch + name + '00')

        self.reset_StyleSheet()
        self.label_1hour.setStyleSheet(self.click_style)
        self.monitoring_label.setStyleSheet('color: #ffffff; background-color: #1b3146')
        self.monitoring_label.setText(f' {self.label_1hour_time.text()} image')

        QTimer.singleShot(2000, self.thumbnail_show)

    def thumbnail_click2(self, e):
        name = self.label_2hour_time.text()[:2] + self.label_2hour_time.text()[3:]
        epoch = time.strftime('%Y%m%d', time.localtime(time.time()))
        self.thumbnail_view(epoch + name + '00')

        self.reset_StyleSheet()
        self.label_2hour.setStyleSheet(self.click_style)
        self.monitoring_label.setStyleSheet('color: #ffffff; background-color: #1b3146')
        self.monitoring_label.setText(f' {self.label_2hour_time.text()} image')

        QTimer.singleShot(2000, self.thumbnail_show)

    def thumbnail_click3(self, e):
        name = self.label_3hour_time.text()[:2] + self.label_3hour_time.text()[3:]
        epoch = time.strftime('%Y%m%d', time.localtime(time.time()))
        self.thumbnail_view(epoch + name + '00')

        self.reset_StyleSheet()
        self.label_3hour.setStyleSheet(self.click_style)
        self.monitoring_label.setStyleSheet('color: #ffffff; background-color: #1b3146')
        self.monitoring_label.setText(f' {self.label_3hour_time.text()} image')

        QTimer.singleShot(2000, self.thumbnail_show)

    def thumbnail_click4(self, e):
        name = self.label_4hour_time.text()[:2] + self.label_4hour_time.text()[3:]
        epoch = time.strftime('%Y%m%d', time.localtime(time.time()))
        self.thumbnail_view(epoch + name + '00')

        self.reset_StyleSheet()
        self.label_4hour.setStyleSheet(self.click_style)
        self.monitoring_label.setStyleSheet('color: #ffffff; background-color: #1b3146')
        self.monitoring_label.setText(f' {self.label_4hour_time.text()} image')

        QTimer.singleShot(2000, self.thumbnail_show)

    def thumbnail_click5(self, e):
        name = self.label_5hour_time.text()[:2] + self.label_5hour_time.text()[3:]
        epoch = time.strftime('%Y%m%d', time.localtime(time.time()))
        self.thumbnail_view(epoch + name + '00')

        self.reset_StyleSheet()
        self.label_5hour.setStyleSheet(self.click_style)
        self.monitoring_label.setStyleSheet('color: #ffffff; background-color: #1b3146')
        self.monitoring_label.setText(f' {self.label_5hour_time.text()} image')

        QTimer.singleShot(2000, self.thumbnail_show)

    def thumbnail_click6(self, e):
        name = self.label_6hour_time.text()[:2] + self.label_6hour_time.text()[3:]
        epoch = time.strftime('%Y%m%d', time.localtime(time.time()))
        self.thumbnail_view(epoch + name + '00')

        self.reset_StyleSheet()
        self.label_6hour.setStyleSheet(self.click_style)
        self.monitoring_label.setStyleSheet('color: #ffffff; background-color: #1b3146')
        self.monitoring_label.setText(f' {self.label_6hour_time.text()} image')

        QTimer.singleShot(2000, self.thumbnail_show)

    def btn_on(self, event):
        self.setting_button.setIcon(QIcon('resources/asset/settings_on.png'))

    def btn_off(self, event):
        self.setting_button.setIcon(QIcon('resources/asset/settings.png'))

    def unit_convert(self, event):
        if self.km_mile_convert:
            self.km_mile_convert = False
        elif self.km_mile_convert is False:
            self.km_mile_convert = True

    def keyPressEvent(self, e):
        """Override function QMainwindow KeyPressEvent that works when key is pressed"""
        if e.key() == Qt.Key_F:
            self.showFullScreen()
            self.thumbnail_refresh()
        if e.key() == Qt.Key_D:
            self.showNormal()
            self.thumbnail_refresh()
        if e.modifiers() & Qt.ControlModifier:
            if e.key() == Qt.Key_W:
                self.close()
                sys.exit()

    def closeEvent(self, e):
        self.consumer.stop()
        self.video_thread.stop()
        print(f'Close time: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')


class VideoWidget(QWidget):
    """Video stream player using QVideoWidget"""

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        args = [
            '--rtsp-frame-buffer-size=400000',
            '--quiet',
            '--sout-x264-keyint=25',
        ]

        self.instance = vlc.Instance(args)
        self.instance.log_unset()

        self.media_player = self.instance.media_player_new()
        # Current camera must be 'PNM-9031RV'
        self.media_player.video_set_aspect_ratio('20:9')

        self.video_frame = QFrame()

        if sys.platform == 'win32':
            self.media_player.set_hwnd(self.video_frame.winId())

    def on_camera_change(self, uri: str):
        if uri[:4] == 'rtsp':
            self.media_player.set_media(self.instance.media_new(uri))
            self.media_player.play()
        else:
            pass


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QGuiApplication
    from model import JS08Settings

    JS08Settings.set('first_step', True)

    print(f'Start time: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')

    mp.freeze_support()
    q = Queue()
    _q = Queue()

    # _producer = producer
    #
    # p = Process(name='clock', target=clockclock, args=(q,), daemon=True)
    # _p = Process(name='producer', target=_producer, args=(_q,), daemon=True)
    #
    # p.start()
    # _p.start()

    os.makedirs(f'{JS08Settings.get("data_csv_path")}', exist_ok=True)
    os.makedirs(f'{JS08Settings.get("target_csv_path")}', exist_ok=True)
    os.makedirs(f'{JS08Settings.get("rgb_csv_path")}', exist_ok=True)
    os.makedirs(f'{JS08Settings.get("image_save_path")}', exist_ok=True)

    app = QApplication(sys.argv)
    screen_size = QGuiApplication.screens()[0].geometry()
    width, height = screen_size.width(), screen_size.height()
    if width > 1920 or height > 1080:
        QMessageBox.warning(None, 'Warning', 'JS08 is based on FHD screen.')
    window = JS08MainWindow(q, _q)
    sys.exit(app.exec())
