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

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import (Slot, QPointF, QDateTime,
                            QPoint, QTime, Qt)
from PySide6.QtCharts import (QChartView, QLineSeries, QValueAxis,
                              QChart, QDateTimeAxis, QAreaSeries, QScatterSeries)

from model import JS08Settings

class Vis_Chart(QWidget):
    """ 실시간 시정 출력 그래프 위젯 """
    
    # 초기화 선언
    def __init__(self, parent=None, max_value = 50):
        super().__init__(parent) 

        # chart에 넣을 Series 선언
        # 현재 시정
        # self.current_vis_series = QLineSeries() # 직선 Series
        # self.current_vis_scatter = QScatterSeries() # 노란 산점도 Series
        # self.current_vis_scatter_2 = QScatterSeries() # 하얀 산점도 Series
        # current_color = QColor(32,159,223)
        # # 직선 Series에 입힐 색과 두께 설정
        # pen = QPen(current_color)        
        # pen.setWidth(3)
        # self.current_vis_series.setPen(pen)
        
        # # 산점도 Series들의 색상과 두께 설정
        # self.current_vis_scatter.setBorderColor(current_color)
        # self.current_vis_scatter.setBrush(current_color)
        
        # self.current_vis_scatter_2.setMarkerSize(8)
        # self.current_vis_scatter_2.setBorderColor(QColor(225,225,225))
        # self.current_vis_scatter_2.setBrush(QColor(225,225,225))
        
        
        # 예측 시정
        self.vis_series = QLineSeries() # 직선 Series
        self.vis_scatter = QScatterSeries() # 파란 산점도 Series
        self.vis_scatter_2 = QScatterSeries() # 하얀 산점도 Series
        
        # 직선 Series에 입힐 색과 두께 설정
        prediction_color = QColor(250,180,0)
        pen = QPen(prediction_color)
        pen.setWidth(4)
        self.vis_series.setPen(pen)
        
        # 산점도 Series들의 색상과 두께 설정
        self.vis_scatter.setBorderColor(prediction_color)
        self.vis_scatter.setBrush(prediction_color)
        
        self.vis_scatter_2.setMarkerSize(6)
        self.vis_scatter_2.setBorderColor(QColor(225,225,225))
        self.vis_scatter_2.setBrush(QColor(225,225,225))
        
        epoch = QDateTime.currentSecsSinceEpoch()
        print("epoch!!!!!", epoch)
        print(epoch * 1000.0)
        
        # 현재 시간 저장
        self.now = QDateTime.currentDateTime()
        # 몇초 전까지 보여주는지 설정 값
        self.viewLimit = 14400
        # 몇초 단위로 저장하는지 설정
        self.timetick = 3600
        # 각 Series에 랜덤으로 몇초 전까지의 데이터들을 임의로 저장 
        for i in range(0, self.viewLimit, self.timetick):
            # cur = 20 * random.random()
            # time = self.now.addSecs(i).toMSecsSinceEpoch()  #Processing to append to QLineSeries
            print("addsec:", i)
            re_time = self.now.addSecs(i).toSecsSinceEpoch() 
            print(re_time)
            print(re_time * 1000.0)
            self.vis_series.append(QPointF(re_time * 1000.0 , 0))
            self.vis_scatter.append(QPointF(re_time* 1000.0, 0))
            self.vis_scatter_2.append(QPointF(re_time* 1000.0, 0))

        # Seires를 담을 Qchart를 선언
        self.chart = QChart()
        
        # 그래프 그릴 때 애니메이션 효과 적용
        # self.chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Qchart에 Series들 추가
        # self.chart.addSeries(self.current_vis_series)
        # self.chart.addSeries(self.current_vis_scatter)
        # self.chart.addSeries(self.current_vis_scatter_2)
        
        self.chart.addSeries(self.vis_series)
        self.chart.addSeries(self.vis_scatter)
        self.chart.addSeries(self.vis_scatter_2)
        
        # Qchart 설정
        self.chart.legend().hide()        
        # # Qchart의 타이틀 글자 색, 크기 설정 
        self.font = QFont()
        self.font.setPixelSize(20)        
        self.font.setBold(3)
        self.chart.setTitle("Prediction Visibility Graph")
        self.chart.setTitleFont(self.font)
        self.chart.setTitleBrush(QBrush(QColor("white")))
        # Qchart 여백 제거
        self.chart.layout().setContentsMargins(0,0,0,0)
        # Qchart 테두리 라운드 제거
        self.chart.setBackgroundRoundness(0)
        # Qchart 배경색 지정
        self.chart.setBackgroundBrush(QBrush(QColor(22,32,42)))
        
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setAnimationDuration(1000)
        
        
        # self.chart.setPlotArea(QRectF(0,0,1000,500))

        
        # ChartView 선언
        self.chart_view = QChartView()
        
        self.chart_view.setMinimumSize(300, 300)
        self.chart_view.setMaximumSize(450, 350)
        
        # ChartView에 Qchart를 탑재
        self.chart_view.setChart(self.chart)
        # ChartView 안에 있는 내용(차트, 글자 등)들을 부드럽게 해주는 설정
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        # x,y 축의 글자 색 지정
        axisBrush = QBrush(QColor("white"))

        #Create X axis
        time_axis_x = QDateTimeAxis()
        time_axis_x.setFormat("hh:mm")
        time_axis_x.setTitleText("Time")
        time_axis_x.setTitleBrush(axisBrush)
        time_axis_x.setLabelsBrush(axisBrush)
        time_axis_x.setTickCount(8)
        self.chart.addAxis(time_axis_x, Qt.AlignBottom)

        self.vis_series.attachAxis(time_axis_x)
        self.vis_scatter.attachAxis(time_axis_x)
        self.vis_scatter_2.attachAxis(time_axis_x)

        #Create Y1 axis
        cur_axis_y = QValueAxis()
        cur_axis_y.setTitleText("Visibility(km)")
        cur_axis_y.setLinePenColor(self.vis_scatter_2.pen().color())  #Make the axis and chart colors the same
        cur_axis_y.setTitleBrush(axisBrush)
        cur_axis_y.setLabelsBrush(axisBrush)
        cur_axis_y.setRange(0, 10)
        cur_axis_y.setTickCount(6)
        self.chart.addAxis(cur_axis_y, Qt.AlignLeft)
        self.vis_series.attachAxis(cur_axis_y)
        self.vis_scatter.attachAxis(cur_axis_y)
        self.vis_scatter_2.attachAxis(cur_axis_y)

        # 새로운 데이터를 계속 호출하는 QThread 클래스 선언
        # self.pw = ValueWorker("Test")
        # 전송 받은 시정 값을 appendData 함수의 value 인자값에 직접 전달
        # self.pw.dataSent.connect(self.appendData)
        # QThread 시작
        # self.pw.start()
        self.__updateAxis()
        
    
    def appendData(self, pv, value):
        """ Series에 가장 오래된 데이터를 지우고 새로운 데이터를 추가하는 함수 """
        # if len(self.vis_series) == (self.viewLimit//self.timetick):
        #     self.vis_series.remove(0)
        #     self.vis_scatter.remove(0)
        #     self.vis_scatter_2.remove(0)
        
        # 시리즈에 있는 값들 전부 제거
        # self.current_vis_series.clear()
        # self.current_vis_scatter.clear()
        # self.current_vis_scatter_2.clear()
        
        self.vis_series.clear()
        self.vis_scatter.clear()
        self.vis_scatter_2.clear()
        
        dt = QDateTime.currentDateTime()
        self.vis_series.append(QPointF(dt.toSecsSinceEpoch() * 1000.0, pv))
        self.vis_scatter.append(QPointF(dt.toSecsSinceEpoch() * 1000.0, pv))
        self.vis_scatter_2.append(QPointF(dt.toSecsSinceEpoch() * 1000.0, pv))
        
        for i in range(5, value.shape[1]+1, 6):
            time_tick = 600 * i
            fu_time = dt.addSecs(600 + time_tick).toSecsSinceEpoch()  #Processing to append to QLineSeries
            print("QDate time",fu_time)
            real_value = value[0][i][0]
            self.vis_series.append(QPointF(fu_time* 1000.0, real_value))
            self.vis_scatter.append(QPointF(fu_time* 1000.0, real_value))
            self.vis_scatter_2.append(QPointF(fu_time* 1000.0, real_value))
            self.__updateAxis()
        
        # 마지막 예측 시정에 따라 그래프 색 변경
        if real_value < 4 and real_value > 2:
            prediction_color = QColor(250,180,0)
        elif real_value <= 2:
            prediction_color = QColor(250,0,0)
        else:
            prediction_color = QColor(32,159,223)
        
        self.vis_scatter.setBorderColor(prediction_color)
        self.vis_scatter.setBrush(prediction_color)
        pen = QPen(prediction_color)
        pen.setWidth(4)
        self.vis_series.setPen(pen)
        
        self.__updateAxis()
        
        del value
    
    def __updateAxis(self):
        """ Qchart의 X축의 범위를 재지정하는 함수 """
        
        
        pvs = self.vis_series.pointsVector()
        print("pvs : ", pvs)
        print("pvs 0", int(pvs[0].x()))
        dtStart = QDateTime.fromMSecsSinceEpoch(int(pvs[0].x()))
        print("dtStart : ", dtStart)
        # if len(self.vis_series) == self.viewLimit:
        #     dtLast = QDateTime.fromMSecsSinceEpoch(int(pvs[-1].x()))
        # else:
        dtLast = dtStart.addSecs(self.viewLimit)
        print("qchart recent time : ", dtLast)
        ax = self.chart.axisX()
        ax.setRange(dtStart, dtLast)
        # return chart_view
        
