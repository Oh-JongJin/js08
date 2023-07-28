#!/usr/bin/env python3
#
# Copyright 2021-2022 Sijung Co., Ltd.
#
# Authors:
#     cotjdals5450@gmail.com (Seong Min Chae)
#     5jx2oh@gmail.com (Jongjin Oh)

import time
import numpy as np

from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF
from PySide6.QtCharts import (QChartView, QLegend, QLineSeries,
                              QPolarChart, QValueAxis, QChart,
                              QAreaSeries, QCategoryAxis)
from model import JS08Settings


class DiscernmentView(QChartView):

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumSize(200, 200)
        self.setMaximumSize(600, 400)

        chart = QPolarChart()
        chart.legend().setVisible(False)
        self.setChart(chart)
        self.chart().setTheme(QChart.ChartThemeDark)
        self.chart().setBackgroundBrush(QBrush(QColor('#16202a')))

        self.past_dataDist = None

        self.axis_x = QValueAxis()
        self.axis_x.setTickCount(9)
        self.axis_x.setRange(0, 360)
        self.axis_x.setLabelFormat('%d \xc2\xb0')
        self.axis_x.setReverse(True)

        self.axis_y = QValueAxis()
        self.axis_y.setRange(0, 6)
        self.axis_y.setMax(20)
        self.axis_y.setLabelFormat('%d km')

        self.axis_distance = QCategoryAxis()
        self.axis_distance.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        self.axis_distance.setRange(0, 360)
        self.axis_distance.setLabelsFont(QFont('Noto Sans', 15))

        data = np.arange(22.5, 360, 45)
        self.dataName = ['NE', 'EN', 'ES', 'SE', 'SW', 'WS', 'WN', 'NW']
        self.dataDist = [0, 0, 0, 0, 0, 0, 0, 0]

        for name,dist, dt in zip(self.dataName, self.dataDist, data):
            self.axis_distance.append(f'{name} ({dist})', dt)
        self.axis_distance.setGridLineVisible(False)
        self.axis_distance.setLineVisible(False)

        self.lowerLine = QLineSeries()
        self.upperLine = QLineSeries()

        for i in range(0, 46):
            self.upperLine.append(i, 0)
        for i in range(45, 91):
            self.upperLine.append(i, 0)
        for i in range(90, 136):
            self.upperLine.append(i, 0)
        for i in range(135, 181):
            self.upperLine.append(i, 0)
        for i in range(180, 226):
            self.upperLine.append(i, 0)
        for i in range(226, 271):
            self.upperLine.append(i, 0)
        for i in range(270, 316):
            self.upperLine.append(i, 0)
        for i in range(315, 361):
            self.upperLine.append(i, 0)

        self.area = QAreaSeries()
        self.area.setLowerSeries(self.lowerLine)
        self.area.setUpperSeries(self.upperLine)
        self.area.setOpacity(0.7)

        chart.addSeries(self.area)
        chart.addAxis(self.axis_distance, QPolarChart.PolarOrientationAngular)
        chart.setAxisX(self.axis_x, self.area)
        chart.setAxisY(self.axis_y, self.area)

    def refresh_stats(self, data: dict):
        self.upperLine.clear()
        # del data['visibility_front']
        # del data['visibility_rear']

        dataDist = list(data.values())

        for i in range(0, 46):
            self.upperLine.append(i, data.get('NE'))
        for i in range(45, 91):
            self.upperLine.append(i, data.get('EN'))
        for i in range(90, 136):
            self.upperLine.append(i, data.get('ES'))
        for i in range(135, 181):
            self.upperLine.append(i, data.get('SE'))
        for i in range(180, 226):
            self.upperLine.append(i, data.get('SW'))
        for i in range(226, 271):
            self.upperLine.append(i, data.get('WS'))
        for i in range(270, 316):
            self.upperLine.append(i, data.get('WN'))
        for i in range(315, 361):
            self.upperLine.append(i, data.get('NW'))

        if self.past_dataDist is None:
            for name, dist, dt in zip(self.dataName, dataDist, data):
                self.axis_distance.replaceLabel(f'{name} ({self.dataDist[self.dataName.index(name)]})',
                                                f'{name} ({dist})')
        else:
            for name, dist, dt in zip(self.dataName, dataDist, data):
                self.axis_distance.replaceLabel(f'{name} ({self.past_dataDist[self.dataName.index(name)]})',
                                                f'{name} ({dist})')
        self.past_dataDist = dataDist

    def mousePressEvent(self, event):

        print(f'flag: {JS08Settings.get("maxfev_flag")}, count: {JS08Settings.get("maxfev_count")}')


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow

    visibility = {'visibility_front': '18.829', 'visibility_rear': '0.192',
                  'NE': 20.000, 'EN': 7.208,
                  'ES': 20.000, 'SE': 1.015,
                  'SW': 2.613, 'WS': 20.000,
                  'WN': 20.000, 'NW': 20.000}

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.resize(600, 400)
    discernment_view = DiscernmentView(window)
    discernment_view.refresh_stats(visibility)
    window.setCentralWidget(discernment_view)
    window.show()
    sys.exit(app.exec())
