#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import os
from PyQt5.QtCore import QDate, QDateTime, QDir, QObject, QRect, QThreadPool, QTime, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage
from PyQt5.QtMultimedia import QVideoFrame

from js06.model import Js06CameraTableModel, Js06InferenceRunner, Js06IoRunner, Js06Model, Js06Settings

class Js06MainCtrl(QObject):
    abnormal_shutdown = pyqtSignal()
    current_camera_changed = pyqtSignal(str)

    def __init__(self, model: Js06Model):
        super().__init__()

        self.inference_pool = QThreadPool.globalInstance()
        self.set_max_inference_thread()

        self.io_pool = QThreadPool.globalInstance()
        self.io_pool.setMaxThreadCount(1)

        self._model = model

        self.video_frame = None

        self.init()

        self.timer = QTimer()
        self.current_camera_changed.connect(self.start_timer)
    # end of __init__

    def set_max_inference_thread(self):
        threads = Js06Settings.get('thread_count')
        self.inference_pool.setMaxThreadCount(threads)
    # end of set_max_inference_thread

    def init(self):
        db_host = Js06Settings.get('db_host')
        db_port = Js06Settings.get('db_port')
        db_name = Js06Settings.get('db_name')
        self._model.connect_to_db(db_host, db_port, db_name)

        self._attr = self._model.read_attr()
    # end of init

    @pyqtSlot(str)
    def start_timer(self, _:str) -> None:
        print('DEBUG:', QTime.currentTime().toString())
        observation_period = Js06Settings.get('observation_period')
        self.timer.setInterval(observation_period * 60 * 1000)
        self.timer.timeout.connect(self.job_broker)

        # Start repeating timer on time        
        now = QTime.currentTime()
        minute_left = observation_period - (now.minute() % observation_period) - 1
        second_left = 60 - now.second()
        timeout_in_sec = minute_left * 60 + second_left
        QTimer.singleShot(timeout_in_sec * 1000, self.timer.start)
    # end of start_timer

    def stop_timer(self) -> None:
        self.timer.stop()
    # end of stop_timer

    def job_broker(self) -> None:
        # print('DEBUG: Inside of job_broker')
        if self.video_frame == None:
            return
        
        epoch = QDateTime.currentSecsSinceEpoch()
        # print('DEBUG:', now.toString())
        image = self.get_image()
            
        if Js06Settings.get('save_vista'):
            basepath = Js06Settings.get('image_base_path')
            print(f'DEBUG: {basepath}')
            now = QDateTime.fromSecsSinceEpoch(epoch)
            dir = os.path.join(basepath, 'vista', now.toString("yyyy-MM-dd"))
            filename = f'vista-{now.toString("yyyy-MM-dd-hh-mm")}.png'
            self.save_image(dir, filename, image)

        targets = self.get_target()
        # print('DEBUG:', type(targets))
        for i, tg in enumerate(targets):
            id = i # key
            point = tg['roi']['point']
            size = tg['roi']['size']
            rect = QRect(*point, *size)
            patch = image.copy(rect) # key
            inf_runner = Js06InferenceRunner(self._model, epoch, id, patch)
            self.inference_pool.start(inf_runner)
    # end of job_broker

    def save_image(self, dir: str, filename: str, image: QImage):
        os.makedirs(dir, exist_ok=True)
        path = QDir.cleanPath(os.path.join(dir, filename))
        runner = Js06IoRunner(path, image)
        self.io_pool.start(runner)
    # end of save_image

    def get_image(self) -> QImage:
        if self.video_frame == None:
            return None
        image = self.video_frame.image().mirrored(False, True)
        return image

    def update_video_frame(self, video_frame: QVideoFrame):
        self.video_frame = video_frame
    # end of update_video_frame

    def get_current_camera_uri(self):
        return self._attr['camera']['uri']
    # end of get_current_camera_rui

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

    def get_attr(self):
        self._model.get_attr()
        attr_doc = None
        if self._attr.count_documents({}):
            attr_doc = list(self._attr.find().sort("_id", -1).limit(1))[0]
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
