#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

from pymongo import MongoClient

from PyQt5.QtCore import QThreadPool, pyqtSlot # pylint: disable=no-name-in-module

from controllers.settings import Js06Settings
from ..model.model import Js06Model
from ..views.main_view import Js06MainView

class Js06MainCtrl:
    def __init__(self, model:Js06Model, view:Js06MainView):
        self.pool = QThreadPool.globalInstance()

        db_host = Js06Settings.get('db_host')
        db_port = Js06Settings.get('db_port')
        client = MongoClient(db_host, db_port)
        db = client.js06
        self.attr = db.attr

        self._model = model
        self._view = view

        self._view.restore_defaults_requested.connet(self.restore_defaults)
        
    # end of __init__

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

    @pyqtSlot(bool)
    def restore_defaults(self):
        Js06Settings.restore_defaults()

    @pyqtSlot(bool)
    def set_normal_shutdown(self, status:bool):
         Js06Settings.set('normal_shutdown', status)

# end of Js06MainCtrl

# if __name__ == '__main__':
#     ctrl = Js06MainCtrl()
#     print(ctrl.get_attr)

# end of main_ctrl.py
 