#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

from matplotlib.backends.qt_compat import QtCore, QtWidgets

if QtCore.qVersion() >= "5.":
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from PyQt5.QtWidgets import QWidget, QVBoxLayout

import numpy as np
import time

class Js06TargetPlotWidget(QWidget):
    """Plot using MatPlotlib
    """
    def __init__(self, parent=None):
        super(Js06TargetPlotWidget, self).__init__(parent)
        layout = QVBoxLayout(self)

        canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(canvas)

        self._ax = canvas.figure.subplots()
        t = np.linspace(0, 10, 101)
        # Set up a Line2D.
        self._line, = self._ax.plot(t, np.sin(t + time.time()))
        self._timer = canvas.new_timer(0.1)
        self._timer.add_callback(self._update_canvas)
        self._timer.start()
    # end of __init__

    def _update_canvas(self):
        t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        self._line.set_data(t, np.sin(t + time.time() * 3))
        self._line.figure.canvas.draw()
    # end of _update_canvas
# end of TargetPlotWidget

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Js06TargetPlotWidget()
    window.show()
    sys.exit(app.exec_())

# end of target_plot_widget.py