class Predict_VisibilityView(QChartView):

    def __init__(self, parent: QWidget, maxlen: int):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumSize(200, 200)
        self.setMaximumSize(600, 400)
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

        self.series = QLineSeries(name='Predict Visibility')
        chart.addSeries(self.series)

        axis_x = QDateTimeAxis()
        axis_x.setFormat('MM/dd hh:mm')
        axis_x.setTitleText('Time')

        # save_path = os.path.join(f'{JS08Settings.get("data_csv_path")}/Predict_Visibility/{year}')
        predict_path = f"predict/{current_time[:8]}"
        
        file = f'{predict_path}/{predict_path[:8]}.csv'
        
        # 실행할 때 데이터 파일이 없으면
        if os.path.isfile(f'{file}') is False:
            print('NOT FOUND data csv file')
            zeros = [(t * 1000.0, -1) for t in range(now - maxlen * 60, now, 60)]
            self.data = collections.deque(zeros, maxlen=maxlen)

            left = QDateTime.fromMSecsSinceEpoch(int(self.data[0][0]))
            right = QDateTime.fromMSecsSinceEpoch(int(self.data[-1][0]))
            axis_x.setRange(left, right)
            chart.setAxisX(axis_x, self.series)
        else:
            # path = os.path.join(f'{JS08Settings.get("data_csv_path")}/Predict_Visibility/{year}')
            
            # 이게머지?
            # mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
            
            # res = list(sorted(os.listdir(path), key=mtime))

            # if len(res) >= 2:
            #     JS08Settings.set('first_step', False)

            result_today = pd.read_csv(file)

            epoch_today = result_today['epoch'].tolist()
            vis_list_today = result_today['prev'].tolist()

            data = []

            # if JS08Settings.get('first_step') is False and len(res) > 1:
            #     if md == '0101':
            #         save_path = os.path.join(f'{JS08Settings.get("data_csv_path")}/'
            #                                  f'Predict_Visibility/{int(year) - 1}')
            #     yesterday_file = f'{save_path}/{res[-2]}'
            #     result_yesterday = pd.read_csv(yesterday_file)

            #     epoch_yesterday = result_yesterday['epoch'].tolist()
            #     vis_list_yesterday = result_yesterday['prev'].tolist()

            #     for i in range(len(epoch_yesterday)):
            #         data.append((epoch_yesterday[i], vis_list_yesterday[i]))

            for i in range(len(epoch_today)):
                data.append((epoch_today[i], vis_list_today[i]))

            self.data = collections.deque(data, maxlen)

            left = QDateTime.fromMSecsSinceEpoch(int(self.data[0][0]))
            right = QDateTime.fromMSecsSinceEpoch(int(self.data[-1][0]))
            axis_x.setRange(left, right)
            chart.setAxisX(axis_x, self.series)

        axis_y = QValueAxis()
        axis_y.setRange(0, 20)
        axis_y.setLabelFormat('%d km')
        axis_y.setTitleText('Distance (km)')
        chart.setAxisY(axis_y, self.series)

        data_point = [QPointF(t, v) for t, v in self.data]
        self.series.append(data_point)

    @Slot(float, list)
    def refresh_stats(self, epoch: float, vis_list: list):
        if len(vis_list) == 0:
            vis_list = [0]
        prev_vis = self.Predict_visibility(vis_list)
        self.data.append((epoch, prev_vis))

        left = QDateTime.fromMSecsSinceEpoch(int(self.data[0][0]))
        right = QDateTime.fromMSecsSinceEpoch(int(self.data[-1][0]))

        self.chart().axisX().setRange(left, right)

        data_point = [QPointF(t, v) for t, v in self.data]
        self.series.replace(data_point)

    def Predict_visibility(self, vis: list) -> float:
        if None in vis:
            return 0

        sorted_vis = sorted(vis, reverse=True)
        Predict = sorted_vis[(len(sorted_vis) - 1) // 2]

        return Predict


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
