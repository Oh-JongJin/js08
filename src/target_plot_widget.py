# !/usr/bin/env python3

from matplotlib.backends.qt_compat import QtCore, QtWidgets
if QtCore.qVersion() >= "5.":
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import QRectF, Qt, QUrl, pyqtSlot
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem, QVideoWidget

import numpy as np
import time

class TargetPlotWidget(QWidget):
    def __init__(self, parent=None):
        super(TargetPlotWidget, self).__init__(parent)
        layout = QVBoxLayout(self)

        canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(canvas)

        self._ax = canvas.figure.subplots()
        t = np.linspace(0, 10, 101)
        # Set up a Line2D.
        self._line, = self._ax.plot(t, np.sin(t + time.time()))
        self._timer = canvas.new_timer(50)
        self._timer.add_callback(self._update_canvas)
        self._timer.start()
    # end of __init__

    def _update_canvas(self):
        t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        self._line.set_data(t, np.sin(t + time.time()))
        self._line.figure.canvas.draw()
    # end of _update_canvas
# end of TargetPlotWidget

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = TargetPlotWidget()
    window.show()
    sys.exit(app.exec_())
# end of target_plot_widget.py