#!/usr/bin/env python3
# 
# References
#  1. https://subscription.packtpub.com/video/application_development/9781788471268/36149/36150/calling-dialogs-from-the-main-window
#  2. https://www.learnpyqt.com/courses/graphics-plotting/plotting-matplotlib/

import time
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from target_plot_dialog import Ui_TargetPlot

global distance_label
distance_label = "(km)"


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent: QtWidgets = None, width: int = 5, height: int = 4, dpi: int = 100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.set_tight_layout(True)
        fig.set_facecolor("skyblue")
        self.axes = fig.add_subplot(111, projection='polar')
        super().__init__(fig)


class TargetPlotWindow(Ui_TargetPlot):
    def __init__(self):
        super().__init__()

        # angle and distance of targets
        self.angle = None
        self.distance = None
        self.predict = None

        # FigureCanvasQTAgg to plot the target
        self.canvas = None

        # a timer to trigger the redraw
        self.timer = None
        
        # Reference to the plotted targets
        self._plot_ref = None

        self.ylabel = None
        self.ann = None

    def setupUi(self, TargetPlot: QtWidgets.QDialog, timer):
        super().setupUi(TargetPlot, 800, 600)

        pi = np.pi  # pylint: disable=invalid-name,locally-disabled
        
        self.canvas = MplCanvas(TargetPlot, width=5, height=4, dpi=100)
        self.read_target()

        self.canvas.axes.set_thetamin(-90)
        self.canvas.axes.set_thetamax(90)
        self.canvas.axes.set_xticks([-pi / 2, -pi / 6, -pi / 3, 0, pi / 6, pi / 3, pi / 2])
        self.canvas.axes.set_theta_zero_location("N")
        self.canvas.axes.set_theta_direction(-1)

        self.update_plot()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        TargetPlot.setLayout(layout)

        # Thread timer.
        # Run update_plot every 'timer: int'
        self.timer = QtCore.QTimer()
        self.timer.setInterval(timer)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def read_target(self):
        pi = np.pi  # pylint: disable=invalid-name,locally-disabled
        csv = pd.read_csv('target/PNM-9030V.csv',
                          header=0, dtype={'target_x': float, 'target_y': float, 'predict': int})

        self.angle = csv.target_x.values
        self.angle[:] = self.angle[:] * 1920 / 6096
        self.angle[:] = self.angle[:] * 180 / 1920
        self.angle[:] = pi * self.angle[:] / 180 - pi / 2

        self.distance = csv.distance.values
        self.predict = csv.predict.values

    def update_plot(self):
        # TODO(Jongjin): Come up other ways other than 'self.canvas.axes.clear()'
        pi = np.pi  # pylint: disable=invalid-name,locally-disabled

        start = time.time()

        # self.canvas.axes.clear()
        # self.canvas.axes.set_thetamin(-90)
        # self.canvas.axes.set_thetamax(90)
        # self.canvas.axes.set_xticks([-pi / 2, -pi / 6, -pi / 3, 0, pi / 6, pi / 3, pi / 2])
        # self.canvas.axes.set_theta_zero_location("N")
        # self.canvas.axes.set_theta_direction(-1)
        # self.ylabel = self.canvas.axes.set_ylabel(f"{distance_label}")
        # self.ylabel.set_position((2, 0.2))
        # self.ylabel.set_rotation(45)

        self.read_target()

        if distance_label == "(mi)":
            self.distance = 0.621371 * self.distance

        #TODO(Jongjin): the color change according to result of 'predict' in csv file.
        # Don't overlay 'annotate'
        if self._plot_ref is None:
            # self.canvas.axes.scatter(self.angle, self.distance, s=20, cmap='hsv', alpha=0.75)

            # for i in range(len(self.predict)):
            #     if self.predict[i] == 0:
            #         self._plot_ref, = self.canvas.axes.plot(self.angle[i], self.distance[i], 'ro')
            #     else:
            #         self._plot_ref, = self.canvas.axes.plot(self.angle[i], self.distance[i], 'go')

            self._plot_ref, = self.canvas.axes.plot(self.angle, self.distance, 'go')

            for i, xy in enumerate(zip(self.angle, self.distance), start=1):
                self.canvas.axes.annotate(i, xy)
        else:
            self._plot_ref.set_xdata(self.angle)
            self._plot_ref.set_ydata(self.distance)

            # for i, xy in enumerate(zip(self.angle, self.distance), start=1):
            #     self.ann = self.canvas.axes.annotate(i, xy)
            # self.ann.remove()

            # print(time.time()-start)

            # for i, xy in enumerate(zip(self.angle, self.distance), start=1):
            #     self.canvas.axes.annotate(i, xy, arrowprops=dict(facecolor='black', shrink=0.05),
            #                               xytext=(0.05, 0.05), textcoords='figure fraction',
            #                               horizontalalignment='left', verticalalignment='bottom')

        self.canvas.draw()
