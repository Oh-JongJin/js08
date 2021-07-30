#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import enum
import platform

from pymongo import MongoClient

@enum.unique
class Js06TargetCategory(enum.Enum):
    SINGLE = 0
    COMPOUND = 1

    def __str__(self):
        category_to_str = {
            Js06TargetCategory.SINGLE: "single",
            Js06TargetCategory.COMPOUND: "compound"
        }
        return category_to_str[self]
    # end of __str__

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
            Js06Ordinal.N: "N",
            Js06Ordinal.NE: "NE",
            Js06Ordinal.E: "E",
            Js06Ordinal.SE: "SE",
            Js06Ordinal.S: "S",
            Js06Ordinal.SW: "SW",
            Js06Ordinal.W: "W",
            Js06Ordinal.NW: "NW"
            }
        return oridnal_to_str[self]
    # end of __str__

# end of Js06Ordinal

class Js06Camera:
    def __init__(self, id:int=None, label:str=None, manufacturer:str=None, model:str=None, 
    serial_number:str=None, resolution:tuple=None, uri:str=None, direction:int=None, view_angle:int=None):
        self.id = id
        self.label = label
        self.manufacturer = manufacturer
        self.model = model
        self.serial = serial_number
        
        # integer tuple: (width, height)
        self.res = resolution 
        self.uri = uri
        self.direction = direction 
        self.view_angle = view_angle
    # end of __init__

    def check_duplication():
        pass
    # end of check_duplication

    def to_dict(self):
        doc = {
            'label': self.label,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'serial': self.serial,
            'resolution': self.res,
            'uri': self.uri,
            'direction': self.direction,
            'view_angle': self.view_angle
        }
        return doc
    # end of to_dict

# end of Js06Camera

class Js06Attribute:
    def __init__(self, id:int=None, label:str=None, version:str=None, serial_number:str=None,
    os_str:str=None, location:tuple=None, camera:tuple=None, target:tuple=None, 
    discernment_model:tuple=None, vis_collection=None):
        self.id = id # check the latest id and add up by one.
        self.label = label
        self.ver = version
        self.sn = serial_number
        self.platform = os_str if os_str else platform.platform()
        self.loc = location
        self.camera = tuple(camera)
        self.target = tuple(target)
        self.disc_model = discernment_model
        self.vis_collection = vis_collection
    # end of __init__

    def to_dict(self):
        doc = {
            'label': self.label,
            'version': self.ver,
            'serial_number': self.sn,
            'platform': self.platform,
            'location': self.loc,
            'camera': [],
            'target': [],
            'discernment_model': None,
            'vis_collection': self.vis_collection
        }

        for cam in self.camera:
            doc['camera'].append(cam.to_dict())
        
        for target in self.target:
            doc['target'].append(target.to_dict())

        return doc
    # end of to_dict

# end of Js06Attribute

class Js06Target:
    def __init__(self, label:str=None, distance:float=None, ordinal:Js06Ordinal=None,
    category:Js06TargetCategory=None, roi:tuple=None):
        """ 
            arguments:
                roi: [upper left coordinate, lower right coordinate]
        """
        self.label = label

        self.dist = distance # in kilometer

        self.ordinal = ordinal

        # category: single, compound
        self.category = category

        # [ (x, y) of upper left, (x, y) of lower right ]
        self.roi = roi
    # end of __init__

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

class Js06Db:
    def __init__(self, uri:str=None, port:int=None):
        super().__init__()
        self.uri = uri if uri else 'localhost'
        self.port = port if port else 27017
        # self.db_name = 'js06'
        self.client = MongoClient(self.uri, self.port)
        self.js06_db = self.client.js06
        self.camera_db = self.client.camera
    # end of __init__

# end of Js06Db

if __name__ == '__main__':
    pass

# end of db.py
