#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import argparse
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from . import js06_rc
from .controller import Js06MainCtrl
from .model import Js06AttrModel
from .view import Js06MainView


def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--window-size', 
        action='store',
        help='--window-size=<width>,<height>'
    )

    parsed_args, unparsed_args = parser.parse_known_args()
    return parsed_args, unparsed_args
    
def main():
    """Main function"""
    parsed_args, unparsed_args = process_args()
    
    window_size = None
    if parsed_args.window_size is not None:
        width, height = parsed_args.window_size.split(',')
        window_size = (int(width), int(height))

    # Create an instance of `QApplication`
    app = QApplication(unparsed_args)
    # Create instances of the model
    model = Js06AttrModel()
    # Create instances of the controller
    ctrl = Js06MainCtrl(model)
    # Show GUI of JS-06
    view = Js06MainView(ctrl, size=window_size)
    # Set icon of the app
    app_icon = QIcon(':icon/logo.png')
    view.setWindowIcon(app_icon)
    # Execute calculator's main loop
    sys.exit(app.exec())

if __name__ == '__main__':
    do_profiling = False
    if do_profiling:
        import cProfile
        cProfile.run('main()', 'restats')
    else:
        main()
