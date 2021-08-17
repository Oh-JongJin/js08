#!/usr/bin/env python3

import enum
import platform
import pymongo

from PyQt5.QtCore import QObject # pylint: disable=no-name-in-module

@enum.unique
class Js06TargetCategory(enum.Enum):
    SINGLE = 0
    COMPOUND = 1

    def __str__(self):
        category_to_str = {
            Js06TargetCategory.SINGLE: 'single',
            Js06TargetCategory.COMPOUND: 'compound'
        }
        return category_to_str[self]
    # end of __str__

    @classmethod
    def from_str(cls, category_str:str):
        dictionary = {
            'single': cls.SINGLE,
            'compound': cls.COMPOUND
        }
        return dictionary[category_str.strip().lower()]
    # end of from_str

# end of Js06TargetCategory

@enum.unique
class Js06Ordinal(enum.Enum):
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7
    
    def __str__(self):
        oridnal_to_str = {
            self.N: 'N',
            self.NE: 'NE',
            self.E: 'E',
            self.SE: 'SE',
            self.S: 'S',
            self.SW: 'SW',
            self.W: 'W',
            self.NW: 'NW'
            }
        return oridnal_to_str[self]
    # end of __str__
    
    @classmethod
    def from_str(cls, ordinal_str:str):
        dictionary = {
            'N': cls.N, # 'NORTH': cls.N,
            'NE': cls.NE, # 'NORTHEAST': cls.NE,
            'E': cls.E, # 'EAST': cls.E,
            'SE': cls.SE, # 'SOUTHEAST': cls.SE,
            'S': cls.S, # 'SOUTH': cls.S,
            'SW': cls.SW, # 'SOUTWEST': cls.SW,
            'W': cls.W, # 'WEST': cls.W,
            'NW': cls.NW, # 'NORTHWEST': cls.NW,
        }
        return dictionary[ordinal_str.strip().upper()]
    # end of from_str

# end of Js06Ordinal

class Js06Camera(QObject):
    def __init__(self, _id:str=None, label:str=None, manufacturer:str=None, 
    model:str=None, serial_number:str=None, resolution:tuple=None, 
    uri:str=None, direction:int=None, view_angle:int=None):
        super().__init__()
        self._id = _id
        self.label = label
        self.manufacturer = manufacturer
        self.model = model
        self.serial_number = serial_number
        self.resolution = resolution # (width, height)
        self.uri = uri
        self.direction = direction 
        self.view_angle = view_angle
    # end of __init__

    def from_dict(self, camera:dict):
        if '_id' in camera.keys():
            self._id = camera['_id']
        self.label = camera['label']
        self.manufacturer = camera['manufacturer']
        self.model = camera['model']
        self.serial_number = camera['serial_number']
        self.resolution = camera['resolution']
        self.uri = camera['uri']
        self.direction = camera['direction']
        self.view_angle = camera['view_angle']
    # end of from_dict

    def to_dict(self):
        doc = {
            'label': self.label,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'serial_number': self.serial_number,
            'resolution': self.resolution,
            'uri': self.uri,
            'direction': self.direction,
            'view_angle': self.view_angle
        }
        if self._id:
            doc['_id'] = self._id
        return doc
    # end of to_dict

    def to_simple_dict(self):
        """For the embeded camera in Js06Attribute
        """
        doc = {
            '_id': self._id,
            'label': self.label,
            'resolution': self.resolution,
            'uri': self.uri,
            'direction': self.direction,
            'view_angle': self.view_angle
        }
        return doc
    # end of to_dict

# end of Js06Camera

class Js06Attribute(QObject):
    def __init__(self, label:str=None, version:str=None, 
    serial_number:str=None, os_str:str=None, location:tuple=None, 
    camera:Js06Camera=None, targets:list=[], 
    discernment_model:tuple=None, vis_collection=None):
        super().__init__()
        self.label = label
        self.version = version
        self.serial_number = serial_number
        self.platform = os_str if os_str else platform.platform()
        self.location = location
        self.camera = camera
        self.targets = list(targets)
        self.discernment_model = discernment_model
        self.vis_collection = vis_collection
    # end of __init__

    def from_dict(self, attr:dict):
        self.label = attr['label']
        self.version = attr['version']
        self.serial_number = attr['serial_number']
        self.platform = attr['platform']
        self.location = attr['location']
        self.discernment_model = attr['discernment_model']
        self.vis_collection = attr['vis_collection']

        self.camera = Js06Camera()
        self.camera.from_dict(attr['camera'])

        self.targets = []
        for target in attr['targets']:
            t = Js06Target()
            t.from_dict(target)
            self.targets.append(t)
    # end of from_dict

    def to_dict(self):
        doc = {
            'label': self.label,
            'version': self.version,
            'serial_number': self.serial_number,
            'platform': self.platform,
            'location': self.location,
            'camera': self.camera.to_dict() if self.camera else None,
            'targets': [],
            'discernment_model': None,
            'vis_collection': self.vis_collection
        }
        
        for target in self.targets:
            doc['targets'].append(target.to_dict())

        return doc
    # end of to_dict

# end of Js06Attribute

