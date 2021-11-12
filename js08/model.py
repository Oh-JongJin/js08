#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import datetime
import os
import platform

from typing import List

import numpy as np
import pymongo

from PyQt5.QtCore import (QAbstractTableModel, QModelIndex, QRect, QRunnable,
                          QSettings, QStandardPaths, Qt)
from PyQt5.QtGui import QImage


Js08TargetCategory = ['single', 'compound']
Js08Wedge = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']


class Js08SimpleTarget:
    """Simple target"""

    def __init__(self, label: str, wedge: str, azimuth: float, distance: float, roi: QRect, mask: QImage, input_width: int, input_height: int):
        super().__init__()
        self.label = label
        self.wedge = wedge
        self.azimuth = azimuth
        self.distance = distance
        self.roi = roi

        self.mask = self.img_to_arr(mask, input_width, input_height)

        # image are set using clip_roi
        self.image = None
        self.discernment = False

    def clip_roi(self, vista: QImage) -> QImage:
        trimmed = vista.copy(self.roi)
        # multiply self.mask with trimmed
        return trimmed

    def img_to_arr(self, image: QImage, width: int, height: int) -> np.ndarray:
        """
        Parameters:
            image: mask image in RGB format
            width: width of mask array
            height: height of mask array
        """
        img = image.scaled(
            width, 
            height,
            Qt.IgnoreAspectRatio, 
            Qt.SmoothTransformation
            )

        # The following code is referring to:
        # https://stackoverflow.com/questions/19902183/qimage-to-numpy-array-using-pyside
        ptr = img.bits()
        ptr.setsize(int(height * width * 3))
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
        arr = arr.astype(np.float32) / 255

        return arr


class Js08CameraTableModel(QAbstractTableModel):
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
            "azimuth",
            "view_angle"
        ]

        self._data = []
        for el in data:
            row = [el[col] for col in self._headers]
            self._data.append(row)

    def data(self, index: QModelIndex, role: int):
        if role in (Qt.DisplayRole, Qt.EditRole):
            return str(self._data[index.row()][index.column()])

    def rowCount(self, index: QModelIndex):
        return len(self._data)

    def columnCount(self, index: QModelIndex):
        return len(self._headers)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        else:
            return super().headerData(section, orientation, role)

    # TODO(Kyungwon): It may need to keep read-only indexes
    def flags(self, index: QModelIndex):
        if index.column() == 0:
            return super().flags(index)
        else:
            return super().flags(index) | Qt.ItemIsEditable

    def setData(self, index: QModelIndex, value: object, role: int):
        if index.isValid() and role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        else:
            return False

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

    def removeRows(self, position: int, rows: int, parent: object):
        self.beginRemoveRows(
            parent or QModelIndex(),
            position,
            position + rows - 1
        )
        for i in range(rows):
            del (self._data[position])
        self.endRemoveRows()

    def get_data(self):
        data_dict = []
        for row in self._data:
            doc = {col: row[i] for i, col in enumerate(self._headers)}
            data_dict.append(doc)
        return data_dict


class Js08AttrModel:
    def __init__(self):
        super().__init__()
        self.db = None

    def connect_to_db(self, uri: str, port: int, db: str) -> None:
        client = pymongo.MongoClient(uri, port)
        self.db = client[db]

    def setup_db(self, attr_json: list, camera_json: list) -> None:
        """Create MongoDB collections for JS-08.

        This method creates the following collections:
        * attr: attributes collection
        * camera: camera specifications
        * visibility: visibility measurement records

        Paramters:
            attr_json: list of attribute dictionary
            camera_json: list of camerae dictionary
        """
        coll = self.db.list_collection_names()
        
        if 'camera' not in coll or self.db.camera.count_documents({}) == 0:
            self.db.camera.insert_many(camera_json)
    
        if 'attr' not in coll or self.db.attr.count_documents({}) == 0:
            front_cam = self.db.camera.find_one({'placement': 'front'})
            front_cam['camera_id'] = front_cam.pop('_id')

            rear_cam = self.db.camera.find_one({'placement': 'rear'})
            rear_cam['camera_id'] = rear_cam.pop('_id')

            attr_json[-1]['platform'] = platform.platform()
            attr_json[-1]['front_camera'] = front_cam
            attr_json[-1]['rear_camera'] = rear_cam

            self.db.attr.insert_many(attr_json)

        if 'visibility' not in coll:
            self.db.create_collection('visibility',
                timeseries = {
                  'timeField': 'timestamp',
                  'metaField': 'attr_id',
                  'granularity': 'minutes'
                }
            )

        if 'discernment' not in coll:
            self.db.create_collection('discernment',
                timeseries = {
                  'timeField': 'timestamp',
                  'metaField': 'attr_id',
                  'granularity': 'minutes'
                }
            )

    def insert_camera(self, camera: dict) -> str:
        """Insert a camera.

        Parameters:
            camera: a camera dictionary

        Returns:
            The _id of the inserted camera
        """
        response = self.db.camera.insert_one(camera)
        return str(response.inserted_id)

    def upsert_camera(self, camera: dict) -> str:
        """Update a camera with matched _id or insert one.

        Parameters:
            camera: a camera dictionary

        Returns:
            The _id of the inserted camera if an upsert took place.
            Otherwise None.
        """
        if '_id' in camera:
            response = self.db.camera.update_one(
                {'_id': camera['_id']},
                {'$set': camera},
                upsert=True
            )
        else:
            response = self.db.camera.insert_one(camera)

        if type(response) is pymongo.results.UpdateResult and response.upserted_id:
            return str(response.upserted_id)
        elif type(response) is pymongo.results.InsertOneResult and response.inserted_id:
            return str(response.inserted_id)
        else:
            return None

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

    def delete_all_cameras(self) -> int:
        """Delete all cameras in the database.

        Parameters:

        Return:
            The number of cameras deleted.
        """
        response = self.db.camera.delete_many({})
        return response.deleted_count

    def read_cameras(self) -> list:
        """Get all cameras in the database.

        Parameters:

        Returns:
            The list of all cameras
        """
        cr = self.db.camera.find()
        return [cam for cam in cr]

    def read_attr(self) -> dict:
        """Get the latest attribute in the database.

        Parameters:

        Returns:
            A dictionary of the latest attribute
        """
        cr = self.db.attr.find().sort('_id', pymongo.DESCENDING).limit(1)
        return next(cr)

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

    def write_visibility(self, wedge_visibility: dict):
        attr = self.read_attr()
        wedge_visibility['attr_id'] = attr['_id']
        epoch = wedge_visibility.pop('epoch')
        kst = datetime.timezone(datetime.timedelta(hours=9))
        wedge_visibility['timestamp'] = datetime.datetime.fromtimestamp(epoch, kst)
        self.db.visibility.insert_one(wedge_visibility)

    def write_discernment(self, epoch: int, front_targets: List[Js08SimpleTarget], rear_targets: List[Js08SimpleTarget]):
        attr = self.read_attr()
        kst = datetime.timezone(datetime.timedelta(hours=9))
        discernment = {
            'attr_id': attr['_id'],
            'timestamp': datetime.datetime.fromtimestamp(epoch, kst)
        }

        for target in front_targets:
            discernment[target.label] = target.discernment

        for target in rear_targets:
            discernment[target.label] = target.discernment

        self.db.discernment.insert_one(discernment)

