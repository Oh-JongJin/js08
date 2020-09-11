import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class polar(QMainWindow):
    def run(self):
        pi = np.pi

        csv = pd.read_csv('target/PNM-9030V.csv', names=['target_name', 'target_x', 'target_y', 'distance', 'predict'])
        # csv = pd.read_csv('target/HANHWA Panoramic Camera.csv')

        angle = csv['target_x']
        angle_list = angle.values.tolist()
        angle_list.pop(0)

        dist = csv['distance']
        dist_list = dist.values.tolist()
        dist_list.pop(0)

        N = len(dist_list)
        # Fixing random state for reproducibility
        np.random.seed(19680801)

        # Compute areas and colors
        colors = 2 * pi * np.random.rand(N)

        fig = plt.figure("Hello")
        fig.set_facecolor('skyblue')
        self.ax = fig.add_subplot(111, projection='polar')
        self.ax.set_thetamin(-90)
        self.ax.set_thetamax(90)

        for i in range(N):
            angle_list[i] = float((float(angle_list[i]) * 1920) / 6096)
            angle_list[i] = round((float(angle_list[i]) * 180) / 1920, 3)
            # print(angle_list[i])
            self.ax.scatter((pi * angle_list[i] / 180) + (-pi / 2), float(dist_list[i]), s=20, cmap='hsv', alpha=0.75)
            plt.text((pi * angle_list[i] / 180) + (-pi / 2), float(dist_list[i]), str(i+1))

        self.ax.set_xticks([-pi / 2, -pi / 6, -pi / 3, 0, pi / 6, pi / 3, pi / 2])
        self.ax.set_theta_zero_location("N")
        self.ax.set_theta_direction(-1)

        rlab = plt.ylabel("(km)")
        rlab.set_position((2, 0.2))
        rlab.set_rotation(45)

        fig.set_tight_layout(True)

        # mng = plt.get_current_fig_manager()
        # mng.window.showMaximized()
        self.canvas = FigureCanvas(fig)
        self.canvas.draw_idle()
        self.lay = QHBoxLayout()
        self.setLayout(self.lay)
        self.lay.addWidget(self.canvas)

        self.cb = QComboBox()
        self.cb.addItem("Hi")
        self.lay.addWidget(self.cb)
        self.canvas.show()

    #     self.timer = QtCore.QTimer()
    #     self.timer.setInterval(10)
    #     self.timer.timeout.connect(self.update_plot)
    #     self.timer.start()
    #
    # def update_plot(self):
    #     self.ax.cla()
    #     # self.