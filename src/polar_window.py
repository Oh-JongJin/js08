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
    # def __init__(self):
    #     super().__init__()

    def setupUi(self, TargetPlot: QtWidgets.QDialog):
        super().setupUi(TargetPlot)

        pi = np.pi
        
        self.canvas = MplCanvas(TargetPlot, width=5, height=4, dpi=100)
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

    def update_plot(self):
        pi = np.pi

        csv = pd.read_csv('target/PNM-9030V.csv', names=['target_name', 'target_x', 'target_y', 'distance', 'predict'])

        angle = csv['target_x']
        angle_list = angle.values.tolist()
        angle_list.pop(0)

        dist = csv['distance']
        dist_list = dist.values.tolist()
        dist_list.pop(0)

        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.set_facecolor('skyblue')
        self.canvas.axes.set_thetamin(-90)
        self.canvas.axes.set_thetamax(90)
        for i in range(len(dist_list)):
            angle_list[i] = float((float(angle_list[i]) * 1920) / 6096)
            angle_list[i] = round((float(angle_list[i]) * 180) / 1920, 3)
            self.canvas.axes.scatter((pi * angle_list[i] / 180) + (-pi / 2), float(dist_list[i]), s=20, cmap='hsv', alpha=0.75)
            self.canvas.axes.text((pi * angle_list[i] / 180) + (-pi / 2), float(dist_list[i]), str(i+1))

        # Drop off the first y element, append a new one.
        self.canvas.axes.scatter((pi * angle_list[i] / 180) + (-pi / 2), float(dist_list[i]), s=20, cmap='hsv', alpha=0.75)
        self.canvas.axes.text((pi * angle_list[i] / 180) + (-pi / 2), float(dist_list[i]), str(i+1))

        self.canvas.axes.set_xticks([-pi / 2, -pi / 6, -pi / 3, 0, pi / 6, pi / 3, pi / 2])
        self.canvas.axes.set_theta_zero_location("N")
        self.canvas.axes.set_theta_direction(-1)
        
        # Trigger the canvas to update and redraw.
        self.canvas.draw()