#!/usr/bin/env python3
#
# Copyright 2021-2022 Sijung Co., Ltd.
#
# Authors:
#     cotjdals5450@gmail.com (Seong Min Chae)
#     5jx2oh@gmail.com (Jongjin Oh)

import os
import sys
import time
import collections

import pandas as pd
from typing import List

from PySide6.QtGui import QPainter, QBrush, QColor, QPen
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import (Slot, QPointF, QDateTime,
                            QPoint, QTime)
from PySide6.QtCharts import (QChartView, QLineSeries, QValueAxis,
                              QChart, QDateTimeAxis, QAreaSeries)

from model import JS08Settings


class VisibilityView(QChartView):

    def __init__(self, parent: QWidget, maxlen: int):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumSize(200, 200)
        self.setMaximumSize(800, 600)
        # self.m_callouts = List[Callout] = []

        self.maxlen = maxlen
        self._value_pos = QPoint()
        self.rect_flip_x = -120

        now = QDateTime.currentSecsSinceEpoch()
        str_now = str(now)
        sequence = '0'
        indicies = (10, 10)
        now = int(sequence.join([str_now[:indicies[0] - 1], str_now[indicies[1]:]]))

        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))
        year = current_time[:4]
        md = current_time[5:7] + current_time[8:10]

        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)

        chart = QChart()
        chart.legend().setVisible(False)

        self.setChart(chart)
        self.chart().setTheme(QChart.ChartThemeDark)
        self.chart().setBackgroundBrush(QBrush(QColor('#16202a')))

        self.series = QLineSeries(name='Prevailing Visibility')
        chart.addSeries(self.series)

        # seongmin 추가
        self.series_2 = QLineSeries(name='Predict Visibility')
        chart.addSeries(self.series_2)
        
        
        
        axis_x = QDateTimeAxis()
        axis_x.setFormat('MM/dd hh:mm')
        axis_x.setTitleText('Time')

        save_path = os.path.join(f'{JS08Settings.get("data_csv_path")}/Prevailing_Visibility/{year}')
        file = f'{save_path}/{md}.csv'

        if os.path.isfile(f'{file}') is False:
            print('NOT FOUND data csv file')
            zeros = [(t * 1000.0, -1) for t in range(now - maxlen * 60, now, 60)]
            self.data = collections.deque(zeros, maxlen=maxlen)
            self.data_2 = collections.deque(zeros, maxlen=maxlen)

            left = QDateTime.fromMSecsSinceEpoch(int(self.data[0][0]))
            right = QDateTime.fromMSecsSinceEpoch(int(self.data[-1][0]))
            axis_x.setRange(left, right)
            chart.setAxisX(axis_x, self.series)
            chart.setAxisX(axis_x, self.series_2)
        else:
            path = os.path.join(f'{JS08Settings.get("data_csv_path")}/Prevailing_Visibility/{year}')
            mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
            res = list(sorted(os.listdir(path), key=mtime))

            if len(res) >= 2:
                JS08Settings.set('first_step', False)

            result_today = pd.read_csv(file)

            epoch_today = result_today['epoch'].tolist()
            vis_list_today = result_today['prev'].tolist()
            
            #seongmin 추가
            predict_folder_path = f"predict/{year}{md}"
            predict_file_path = f"{predict_folder_path}/{year}{md}.csv"
            predict_result_today = pd.read_csv(predict_file_path)
            
            predict_epoch_today = predict_result_today['epoch'].tolist()
            predict_vis_list_today = predict_result_today['predict_value'].tolist()
            
            data = []
            data_2 = []
            if JS08Settings.get('first_step') is False and len(res) > 1:
                if md == '0101':
                    save_path = os.path.join(f'{JS08Settings.get("data_csv_path")}/'
                                             f'Prevailing_Visibility/{int(year) - 1}')
                    year = str(int(year)-1)
                yesterday_file = f'{save_path}/{res[-2]}'
                result_yesterday = pd.read_csv(yesterday_file)

                epoch_yesterday = result_yesterday['epoch'].tolist()
                vis_list_yesterday = result_yesterday['prev'].tolist()
                
                #seongmin 추가
                predict_yesterday_folder_path = f"predict/{year}{res[-2][:-4]}"
                predict_yesterday_file_path = f"{predict_yesterday_folder_path}/{year}{res[-2]}"
                predict_result_yesterday = pd.read_csv(predict_yesterday_file_path)
                
                predict_epoch_yesterday = predict_result_yesterday['epoch'].tolist()
                predict_vis_list_yesterday = predict_result_yesterday['predict_value'].tolist()

                # 전날꺼 저장_yesterday
                for i in range(len(epoch_yesterday)):
                    data.append((epoch_yesterday[i], vis_list_yesterday[i]))
                    
                    # seongmin 추가
                    if epoch_yesterday[i] in predict_epoch_yesterday:
                        idx = predict_epoch_yesterday.index(epoch_yesterday[i])
                        data_2.append((epoch_yesterday[i], predict_vis_list_yesterday[idx]))
                    else:
                        pass
                    
            # 당일꺼 저장_today
            for i in range(len(epoch_today)):
                data.append((epoch_today[i], vis_list_today[i]))
                
                # seongmin 추가
                if epoch_today[i] in predict_epoch_today:
                    idx = predict_epoch_today.index(epoch_today[i])
                    data_2.append((epoch_today[i], predict_vis_list_today[idx]))
                else:
                    pass

            self.data = collections.deque(data, maxlen=1440)
            self.data_2 = collections.deque(data_2, maxlen=1440)
            

            left = QDateTime.fromMSecsSinceEpoch(int(self.data[0][0]))
            right = QDateTime.fromMSecsSinceEpoch(int(self.data[-1][0]))
            axis_x.setRange(left, right)
            chart.setAxisX(axis_x, self.series)
            chart.setAxisX(axis_x, self.series_2)

        axis_y = QValueAxis()
        axis_y.setRange(0, 20)
        axis_y.setLabelFormat('%d km')
        axis_y.setTitleText('Distance (km)')
        chart.setAxisY(axis_y, self.series)
        chart.setAxisY(axis_y, self.series_2)

        data_point = [QPointF(t, v) for t, v in self.data]
        self.series.append(data_point)
        
        # seongmin 추가
        # data_point_2 = [QPointF(t, v-1) for t, v in self.data if v-5> 0]
        data_point_2 =  [QPointF(t, v) for t, v in self.data_2]
        self.series_2.append(data_point_2)
        pen = QPen(QColor(250,180,0))
        pen.setWidth(1)
        self.series_2.setPen(pen)
        # self.series.setPen(pen)
        
        # print("TEST : ", data_point_2[0])

    @Slot(float, list)
    def refresh_stats(self, epoch: float, vis_list: list):
        if len(vis_list) == 0:
            vis_list = [0]
        prev_vis = self.prevailing_visibility(vis_list)
        self.data.append((epoch, prev_vis))

        left = QDateTime.fromMSecsSinceEpoch(int(self.data[0][0]))
        right = QDateTime.fromMSecsSinceEpoch(int(self.data[-1][0]))

        self.chart().axisX().setRange(left, right)

        data_point = [QPointF(t, v) for t, v in self.data]
        self.series.replace(data_point)
        
        # seongmin 추가
        data_point_2 = [QPointF(t, v-1) for t, v in self.data if v-1 > 0]
        self.series_2.replace(data_point_2)

    def prevailing_visibility(self, vis: list) -> float:
        if None in vis:
            return 0

        sorted_vis = sorted(vis, reverse=True)
        prevailing = sorted_vis[(len(sorted_vis) - 1) // 2]

        return prevailing


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.resize(600, 400)
    visibility_view = VisibilityView(window, 1440)
    # visibility_view.refresh_stats(visibility)
    window.setCentralWidget(visibility_view)
    window.show()
    sys.exit(app.exec())