class Js08Settings:
    settings = QSettings('sijung', 'js08')

    defaults = {
        'save_vista': True,
        'save_image_patch': True,
        'image_base_path': os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.PicturesLocation),
            'js08'
        ),
        'inference_batch_size': 8,
        # Database settings
        'db_host': 'localhost',
        'db_port': 27017,
        'db_name': 'js08',
        'db_admin': 'sijung',
        'db_admin_password': 'sijung_pw',
        'db_user': 'js08',
        'db_user_password': 'js08_pw',
        # Hidden settings
        'window_size': (1230, 700),
        'normal_shutdown': False
    }

    @classmethod
    def set(cls, key, value):
        cls.settings.setValue(key, value)

    @classmethod
    def get(cls, key):
        return cls.settings.value(
            key,
            cls.defaults[key],
            type(cls.defaults[key])
        )

    @classmethod
    def restore_defaults(cls):
        for key, value in cls.defaults.items():
            cls.set(key, value)


class Js08IoRunner(QRunnable):
    def __init__(self, path: str, image: QImage):
        super().__init__()
        self.setAutoDelete(True)

        self.path = path
        self.image = image

    def run(self):
        self.image.save(self.path)


if __name__ == '__main__':
    import pprint
    import random

    import faker

    fake = faker.Faker()

    js08_model = Js08AttrModel()
    js08_model.connect_to_db('localhost', 27017, 'js08')

    camera = {}
    camera['label'] = 'front'
    camera['manufacturer'] = fake.company()
    camera['model'] = 'XYZ-10'
    camera['serial_number'] = 'ABC-0123456789'
    camera['resolution'] = random.choice([(1920, 1080), (1366, 768), (1440, 900), (1536, 864)])
    camera['uri'] = 'rtsp://' + fake.ipv4_private()
    camera['azimuth'] = random.randint(0, 179)
    camera['view_angle'] = random.choice([90, 120, 180, 200])

    response = js08_model.insert_camera(camera)
    print(response)

    cameras = js08_model.read_cameras()

    js08_attr = {}
    js08_attr['label'] = 'brave js08'
    js08_attr['version'] = '0.1'
    js08_attr['serial_number'] = '0123456789XYZ'
    js08_attr['location'] = (float(fake.longitude()), float(fake.latitude()))
    js08_attr['platform'] = platform.platform()
    js08_attr['camera'] = random.choice(cameras)

    for i in range(2):
        target = {}
        target['label'] = str(i)
        target['dist'] = random.uniform(0, 20)
        target['ordinal'] = random.choice(Js08Wedge)
        target['category'] = random.choice(Js08TargetCategory)
        target['roi'] = (
            (random.uniform(-1, 0), random.uniform(0, 1)),
            (random.uniform(0, 1), random.uniform(-1, 0))
        )
        js08_attr['targets'].append(target)

    print('Js08Attribute with sample values:')
    pprint.pprint(js08_attr)

    js08_model.insert_attr(js08_attr)
    js08_attr_2 = js08_model.read_attr()
    pprint.pprint(js08_attr_2.to_dict())
