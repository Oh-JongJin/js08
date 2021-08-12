#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

from pymongo import MongoClient

from PyQt5.QtCore import QObject, QThreadPool, pyqtSignal, pyqtSlot # pylint: disable=no-name-in-module

from js06.model import Js06CameraTableModel, Js06Model, Js06Settings

class Js06MainCtrl(QObject):
    abnormal_shutdown = pyqtSignal()
    current_camera_changed = pyqtSignal(str)

    def __init__(self, model:Js06Model):
        super().__init__()

        self.thread_pool = QThreadPool.globalInstance()

        self._model = model

        self.init()
    # end of __init__

    def init(self):
        db_host = Js06Settings.get('db_host')
        db_port = Js06Settings.get('db_port')
        db_name = Js06Settings.get('db_name')
        self._model.connect_to_db(db_host, db_port, db_name)

        self._attr = self._model.read_attr()
    # end of init

    def get_current_camera_uri(self):
        return self._attr['camera']['uri']
    # end of get_current_camera_rui

    def get_camera_table_model(self):
        cameras = self.get_cameras()
        table_model =  Js06CameraTableModel(cameras)
        return table_model
    # end of get_camera_table_model

    # def select_camera(self):
    #     cameras = self._model.read_cameras()

    # end of select_camera
    #     
    def check_exit_status(self):
        normal_exit = Js06Settings.get('normal_shutdown')
        Js06Settings.set('normal_shutdown', False)
        return normal_exit
    # end of check_exit_stauts

    def update_cameras(self, cameras:list):
        for cam in cameras:
            self._model.update_camera(cam, upsert=True)
    # end of update_cameras

    @pyqtSlot()
    def close_process(self):
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

    # @pyqtSlot(int)
    # def set_current_camera(self, num:int):
    #     Js06Settings.set('camera', num)
    # # end of set_curent_camera

    @pyqtSlot()
    def restore_defaults(self):
        Js06Settings.restore_defaults()

    @pyqtSlot(bool)
    def set_normal_shutdown(self):
         Js06Settings.set('normal_shutdown', True)

    def get_cameras(self):
        return self._model.read_cameras()
# end of Js06MainCtrl


# if __name__ == '__main__':
#     ctrl = Js06MainCtrl(model=Js06Model, view=Js06MainView)
#     print(ctrl.get_attr)

# end of main_ctrl.py
