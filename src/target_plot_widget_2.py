#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

from PyQt5.QtWidgets import QWidget, QVBoxLayout

import numpy as np
import time

from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import GLViewWidget, GLGridItem, GLLinePlotItem
import pyqtgraph as pg
import sys

class Js06TargetPlotWidget2(QWidget):
    def __init__(self, parent=None):
        super(Js06TargetPlotWidget2, self).__init__(parent)
        layout = QVBoxLayout(self)

        canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # layout.addWidget(canvas)

        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.w = GLViewWidget()
        self.w.opts['distance'] = 40
        self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        self.w.setGeometry(0, 110, 300, 300)

        # create the background grids
        gx = GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.w.addItem(gx)
        gy = GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.w.addItem(gy)
        gz = GLGridItem()
        gz.translate(0, 0, -10)
        self.w.addItem(gz)

        self.n = 50
        self.m = 1000
        self.y = np.linspace(-10, 10, self.n)
        self.x = np.linspace(-10, 10, self.m)
        self.phase = 0

        for i in range(self.n):
            yi = np.array([self.y[i]] * self.m)
            d = np.sqrt(self.x ** 2 + yi ** 2)
            z = 10 * np.cos(d + self.phase) / (d + 1)
            pts = np.vstack([self.x, yi, z]).transpose()
            self.traces[i] = GLLinePlotItem(pos=pts, color=pg.glColor(
                (i, self.n * 1.3)), width=(i + 1) / 10, antialias=True)
            self.w.addItem(self.traces[i])

        layout.addWidget(self.w)
    # end of __init__

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
    # end of start

    def set_plotdata(self, name, points, color, width):
        self.traces[name].setData(pos=points, color=color, width=width)
    # end of set_plotdata

    def update(self):
        for i in range(self.n):
            yi = np.array([self.y[i]] * self.m)
            d = np.sqrt(self.x ** 2 + yi ** 2)
            z = 10 * np.cos(d + self.phase) / (d + 1)
            pts = np.vstack([self.x, yi, z]).transpose()
            self.set_plotdata(
                name=i, points=pts,
                color=pg.glColor((i, self.n * 1.3)),
                width=(i + 1) / 10
            )
            self.phase -= .003
    # end of update

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()
    # end of animation

# end of TargetPlotWidget

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Js06TargetPlotWidget2()
    window.resize(600, 600)
    window.show()
    # window.animation()

    sys.exit(app.exec_())

# end of target_plot_widget_2.py
