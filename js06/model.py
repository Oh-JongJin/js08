#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import json
import os
import platform
from PyQt5.QtGui import QImage
import pymongo

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QRunnable, QStandardPaths, Qt, QSettings

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

    def connect_to_db(self, uri: str, port: int, db: str) -> None:
        client = pymongo.MongoClient(uri, port)
        self.db = client[db]
    # end of connect_to_db

    def setup_db(self, attr_json: list, camera_json: list) -> None:
        """
        Paramters:
            attr_json: list of attribute dictionary
            camera_json: list of camerae dictionary
        """
        self.db.camera.insert_many(camera_json)
    
        front = self.db.camera.find_one({'placement': 'front'})
        if attr_json:
            attr_json[-1]["platform"] = platform.platform()
            attr_json[-1]["camera"] = front
            self.db.attr.insert_many(attr_json)
    # end of setup_db

    def insert_camera(self, camera: dict) -> str:
        """Insert a camera.

        Parameters:
            camera: a camera dictionary

        Returns:
            The _id of the inserted camera
        """
        response = self.db.camera.insert_one(camera)
        return str(response.inserted_id)
    # end of insert_camera

    def upsert_camera(self, camera: dict) -> str:
        """Update a camera with matched _id or insert one.

        Parameters:
            camera: a camera dictionary

        Returns:
            The _id of the inserted camera if an upsert took place.
            Otherwise None.
        """
        response = self.db.camera.update_one(
            {"_id": camera["_id"]},
            {"$set": camera},
            upsert=True
        )

        if response.upserted_id:
            return str(response.upserted_id)
        else:
            return None
    # end of update_camera

    def delete_camera(self, _id: str) -> int:
        """Delete a camera with matching _id.

        Parameters:
          _id: _id of cameras to delete.
        
        Return:
          The number of cameras deleted.
        """
        response = self.db.camera.delete_one(
            {"_id": _id}
        )
        return response.deleted_count
    # end of delete_camera

    def delete_all_cameras(self) -> int:
        """Delete all cameras in the database.

        Parameters:

        Return:
            The number of cameras deleted.
        """
        response = self.db.camera.delete_many({})
        return response.deleted_count
    # end of delete_all_cameras

    def read_cameras(self) -> list:
        """Get all cameras in the database.

        Parameters:

        Returns:
            The list of all cameras
        """
        cr = self.db.camera.find()
        return [cam for cam in cr]
    # end of read_cameras

    def read_attr(self) -> dict:
        """Get the latest attribute in the database.

        Parameters:

        Returns:
            A dictionary of the latest attribute
        """
        cr = self.db.attr.find().sort('_id', pymongo.DESCENDING).limit(1)
        return next(cr)
    # end of read_attr

    def insert_attr(self, attr: dict) -> str:
        """Insert a new attribute.

        Parameters:
            attr: The attribute to insert. Must be a mutable mapping type. If 
            the attribute does not have an _id field one will be added 
            automatically.

        Returns:
            The inserted attributes' _id.
        """
        response = self.db.attr.insert_one(attr)
        return str(response.inserted_id)
    # end of insert_attr

    def write_discernment_result(self, epoch: int, id: int, discernment: bool):
        # self.db.disc.
        pass
    # end of write_discerment_result

# end of Js06Model

class Js06Settings:
    settings = QSettings('sijung', 'js06')

    defaults = {
        'observation_period': 1, # in minute
        'save_vista': True,
        'save_image_patch': True,
        'image_base_path': os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.PicturesLocation),
            'js06'
        ),
        'thread_count': 2,
        # Database settings
        'db_host': 'localhost',
        'db_port': 27017,
        'db_name': 'js06',
        'db_admin': 'sijung',
        'db_admin_password': 'sijung_pw',
        'db_user': 'js06',
        'db_user_password': 'js06_pw',
        # Hidden settings
        # 'window_size': [800, 600],
        'normal_shutdown': False
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

class Js06InferenceRunner(QRunnable):
    def __init__(self, model: Js06Model, epoch: int, id: int, image: QImage):
        super().__init__()
        self.setAutoDelete(True)

        self.model = model
        self.epoch = epoch
        self.id = id
        self.image = image
    # end of __init__

    def run(self):
        discernment = True
        self.model.write_discernment_result(self.epoch, self.id, discernment)
    # end of run

# end of Js06InferenceRunner

class Js06IoRunner(QRunnable):
    def __init__(self, path: str, image: QImage):
        super().__init__()
        self.setAutoDelete(True)

        self.path = path
        self.image = image
    # end of __init__

    def run(self):
        print(f'DEBUG: {self.path}')
        self.image.save(self.path)
    # end of run

# end of Js06IoRunner

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