class Js06Target(QObject):
    def __init__(self, label:str=None, distance:float=None, ordinal:Js06Ordinal=None,
    category:Js06TargetCategory=None, roi:tuple=None):
        """ 
            arguments:
                roi: [upper left coordinate, lower right coordinate]
        """
        super().__init__()
        self.label = label
        self.dist = distance # in kilometer
        self.ordinal = ordinal
        self.category = category # category: single, compound
        self.roi = roi # [ (x, y) of upper left, (x, y) of lower right ]
    # end of __init__

    def from_dict(self, target:dict):
        self.label = target['label']
        self.dist = target['distance']
        self.ordinal = Js06Ordinal.from_str(target['ordinal'])
        self.category = Js06TargetCategory.from_str(target['category'])
        self.roi = target['roi']
    # end of from_dict

    def to_dict(self):
        doc = {
            'label': self.label,
            'distance': self.dist,
            'ordinal': str(self.ordinal),
            'category': str(self.category),
            'roi': self.roi
        }
        return doc
    # end of document

# end of Js06Target

class Js06Model(QObject):
    def __init__(self):
        super().__init__()
        self.client = None
    # end of __init__

    def connect_to_db(self, uri:str, port:int):
        self.db = pymongo.MongoClient(uri, port).js06
    # end of connect_to_db
        
    def insert_camera(self, camera:Js06Camera):
        response = self.db.camera.insert_one(camera.to_dict())
        return response
    # end of insert_camera

    def update_camera(self, camera:Js06Camera):
        response = self.db.camera.update_many(
            { "_id": camera._id},
            { "$set": camera.to_dict() }
        )
        return response
    # end of update_camera

    def delete_camera(self, _id:object):
        response = self.db.camera.delete_one(
            { "_id": _id }
        )
        return response
    # end of delete_camera

    def read_cameras(self):
        cameras = []
        cr = self.db.camera.find()
        for cam in cr:
            c = Js06Camera()
            c.from_dict(cam)
            cameras.append(c)
        return cameras
    # end of read_cameras

    def read_attr(self):
        attr = self.db.attr.find().sort('_id', pymongo.DESCENDING).limit(1)
        a = Js06Attribute()
        a.from_dict(next(attr))
        return a
    # end of read_attr

    def insert_attr(self, attr:Js06Attribute):
        response = self.db.attr.insert_one(attr.to_dict())
        return response
    # end of insert_attr

# end of Js06Model

if __name__ == '__main__':
    import faker
    import pprint
    import random
    
    fake = faker.Faker()
    
    js06_model = Js06Model()
    js06_model.connect_to_db('localhost', 27017)

    print('Available targets: '
    f'{Js06TargetCategory.SINGLE}, {Js06TargetCategory.COMPOUND}')
    print()

    print('Available ordinals: '
    f'{Js06Ordinal.N}, {Js06Ordinal.NE}, '
    f'{Js06Ordinal.E}, {Js06Ordinal.SE}, '
    f'{Js06Ordinal.S}, {Js06Ordinal.SW}, '
    f'{Js06Ordinal.W}, {Js06Ordinal.NW}'
    )
    print()

    print('Js06Camera with default values:')
    pprint.pprint(Js06Camera().to_dict())
    print()

    camera = Js06Camera()
    camera.label = 'front'
    camera.manufacturer = fake.company()
    camera.model = 'XYZ-10'
    camera.serial_number = 'ABC-0123456789'
    camera.resolution = random.choice([(1920, 1080), (1366, 768), (1440, 900), (1536, 864)])
    camera.uri = 'rtsp://' + fake.ipv4_private()
    camera.direction = random.randint(0, 179)
    camera.view_angle = random.choice([90, 120, 180, 200])

    print('Js06Attribute with default values:')
    pprint.pprint(Js06Attribute().to_dict())
    print()

    response = js06_model.insert_camera(camera)
    print(response)

    print('Js06Target with default values:')
    pprint.pprint(Js06Target().to_dict())
    print()

    cameras = js06_model.read_cameras()

    js06_attr = Js06Attribute()
    js06_attr.label = 'brave js06'
    js06_attr.version = '0.1'
    js06_attr.serial_number = '0123456789XYZ'
    js06_attr.location = (float(fake.longitude()), float(fake.latitude()))
    js06_attr.camera = random.choice(cameras)

    ordinals = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    for i in range(2):
        target = Js06Target()
        target.label = str(i)
        target.dist = random.uniform(0, 20)
        target.ordinal = Js06Ordinal.from_str(random.choice(ordinals))
        target.category = random.choice([Js06TargetCategory.SINGLE, Js06TargetCategory.COMPOUND])
        target.roi = (
            (random.uniform(-1, 0), random.uniform(0, 1)), 
            (random.uniform(0, 1), random.uniform(-1, 0))
            )
        js06_attr.targets.append(target)

    print('Js06Attribute with sample values:')
    pprint.pprint(js06_attr.to_dict())


    js06_model.insert_attr(js06_attr)
    js06_attr_2 = js06_model.read_attr()
    pprint.pprint(js06_attr_2.to_dict())

# end of model.py
