#!/usr/bin/env python3
"""
This code is not include AWS Sensor, only Visibility
"""

import traceback
import binascii
import struct
import time

from influxdb import InfluxDBClient, exceptions
from PyQt5.QtCore import QThread


class SaveDB(QThread):
    def __init__(self):
        super().__init__()
        self.flag = False
        self.c_visibility = None

    def run(self):
        while self.flag:
            try:
                client = InfluxDBClient('localhost', 8086)
                save_time = time.time_ns()
                client.create_database("Sijung")
                client.switch_database("Sijung")
                points = [{"measurement": "JS06",
                        "tags": {"name": "Sijung"},
                        "fields": {"vis": float(self.c_visibility)},
                        "time": save_time}]
                client.write_points(points=points, protocol="json")
                client.close()

                # Save every 1 minute.
                time.sleep(60)

            except TypeError:
                pass

    def stop(self):
        """Sets flag to False and waits for thread to finish"""
        self.flag = False
        self.terminate()
