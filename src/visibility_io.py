#!/usr/bin/env python3
#
# Copyright 2020-21 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import datetime

from influxdb import InfluxDBClient

class Js06VisibilityIo:
    def __init__(self):
        super().__init__()
        self.hostname = 'localhost'
        self.port = 8086
        self.db_name = 'js06'
        self.client = InfluxDBClient(self.hostname, self.port)        
        
    def create_database(self, db_name=None):
        if db_name is not None:
            self.db_name = db_name
        self.client.create_database(self.db_name)
        
    def write(self, value={}, tags={}):
        """Write to visibility values to DB.

        Allowed keys for value are the octal directions:
        * north
        * northeast
        * east
        * southeast
        * south
        * southwest
        * west
        * northwest

        The visibility should be given in km.
        """

        self.client.switch_database(self.db_name)
        now = datetime.datetime.now()
        current_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        json_body = [{
            'measurement': 'visibility',
            'tags': tags,
            'time': current_time,
            'fields': value
        }]
        self.client.write_points(json_body)

# end of Js06VisibilityIo

if __name__ == '__main__':
    vis_io = Js06VisibilityIo()
    vis_io.create_database()
    print('Databases: ', end='')
    print(vis_io.client.get_list_database())

    vis_io.write({'north': 10})
    result = vis_io.client.query('SELECT "duration" FROM "js06"."autogen"."brushEvents" WHERE time > now() - 4d GROUP BY "user"')
    points = result.get_points(tags={})
    for point in points:
        print(point)
# end of visibility_io.py