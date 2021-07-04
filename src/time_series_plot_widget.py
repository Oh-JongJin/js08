# !/usr/bin/env python3

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView

SRC = "https://grafana.com/static/img/docs/v41/test_data_csv_example.png"

class TimeSeriesPlotWidget(QWidget):
    def __init__(self, parent=None):
        super(TimeSeriesPlotWidget, self).__init__(parent)
        
        self.view = QWebEngineView()
        self.view.load(QUrl(SRC))
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
    # end of __init__
# end of TimeSeriesPlotWidget

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = TimeSeriesPlotWidget()
    window.show()
    sys.exit(app.exec_())
# end of time_series_plot_widget.py