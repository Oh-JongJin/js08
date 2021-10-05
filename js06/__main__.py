#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from .view import Js06MainView
from .model import Js06AttrModel
from .controller import Js06MainCtrl
from . import js06_rc

def main():
    """Main function"""
    # Create an instance of `QApplication`
    app = QApplication(sys.argv)
    # Create instances of the model
    model = Js06AttrModel()
    # Create instances of the controller
    ctrl = Js06MainCtrl(model)
    # Show GUI of JS-06
    view = Js06MainView(ctrl)
    # Set icon of the app
    app_icon = QIcon(":icon/logo.png")
    view.setWindowIcon(app_icon)
    # Execute calculator's main loop
    sys.exit(app.exec())
# end of main

if __name__ == "__main__":
    main()

# end of __main__.py
