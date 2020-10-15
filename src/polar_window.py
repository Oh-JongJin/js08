#!/usr/bin/env python3
# 
# References
#  1. https://subscription.packtpub.com/video/application_development/9781788471268/36149/36150/calling-dialogs-from-the-main-window
#  2. https://www.learnpyqt.com/courses/graphics-plotting/plotting-matplotlib/

import numpy as np
import pandas as pd

from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from target_plot_dialog import Ui_TargetPlot


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent: QtWidgets = None, width: int = 5, height: int = 4, dpi: int = 100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.set_tight_layout(True)
        self.axes = fig.add_subplot(111, projection='polar')
        super().__init__(fig)


class TargetPlotWindow(Ui_TargetPlot):
    def __init__(self):
        super().__init__()

        # angle and distance of targets
        self.angle = None
        self.distance = None

        # FigureCanvasQTAgg to plot the target
        self.canvas = None

        # a timer to trigger the redraw
        self.timer = None
        
        # Reference to the plotted targets
        self._plot_ref = None

    def setupUi(self, TargetPlot: QtWidgets.QDialog):
        super().setupUi(TargetPlot)

        pi = np.pi # pylint: disable=invalid-name,locally-disabled
        
        self.canvas = MplCanvas(TargetPlot, width=5, height=4, dpi=100)
        self.read_target()

        self.canvas.axes.set_facecolor('skyblue')
        self.canvas.axes.set_thetamin(-90)
        self.canvas.axes.set_thetamax(90)
        self.canvas.axes.set_xticks([-pi / 2, -pi / 6, -pi / 3, 0, pi / 6, pi / 3, pi / 2])
        self.canvas.axes.set_theta_zero_location("N")
        self.canvas.axes.set_theta_direction(-1)

        self.update_plot()
        
        # plot.show()
        # rlab = plot.axes.ylabel("(mi)")
        # rlab.set_position((2, 0.2))
        # rlab.set_rotation(45)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        TargetPlot.setLayout(layout)

        # self.canvas = FigureCanvasQTAgg(fig)
        # self.canvas.draw_idle()
        # self.lay = QtWidgets.QHBoxLayout()
        # self.setLayout(self.lay)
        # self.lay.addWidget(self.canvas)
        # self.show()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def read_target(self):
        pi = np.pi # pylint: disable=invalid-name,locally-disabled

        csv = pd.read_csv('target/PNM-9030V.csv',
                          header=0, dtype={'target_x': float, 'target_y': float})

        self.angle = csv.target_x.values
        self.angle[:] = self.angle[:] * 1920 / 6096
        self.angle[:] = self.angle[:] * 180 / 1920
        self.angle[:] = pi * self.angle[:] / 180 - pi / 2

        self.distance = csv.distance.values

    def update_plot(self):
        pi = np.pi # pylint: disable=invalid-name,locally-disabled

        self.read_target()

        if self._plot_ref is None:
            self.canvas.axes.scatter(self.angle, self.distance, s=20, cmap='hsv', alpha=0.75)
            for i, xy in enumerate(zip(self.angle, self.distance), start=1):
                self.canvas.axes.annotate(i, xy)
        else:
            self._plot_ref.set_xdata(self.angle)
            self._plot_ref.set_ydata(self.distance)
            for i, xy in enumerate(zip(self.angle, self.distance), start=1):
                self.canvas.axes.annotate(i, xy)

        self.canvas.draw()
