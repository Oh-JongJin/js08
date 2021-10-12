#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import json
import os
import sys

from PyQt5.QtCore import (QDateTime, QDir, QObject, QRect, QThread, QThreadPool, QTime,
                          QTimer, pyqtSignal, pyqtSlot)
from PyQt5.QtGui import QImage
from PyQt5.QtMultimedia import QVideoFrame

from .model import (Js06AttrModel, Js06CameraTableModel, Js06IoRunner,
                    Js06Settings, Js06Wedge, SimpleTarget)


class Js06MainCtrl(QObject):
    abnormal_shutdown = pyqtSignal()
    front_camera_changed = pyqtSignal(str) # uri
    rear_camera_changed = pyqtSignal(str) # uri
    front_target_decomposed = pyqtSignal()
    rear_target_decomposed = pyqtSignal()
    target_discerned = pyqtSignal(list, list) # positives, negatives
    prevailing_visibility_prepared = pyqtSignal(int, float) # epoch, prevailing visibility

    def __init__(self, model: Js06AttrModel):
        super().__init__()

        self.video_thread = QThread()
        self.plot_thread = QThread()

        self.inference_pool = QThreadPool.globalInstance()
        self.set_max_inference_thread()

        self.writer_pool = QThreadPool.globalInstance()
        self.writer_pool.setMaxThreadCount(1)

        self._model = model

        self.front_video_frame = None
        self.rear_video_frame = None
        self.num_working_cam = 0

        self.front_decomposed_targets = []
        self.rear_decomposed_targets = []

        self.init_db()

        self.observation_timer = QTimer()
        self.front_camera_changed.connect(self.decompose_front_targets)
        self.rear_camera_changed.connect(self.decompose_rear_targets)
        self.front_target_decomposed.connect(self.start_observation_timer)
        self.rear_target_decomposed.connect(self.start_observation_timer)
    
    def set_max_inference_thread(self):
        threads = Js06Settings.get('thread_count')
        self.inference_pool.setMaxThreadCount(threads)

    def init_db(self):
        db_host = Js06Settings.get('db_host')
        db_port = Js06Settings.get('db_port')
        db_name = Js06Settings.get('db_name')
        self._model.connect_to_db(db_host, db_port, db_name)

        if getattr(sys, 'frozen', False):
            directory = sys._MEIPASS
        else:
            directory = os.path.dirname(__file__)
        attr_path = os.path.join(directory, 'resources', 'attr.json')
        with open(attr_path, 'r') as f:
            attr_json = json.load(f)
        camera_path = os.path.join(directory, 'resources', 'camera.json')
        with open(camera_path, 'r') as f:
            camera_json = json.load(f)

        self._model.setup_db(attr_json, camera_json)

    @pyqtSlot(str)
    def decompose_front_targets(self, _:str) -> None:
        """Make list of SimpleTarget by decoposing compound targets.

        Parameters:
            epoch: timestamp when the vista taken
            vista: vista image
        """
        # Discard existing targets
        self.front_decomposed_targets = []
        attr = self._model.read_attr()
        targets = attr['front_camera']['targets']
        for tg in targets:
            wedge = tg['wedge']
            azimuth = tg['azimuth']
            point = tg['roi']['point']
            size = tg['roi']['size']
            roi = QRect(*point, *size)

            if tg['category'] == 'simple':
                label = tg['label']
                distance = tg['distance']
                mask = None # read mask from disk
                st = SimpleTarget(label, wedge, azimuth, distance, roi, mask)
                self.front_decomposed_targets.append(st)
                # continue
            
            elif tg['category'] == 'compound':
                for i in range(len(tg['mask'])):
                    label = f"{tg['label']}_{i}"
                    distance = tg['distance'][i]
                    mask = None # read mask from disk
                    st = SimpleTarget(label, wedge, azimuth, distance, roi, mask)
                    self.front_decomposed_targets.append(st)

        self.front_target_decomposed.emit()

    @pyqtSlot(str)
    def decompose_rear_targets(self, _:str) -> None:
        """Make list of SimpleTarget by decoposing compound targets.

        Parameters:
            epoch: timestamp when the vista taken
            vista: vista image
        """
        # Discard existing targets
        self.rear_decomposed_targets = []
        attr = self._model.read_attr()
        targets = attr['rear_camera']['targets']
        for tg in targets:
            wedge = tg['wedge']
            azimuth = tg['azimuth']
            point = tg['roi']['point']
            size = tg['roi']['size']
            roi = QRect(*point, *size)

            if tg['category'] == 'simple':
                label = tg['label']
                distance = tg['distance']
                mask = None # read mask from disk
                st = SimpleTarget(label, wedge, azimuth, distance, roi, mask)
                self.rear_decomposed_targets.append(st)
                # continue
            
            elif tg['category'] == 'compound':
                for i in range(len(tg['mask'])):
                    label = f"{tg['label']}_{i}"
                    distance = tg['distance'][i]
                    mask = None # read mask from disk
                    st = SimpleTarget(label, wedge, azimuth, distance, roi, mask)
                    self.rear_decomposed_targets.append(st)

        self.rear_target_decomposed.emit()

    # def prevailing_visibility(self) -> float:
    #     vis = list(self.directional_visibility.values())
    #     if None in vis:
    #         return None
    #     vis.sort(reverse=True)
    #     prevailing = vis[(len(vis) - 1) // 2]
    #     return prevailing

    @pyqtSlot()
    def start_observation_timer(self) -> None:
        # Start timer only when both cameras are ready.
        if self.num_working_cam < 1:
            self.num_working_cam += 1
            return
        else:
            self.num_working_cam = 0

        print('DEBUG(start_observation_timer):', QTime.currentTime().toString())
        observation_period = Js06Settings.get('observation_period')
        self.observation_timer.setInterval(observation_period * 1000) #* 60 * 1000)
        self.observation_timer.timeout.connect(self.job_broker)

        # # Start repeating timer on time        
        # now = QTime.currentTime()
        # minute_left = observation_period - (now.minute() % observation_period) - 1
        # second_left = 60 - now.second()
        # timeout_in_sec = minute_left * 60 + second_left
        # QTimer.singleShot(timeout_in_sec * 1000, self.observation_timer.start)
        self.observation_timer.start()

    def stop_timer(self) -> None:
        self.observation_timer.stop()

    def job_broker(self) -> None:
        print(f'DEBUG(job_broker): {self.front_video_frame}, {self.rear_video_frame}')
        if self.front_video_frame == None or self.rear_video_frame == None:
            return
        
        print('DEBUG(job_broker): after frame null check')
        epoch = QDateTime.currentSecsSinceEpoch()
        front_image = self.get_front_image()
        rear_image = self.get_rear_image()

        if Js06Settings.get('save_vista'):
            basepath = Js06Settings.get('image_base_path')
            now = QDateTime.fromSecsSinceEpoch(epoch)
            dir = os.path.join(basepath, 'vista', now.toString("yyyy-MM-dd"))
            filename = f'vista-front-{now.toString("yyyy-MM-dd-hh-mm")}.png'
            self.save_image(dir, filename, front_image)
            filename = f'vista-rear-{now.toString("yyyy-MM-dd-hh-mm")}.png'
            self.save_image(dir, filename, rear_image)

        for stg in self.front_decomposed_targets:
            stg.clip_roi(epoch, front_image)
            self.inference_pool.start(stg)

        for stg in self.rear_decomposed_targets:
            stg.clip_roi(epoch, rear_image)
            self.inference_pool.start(stg)

        self.inference_pool.waitForDone()
        
        pos, neg = self.assort_discernment()
        self.target_discerned.emit(pos, neg)

        wedge_visibility = self.wedge_visibility()
        self.write_visibilitiy(epoch, wedge_visibility)

    def assort_discernment(self) -> tuple:
        pos, neg = [], []

        for t in self.front_decomposed_targets:
            point = (t.azimuth, t.distance)
            if t.discernment:
                pos.append(point)
            else:
                neg.append(point)

        for t in self.rear_decomposed_targets:
            point = (t.azimuth, t.distance)
            if t.discernment:
                pos.append(point)
            else:
                neg.append(point)

        return pos, neg

    def write_visibilitiy(self, epoch: int, wedge_visibility: dict) -> None:
        vis_list = list(wedge_visibility.values())
        prevailing = self.prevailing_visibility(vis_list)
        if prevailing is None:
            self.prevailing_visibility_prepared.emit(epoch, 0)
        else:
            self.prevailing_visibility_prepared.emit(epoch, prevailing)
        wedge_visibility['epoch'] = epoch
        wedge_visibility['prevailing'] = prevailing
        print('DEBUG:', wedge_visibility)
        self._model.write_visibility(wedge_visibility)

    def wedge_visibility(self) -> dict:
        wedge_vis = {w: None for w in Js06Wedge}
        for t in self.front_decomposed_targets:
            if t.discernment:
                if wedge_vis[t.wedge] == None:
                    wedge_vis[t.wedge] = t.distance
                elif wedge_vis[t.wedge] < t.distance:
                    wedge_vis[t.wedge] = t.distance
        for t in self.rear_decomposed_targets:
            if t.discernment:
                if wedge_vis[t.wedge] == None:
                    wedge_vis[t.wedge] = t.distance
                elif wedge_vis[t.wedge] < t.distance:
                    wedge_vis[t.wedge] = t.distance
        return wedge_vis

    def prevailing_visibility(self, wedge_vis: list) -> float:
        if None in wedge_vis:
            return None
        sorted_vis = sorted(wedge_vis, reverse=True)
        prevailing = sorted_vis[(len(sorted_vis) - 1) // 2]
        return prevailing

    def save_image(self, dir: str, filename: str, image: QImage) -> None:
        os.makedirs(dir, exist_ok=True)
        path = QDir.cleanPath(os.path.join(dir, filename))
        runner = Js06IoRunner(path, image)
        self.writer_pool.start(runner)

    def get_front_image(self) -> QImage:
        if self.front_video_frame == None:
            return None
        image = self.front_video_frame.image().mirrored(False, True)
        return image

    def get_rear_image(self) -> QImage:
        if self.rear_video_frame == None:
            return None
        image = self.rear_video_frame.image().mirrored(False, True)
        return image

    @pyqtSlot(QVideoFrame)
    def update_front_video_frame(self, video_frame: QVideoFrame) -> None:
        self.front_video_frame = video_frame

    @pyqtSlot(QVideoFrame)
    def update_rear_video_frame(self, video_frame: QVideoFrame) -> None:
        self.rear_video_frame = video_frame

    @pyqtSlot()
    def get_front_camera_uri(self) -> str:
        attr = self._model.read_attr()
        return attr['front_camera']['uri']

    @pyqtSlot()
    def get_rear_camera_uri(self) -> str:
        attr = self._model.read_attr()
        return attr['rear_camera']['uri']

    def get_front_target(self) -> list:
        attr = self._model.read_attr()
        return attr['front_camera']['targets']

    def get_rear_target(self) -> list:
        attr = self._model.read_attr()
        return attr['rear_camera']['targets']

    def get_camera_table_model(self) -> dict:
        cameras = self.get_cameras()
        table_model =  Js06CameraTableModel(cameras)
        return table_model

    def check_exit_status(self) -> bool:
        normal_exit = Js06Settings.get('normal_shutdown')
        Js06Settings.set('normal_shutdown', False)
        return normal_exit

    def update_cameras(self, cameras: list) -> None:
        # Remove deleted cameras
        cam_id_in_db = [cam["_id"] for cam in self._model.read_cameras()]
        cam_id_in_arg = [cam["_id"] for cam in cameras]
        for cam_id in cam_id_in_db:
            if cam_id not in cam_id_in_arg:
                self._model.delete_camera(cam_id)

        # Update existing camera or Insert new cameras
        for cam in cameras:
            self._model.update_camera(cam, upsert=True)

    @pyqtSlot()
    def close_process(self) -> None:
        Js06Settings.set('normal_shutdown', True)

    def get_attr(self) -> dict:
        self._model.get_attr()
        attr_doc = None
        if self._attr.count_documents({}):
            attr_doc = list(self._attr.find().sort("_id", -1).limit(1))[0]
        return attr_doc
    
    def set_attr(self, model: dict) -> None:
        self._model.update_attr(model)

    @pyqtSlot()
    def restore_defaults(self) -> None:
        Js06Settings.restore_defaults()

    @pyqtSlot(bool)
    def set_normal_shutdown(self) -> None:
         Js06Settings.set('normal_shutdown', True)

    def get_cameras(self) -> list:
        return self._model.read_cameras()
