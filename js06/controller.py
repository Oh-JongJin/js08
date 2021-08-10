#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

from pymongo import MongoClient

from PyQt5.QtCore import QObject, QThreadPool, pyqtSignal, pyqtSlot # pylint: disable=no-name-in-module

import sys
sys.path.append("E:/Workspace/xavier-nx/")
from js06.model import Js06Model, Js06Settings
from js06.view import Js06MainView

class Js06MainCtrl(QObject):
    abnormal_shutdown = pyqtSignal()

    def __init__(self, model:Js06Model, view:Js06MainView):
        super().__init__()

        self.thread_pool = QThreadPool.globalInstance()

        self._model = model
        self._view = view

        # Connect signals and slots
        self._view.restore_defaults_requested.connect(self.restore_defaults)
        self.abnormal_shutdown.connect(self._view.ask_restore_default)

        self._view.main_view_closed.connect(self.close_process)

        self.init()
    # end of __init__

    def init(self):
        self.check_exit_status()

        db_host = Js06Settings.get('db_host')
        db_port = Js06Settings.get('db_port')
        db_name = Js06Settings.get('db_name')
        self._model.connect_to_db(db_host, db_port, db_name)

        attr = self._model.read_attr()
        print(attr.to_dict())
    # end of init
    
    def check_exit_status(self):
        normal_exit = Js06Settings.get('normal_shutdown')
        if not normal_exit:
            self.abnormal_shutdown.emit()
        Js06Settings.set('normal_shutdown', False)
    # end of check_exit_stauts

    @pyqtSlot()
    def close_process(self):
        print("DEBUG: inside close_process method")
        Js06Settings.set('normal_shutdown', True)
    # end of close_process

    def get_attr(self, model):
        if self.attr.count_documents({}):
            attr_doc = list(self.attr.find().sort("_id", -1).limit(1))[0]
        else:
            attr_doc = model.to_dict()
        return attr_doc
    # end of get_attr
    
    def set_attr(self, model):
        self.attr.insert_one(model.to_dict())
    # end of set_attr

    @pyqtSlot(int)
    def set_current_camera(self, num:int):
        Js06Settings.set('camera', num)
    # end of set_curent_camera

    @pyqtSlot()
    def restore_defaults(self):
        print("DEBUG: inside restore_defaults")
        Js06Settings.restore_defaults()

    # @pyqtSlot(bool)
    # def set_normal_shutdown(self):
    #      Js06Settings.set('normal_shutdown', True)

# end of Js06MainCtrl


if __name__ == '__main__':
    ctrl = Js06MainCtrl(model=Js06Model, view=Js06MainView)
    print(ctrl.get_attr)

# end of main_ctrl.py
