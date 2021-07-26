# !/usr/bin/env python3
#
# Copyright 2020-21 Sijung Co., Ltd.
# Authors:
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import QWidget, QVBoxLayout


class Js06TargetPlotWidget(QWidget):
    def __init__(self, parent=None):
        super(Js06TargetPlotWidget, self).__init__(parent)
        layout = QVBoxLayout(self)


        pi = np.pi
        self._plot_ref_red = None
        self._plot_ref_green = None
        self.annotate = None
        self.ylabel = None
        self.xlabel = None

        self.fig = plt.Figure(figsize=(5, 4), dpi=100, facecolor=(0.9686, 0.9725, 0.9803), tight_layout=False)
        self.fig.suptitle("Target Distribution")
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111, projection="polar")

        self.axes.set_thetamin(-90)
        self.axes.set_thetamax(90)
        self.axes.set_xticks([-pi / 2, -pi / 6, -pi / 3, 0, pi / 6, pi / 3, pi / 2])
        self.axes.set_theta_zero_location("N")
        self.axes.set_theta_direction(-1)
        self.ylabel = self.axes.set_ylabel("(km)", fontsize=7)
        self.ylabel.set_position((2, 0.2))
        self.ylabel.set_rotation(45)
        vis = int(np.random.randint(0, 10000, size=1))
        self.xlabel = self.axes.set_xlabel(f"Visibility: {vis} m", fontsize=20)
        plt.rcParams.update({'font.size': 7})

        layout.addWidget(self.canvas)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Js06TargetPlotWidget()
    window.resize(600, 600)
    window.show()

    sys.exit(app.exec_())
