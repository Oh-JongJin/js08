#!/usr/bin/env python3
# A implementation of the target visualization graph for JS-06.
#
# This example illustrates the following techniques:
# * Open and access a CSV file


import os
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, QtGui, QtWidgets


class polar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.lay = QtWidgets.QHBoxLayout()
        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)

        self.setWindowTitle("Visibility")
        self.run()

    def run(self):
        pi = np.pi
        csv = pd.read_csv('target/PNM-9030V.csv', names=['target_name', 'target_x', 'target_y', 'distance', 'predict'])

        # Call up 'target_x' from the csv file.
        angle = csv['target_x']
        angle_list = angle.values.tolist()
        angle_list.pop(0)

        dist = csv['distance']
        dist_list = dist.values.tolist()
        dist_list.pop(0)

        ox = csv['predict']
        ox_list = ox.values.tolist()
        ox_list.pop(0)

        N = len(dist_list)
        self.fig = plt.figure()
        self.fig.set_facecolor('skyblue')
        self.ax = self.fig.add_subplot(111, projection='polar')
        self.ax.set_thetamin(-90)
        self.ax.set_thetamax(90)

        for i in range(N):
            angle_list[i] = float((float(angle_list[i]) * 1920) / 6096)
            angle_list[i] = round((float(angle_list[i]) * 180) / 1920, 3)

            if ox_list[i] == '0':
                self.ax.scatter((pi * angle_list[i] / 180) + (-pi / 2), float(dist_list[i])
                                , s=20, c='red', cmap='hsv', alpha=0.75)
            else:
                self.ax.scatter((pi * angle_list[i] / 180) + (-pi / 2), float(dist_list[i])
                                , s=20, c='limegreen', cmap='hsv', alpha=0.75)
            plt.text((pi * angle_list[i] / 180) + (-pi / 2), float(dist_list[i]), str(i + 1))

        self.ax.set_xticks([-pi / 2, -pi / 6, -pi / 3, 0, pi / 6, pi / 3, pi / 2])
        self.ax.set_theta_zero_location("N")
        self.ax.set_theta_direction(-1)

        rlab = plt.ylabel("(mi)")
        rlab.set_position((2, 0.2))
        rlab.set_rotation(45)

        self.fig.set_tight_layout(True)
        self.canvas = FigureCanvas(self.fig)
        self.lay.addWidget(self.canvas)
        self.setLayout(self.lay)
        self.canvas.show()

    # Press 'F5' key, refresh Polar Plot Window.
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_F5:
            plt.close()
            self.lay.removeWidget(self.canvas)
            self.run()
