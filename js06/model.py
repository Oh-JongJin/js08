#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import json
import os
import platform
import pymongo

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QRunnable, Qt, QSettings, pyqtSlot

Js06TargetCategory = ['single', 'compound']
Js06Ordinal = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

class Js06CameraTableModel(QAbstractTableModel):
    def __init__(self, data: list):
        super().__init__()
        self._headers = [
            "_id",
            "placement",
            "label",
            "manufacturer",
            "model",
            "serial_number",
            "resolution",
            "uri",
            "direction",
            "view_angle"
        ]

        self._data = []
        for el in data:
            row = [el[col] for col in self._headers]
            self._data.append(row)
    # end of __init__

    def data(self, index: QModelIndex, role: int):
        if role in (Qt.DisplayRole, Qt.EditRole):
            return str(self._data[index.row()][index.column()])
    # end of data

    def rowCount(self, index: QModelIndex):
        return len(self._data)
    # end of rowCount

    def columnCount(self, index: QModelIndex):
        return len(self._headers)
    # end of columnCount

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        else:
            return super().headerData(section, orientation, role)
    # end of headerData

    # TODO(Kyungwon): It may need to keep read-only indexes
    def flags(self, index: QModelIndex):
        if index.column() == 0:
            return super().flags(index)
        else:
            return super().flags(index) | Qt.ItemIsEditable
    # end of flags

    def setData(self, index: QModelIndex, value: object, role: int):
        if index.isValid() and role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        else:
            return False
    # end of setData

    def insertRows(self, position: int, rows: int, parent: object):
        self.beginInsertRows(
            parent or QModelIndex(),
            position,
            position + rows - 1
        )
        for i in range(rows):
            default_row = [''] * len(self._headers)
            self._data.insert(position, default_row)
        self.endInsertRows()
    # end of insertRows

    def removeRows(self, position: int, rows: int, parent: object):
        self.beginRemoveRows(
            parent or QModelIndex(),
            position,
            position + rows - 1
        )
        for i in range(rows):
            del (self._data[position])
        self.endRemoveRows()
    # end of removeRows

    def get_data(self):
        data_dict = []
        for row in self._data:
            doc = {col: row[i] for i, col in enumerate(self._headers)}
            data_dict.append(doc)
        return data_dict
    # end of save_data

# end of Js06CameraTableModel

class Js06Model:
    def __init__(self):
        super().__init__()
        self.db = None
    # end of __init__

    def setup_db(self, attr_json: str, camera_json: str):
        """
        Paramters:
          attr_json: Path to the attribute JSON file.
          camera_json: Path to the files containing list of camera information.
        """
        if camera_json is not None:
            with open(camera_json, 'r') as fh:
                camera_data = json.load(fh)
            self.db.camera.insert_many(camera_data)

        if attr_json is not None:
            with open(attr_json, 'r') as fh:
                attr_data = json.load(fh)
                attr_data[0]["platform"] = platform.platform()
            self.db.attr.insert_one(attr_data[0])
    # end of setup_db

    def connect_to_db(self, uri: str, port: int, db: str):
        client = pymongo.MongoClient(uri, port)
        self.db = client[db]
    # end of connect_to_db

    def insert_camera(self, camera: dict):
        response = self.db.camera.insert_one(camera)
        return response
    # end of insert_camera

    def update_camera(self, camera: dict, upsert: bool = False):
        response = self.db.camera.update_one(
            {"_id": camera["_id"]},
            {"$set": camera}
        )
        return response
    # end of update_camera

    def delete_camera(self, _id: str):
        response = self.db.camera.delete_one(
            {"_id": _id}
        )
        return response
    # end of delete_camera

    def delete_all_cameras(self):
        response = self.db.camera.delete_many({})
        return response
    # end of delete_all_cameras

    def read_cameras(self):
        cameras = []
        cr = self.db.camera.find()
        for cam in cr:
            cameras.append(cam)
        return cameras
    # end of read_cameras

    def read_attr(self):
        cr = self.db.attr.find().sort('_id', pymongo.DESCENDING).limit(1)
        if cr.count() == 0:
            attr_json = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     "../resources/attr.json")
            camera_json = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                       "../resources/camera.json")
            self.setup_db(attr_json, camera_json)
        a = next(cr)
        return a
    # end of read_attr

    def insert_attr(self, attr: dict):
        response = self.db.attr.insert_one(attr)
        return response
    # end of insert_attr

    # TODO(Kyungwon): target attribute was moved into camera attribute.
    def update_attr(self, attr: dict):
        self.db.attr.update({'model': 'JS-08'}, {'$set': {'targets': attr}})
    # end of update_attr

