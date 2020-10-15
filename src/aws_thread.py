#!/usr/bin/env python3

import binascii
import serial
import struct
import time

from influxdb import InfluxDBClient
from PyQt5 import QtWidgets, QtGui, QtCore


class AwsThread(QtCore.QThread):
    def __init__(self):
        super().__init__()
        self.run_flag = False

    def run(self):
        while self.run_flag:
            try:
                write_aws = b'\x01\x03\x00\x00\x00\x29\x84\x14'
                self.ser = serial.Serial(port="COM9", baudrate=9600, parity=serial.PARITY_EVEN,
                                         stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,
                                         timeout=1)
                if self.ser.readable():
                    self.ser.write(write_aws)
                    res = self.ser.readline()

                    # Weather sensor value parsing, replace processing
                    wind_speed_hex = f"{hex(res[8]) + ' ' + hex(res[7]) + ' ' + hex(res[10]) + ' ' + hex(res[9])}".replace(
                        "0x0 ", "0x00 ").replace("0x1 ", "0x10 ").replace("0x2 ", "0x20 ").replace("0x3 ", "0x30 ").replace(
                        "0x4 ", "0x40 ").replace("0x5 ", "0x50 ").replace("0x6 ", "0x60 ").replace("0x7 ", "0x70 ") \
                        .replace("0x8 ", "0x80 ").replace("0x9 ", "0x90 ").replace("0xa ", "0xa0 ").replace("0xb ", "0xb0 ") \
                        .replace("0xc ", "0xc0 ").replace("0xd ", "0xd0 ").replace("0xe ", "0xe0 ").replace("0xf ", "0xF0 ") \
                        .replace("0x00 0x00 0x00 0x0", "0x00 0x00 0x00 0x00")
                    temp_hex = f"{hex(res[12]) + ' ' + hex(res[11]) + ' ' + hex(res[14]) + ' ' + hex(res[13])}".replace(
                        "0x0 ", "0x00 ").replace("0x1 ", "0xA0 ").replace("0x2 ", "0xB0 ").replace("0x3 ",
                                                                                                   "0xC0 ").replace(
                        "0x4 ", "0x40 ").replace("0x5 ", "0x50 ").replace("0x6 ", "0x60 ").replace("0x7 ", "0x70 ") \
                        .replace("0x8 ", "0x80 ").replace("0x9 ", "0x90 ").replace("0xa ", "0xa0 ").replace("0xb ",
                                                                                                            "0xb0 ") \
                        .replace("0xc ", "0xc0 ").replace("0xd ", "0xd0 ").replace("0xe ", "0xe0 ").replace("0xf ",
                                                                                                            "0xF0 ")
                    humid_hex = f"{hex(res[16]) + ' ' + hex(res[15]) + ' ' + hex(res[18]) + ' ' + hex(res[17])}".replace(
                        "0x0 ", "0x00 ").replace("0x1 ", "0xA0 ").replace("0x2 ", "0xB0 ").replace("0x3 ",
                                                                                                   "0xC0 ").replace(
                        "0x4 ", "0x40 ").replace("0x5 ", "0x50 ").replace("0x6 ", "0x60 ").replace("0x7 ", "0x70 ") \
                        .replace("0x8 ", "0x80 ").replace("0x9 ", "0x90 ").replace("0xa ", "0xa0 ").replace("0xb ",
                                                                                                            "0xb0 ") \
                        .replace("0xc ", "0xc0 ").replace("0xd ", "0xd0 ").replace("0xe ", "0xe0 ").replace("0xf ",
                                                                                                            "0xF0 ")
                    pressure_hex = f"{hex(res[20]) + ' ' + hex(res[19]) + ' ' + hex(res[22]) + ' ' + hex(res[21])}".replace(
                        "0x0 ", "0x00 ").replace("0x1 ", "0xA0 ").replace("0x2 ", "0xB0 ").replace("0x3 ",
                                                                                                   "0xC0 ").replace(
                        "0x4 ", "0x40 ").replace("0x5 ", "0x50 ").replace("0x6 ", "0x60 ").replace("0x7 ", "0x70 ") \
                        .replace("0x8 ", "0x80 ").replace("0x9 ", "0x90 ").replace("0xa ", "0xa0 ").replace("0xb ",
                                                                                                            "0xb0 ") \
                        .replace("0xc ", "0xc0 ").replace("0xd ", "0xd0 ").replace("0xe ", "0xe0 ").replace("0xf ",
                                                                                                            "0xF0 ")
                    pm25_hex = f"{hex(res[54]) + ' ' + hex(res[53]) + ' ' + hex(res[56]) + ' ' + hex(res[55])}".replace(
                        "0x0 ", "0x00 ").replace("0x1 ", "0x10 ").replace("0x2 ", "0x20 ").replace("0x3 ", "0x30 ").replace(
                        "0x4 ", "0x40 ").replace("0x5 ", "0x50 ").replace("0x6 ", "0x60 ").replace("0x7 ", "0x70 ") \
                        .replace("0x8 ", "0x80 ").replace("0x9 ", "0x90 ").replace("0xa ", "0xa0 ").replace("0xb ", "0xb0 ") \
                        .replace("0xc ", "0xc0 ").replace("0xd ", "0xd0 ").replace("0xe ", "0xe0 ").replace("0xf ", "0xF0 ") \
                        .replace("0x00 0x00 0x00 0x0", "0x00 0x00 0x00 0x00")

                    # Remove 0x of hexadecimal numbers.
                    wind_speed_non = wind_speed_hex.replace("0x", '')
                    temp_non = temp_hex.replace("0x", '')
                    humid_non = humid_hex.replace("0x", '')
                    pressure_non = pressure_hex.replace("0x", '')
                    pm25_non = pm25_hex.replace("0x", '')

                    if wind_speed_non == '00 00 00 00':
                        wind_speed = (1,)
                        lst_ws = list(wind_speed)
                        lst_ws[0] = 0.00
                        wind_speed = tuple(lst_ws)
                    else:
                        wind_speed = struct.unpack('<f', binascii.unhexlify(wind_speed_non.replace(' ', '')))

                    # IEEE754 Format Conversion.
                    temp = struct.unpack('<f', binascii.unhexlify(temp_non.replace(' ', '')))
                    humid = struct.unpack('<f', binascii.unhexlify(humid_non.replace(' ', '')))
                    pressure = struct.unpack('<f', binascii.unhexlify(pressure_non.replace(' ', '')))
                    pm25 = struct.unpack('<f', binascii.unhexlify(pm25_non.replace(' ', '')))

                    # Access Virtual-Machine Ubuntu IP and PORT.
                    client = InfluxDBClient("192.168.85.129", 8086)
                    # Use Database named 'AWS'
                    client.switch_database("AWS")
                    # Inserts Database's tags and field values.
                    points = [
                        {"measurement": "test1",
                         "tags": {"name": "OJJ"},
                         "fields": {"wind_direction": float(int(binascii.hexlify(res[5:7]), 16)),
                                    "wind_speed": float(wind_speed[0]), "temp": round(temp[0], 2),
                                    "humid": round(humid[0], 2), "pressure": round(pressure[0], 2),
                                    "pm25": round(pm25[0], 2)},
                         "time": time.time_ns()}
                    ]
                    client.write_points(points=points, protocol="json")
                    time.sleep(1)
                    self.ser.close()

            except Exception as e:
                self.ser.close()
                pass

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.run_flag = False
        self.wait()
