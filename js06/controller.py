#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

from PyQt5.QtCore import QObject, QThreadPool, pyqtSignal, pyqtSlot
from PyQt5.QtMultimedia import QVideoFrame

from js06.model import Js06CameraTableModel, Js06Model, Js06Settings

class Js06MainCtrl(QObject):
    abnormal_shutdown = pyqtSignal()
    current_camera_changed = pyqtSignal(str)

    def __init__(self, model: Js06Model):
        super().__init__()

        self.thread_pool = QThreadPool.globalInstance()

        self._model = model

        self.video_frame = None

        self.init()
    # end of __init__

    def init(self):
        db_host = Js06Settings.get('db_host')
        db_port = Js06Settings.get('db_port')
        db_name = Js06Settings.get('db_name')
        self._model.connect_to_db(db_host, db_port, db_name)

        self._attr = self._model.read_attr()
    # end of init

    def update_video_frame(self, video_frame: QVideoFrame):
        self.video_frame = video_frame
    # end of update_video_frame

    def get_current_camera_uris(self):
        return self._attr['camera']['uri']
    # end of get_current_camera_ruis

    def get_camera_models(self):
        return self._attr['camera']['model']
    # end of get_camera_models

    def get_target(self):
        return self._attr['camera']['targets']
    # end of get_target

    def get_camera_table_model(self):
        cameras = self.get_cameras()
        table_model =  Js06CameraTableModel(cameras)
        return table_model
    # end of get_camera_table_model

    def check_exit_status(self):
        normal_exit = Js06Settings.get('normal_shutdown')
        Js06Settings.set('normal_shutdown', False)
        return normal_exit
    # end of check_exit_stauts

    def update_cameras(self, cameras: list):
        # Remove deleted cameras
        cam_id_in_db = [cam["_id"] for cam in self._model.read_cameras()]
        cam_id_in_arg = [cam["_id"] for cam in cameras]
        for cam_id in cam_id_in_db:
            if cam_id not in cam_id_in_arg:
                self._model.delete_camera(cam_id)

        # Update existing camera or Insert new cameras
        for cam in cameras:
            self._model.update_camera(cam, upsert=True)
    # end of update_cameras

    @pyqtSlot()
    def close_process(self):
        Js06Settings.set('normal_shutdown', True)
    # end of close_process

    def get_attr(self, model: dict):
        if self.attr.count_documents({}):
            attr_doc = list(self.attr.find().sort("_id", -1).limit(1))[0]
        else:
            attr_doc = model
        return attr_doc
    # end of get_attr
    
    def set_attr(self, model: dict):
        self._model.update_attr(model)
    # end of set_attr

    @pyqtSlot()
    def restore_defaults(self):
        Js06Settings.restore_defaults()
    # end of restore_defaults

    @pyqtSlot(bool)
    def set_normal_shutdown(self):
         Js06Settings.set('normal_shutdown', True)
    # end of set_normal_shutdown

    def get_cameras(self):
        return self._model.read_cameras()
    # end of get_camearas

# end of Js06MainCtrl

# if __name__ == '__main__':
#     ctrl = Js06MainCtrl(model=Js06Model, view=Js06MainView)
#     print(ctrl.get_attr)

# end of main_ctrl.py