# end of Js06Model

class Js06InferenceRunner(QRunnable):
    def __init__(self, i):
        super().__init__()
        self.i = i
        self.setAutoDelete(True)
    # end of __init__

    @pyqtSlot()
    def run(self):
        print(f"{self.i}: Sleeping 3 seconds")
        import time
        time.sleep(3)
    # end of run

# end of Js06InferenceRunner

class Js06Settings:
    settings = QSettings('sijung', 'js06')

    defaults = {
        'camera': 3,
        'normal_shutdown': False,
        'db_host': 'localhost',
        'db_port': 27017,
        'db_name': 'js06',
        'db_admin': 'sijung',
        'db_admin_password': 'sijung_pw',
        'db_user': 'js06',
        'db_user_password': 'js06_pw'
    }

    @classmethod
    def set(cls, key, value):
        cls.settings.setValue(key, value)
    # end of set

    @classmethod
    def get(cls, key):
        return cls.settings.value(
            key,
            cls.defaults[key],
            type(cls.defaults[key])
        )
    # end of get

    @classmethod
    def restore_defaults(cls):
        for key, value in cls.defaults.items():
            cls.set(key, value)
    # end of restore_defaults

# end of Js06Settings

if __name__ == '__main__':
    import faker
    import pprint
    import random

    fake = faker.Faker()

    js06_model = Js06Model()
    js06_model.connect_to_db('localhost', 27017, 'js06')

    camera = {}
    camera['label'] = 'front'
    camera['manufacturer'] = fake.company()
    camera['model'] = 'XYZ-10'
    camera['serial_number'] = 'ABC-0123456789'
    camera['resolution'] = random.choice([(1920, 1080), (1366, 768), (1440, 900), (1536, 864)])
    camera['uri'] = 'rtsp://' + fake.ipv4_private()
    camera['direction'] = random.randint(0, 179)
    camera['view_angle'] = random.choice([90, 120, 180, 200])

    response = js06_model.insert_camera(camera)
    print(response)

    cameras = js06_model.read_cameras()

    js06_attr = {}
    js06_attr['label'] = 'brave js06'
    js06_attr['version'] = '0.1'
    js06_attr['serial_number'] = '0123456789XYZ'
    js06_attr['location'] = (float(fake.longitude()), float(fake.latitude()))
    js06_attr['platform'] = platform.platform()
    js06_attr['camera'] = random.choice(cameras)

    for i in range(2):
        target = {}
        target['label'] = str(i)
        target['dist'] = random.uniform(0, 20)
        target['ordinal'] = random.choice(Js06Ordinal)
        target['category'] = random.choice(Js06TargetCategory)
        target['roi'] = (
            (random.uniform(-1, 0), random.uniform(0, 1)),
            (random.uniform(0, 1), random.uniform(-1, 0))
        )
        js06_attr['targets'].append(target)

    print('Js06Attribute with sample values:')
    pprint.pprint(js06_attr)

    js06_model.insert_attr(js06_attr)
    js06_attr_2 = js06_model.read_attr()
    pprint.pprint(js06_attr_2.to_dict())

# end of model.py
