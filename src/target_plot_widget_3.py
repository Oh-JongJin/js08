#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#

import time

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPalette

import pyqtgraph as pg
import numpy as np

class Js06TargetPlotWidget3(QWidget):
    """Plot using PyQtGraph
    """
    def __init__(self, parent=None):
        super(Js06TargetPlotWidget3, self).__init__(parent)
        layout = QVBoxLayout(self)

        self.graphWidget = pg.PlotWidget()
        layout.addWidget(self.graphWidget)

        self._t = np.linspace(0, 10, 101)
        self._y = np.sin(self._t + time.time())
        
        color = self.palette().color(QPalette.Window)
        self.graphWidget.setBackground(color)

        self.plot(self._t, self._y, 'Sensor 1', 'b')
        
        # self.graphWidget.addLegend()
        # self.graphWidget.showGrid(x=True, y=True)
        # self.graphWidget.setYRange(0, 100)

        # self.graphWidget.setTitle('Your Title Here', color='b', size='30pt')
        
        # styles = {'color':'r', 'font-size': '30pt'}
        # self.graphWidget.setLabel('left', 'Temperature (°C)', **styles)
        # self.graphWidget.setLabel('bottom', 'Hour (H)', **styles)

        self.timer = QTimer()
        self.timer.setInterval(0.1)
        self.timer.timeout.connect(self._update_plot_data)
        self.timer.start()
    # end of __init__

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color, width=2)
        self._line = self.graphWidget.plot(x, y, name=plotname, pen=pen)
    # end of plot

    def _update_plot_data(self):
        self._y = np.sin(self._t + time.time() * 3)
        self._line.setData(self._t, self._y)
    # end of _update_plot_data

# end of Js06TargetPlotWidget3

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = Js06TargetPlotWidget3()
    window.show()
    sys.exit(app.exec_())

# end of target_plot_widget_3.py
