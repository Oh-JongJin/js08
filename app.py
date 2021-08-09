#!/usr/bin/env python3
 
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QApplication, QMessageBox # pylint: disable=no-name-in-module

from views.main_view import Js06MainWindow
from model.settings import Js06Settings
from model.model import Js06Attribute

import js06_rc

class Js06(QApplication):
    abnormal_shutdown = pyqtSignal()

    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        self.model = Js06Attribute()
        self.main_ctrl = Js06MainCtrl()
        self.main_view = Js06MainWindow()
        self.abnormal_shutdown.connect(self.main_view.restore_default)

        shutdown_status = Js06Settings.get('normal_shutdown')
        if not shutdown_status:
            self.abnormal_shutdown.emit()

        app_icon = QIcon(":icon/logo.png")
        self.main_view.setWindowIcon(app_icon)

        self.main_view.show()
    # end of __init__

# end of Js06

if __name__ == '__main__':

    app = Js06(sys.argv)
    sys.exit(app.exec_())
    
# end of app.py
