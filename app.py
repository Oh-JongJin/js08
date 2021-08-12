#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import sys

from PyQt5.QtGui import QIcon # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QApplication # pylint: disable=no-name-in-module

from js06.view import Js06MainView
from js06.model import Js06Model
from js06.controller import Js06MainCtrl
from js06 import js06_rc

def main():
    """Main function"""
    # Create an instance of `QApplication`
    app = QApplication(sys.argv)
    # Create instances of the model
    model = Js06Model()
    # Create instances of the controller
    ctrl = Js06MainCtrl(model)
    # Show GUI of JS-06
    view = Js06MainView(ctrl)
    view.show()
    # Set icon of the app
    app_icon = QIcon(":icon/logo.png")
    view.setWindowIcon(app_icon)
    # Execute calculator's main loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

# end of app.py
