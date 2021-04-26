#!/usr/bin/env python3

import binascii
import serial
import struct
import time

from influxdb import InfluxDBClient, exceptions
from PyQt5.QtCore import QThread


class SaveDB(QThread):
    def __init__(self):
        super().__init__()
        self.flag = False
        self.write_aws = None
        self.ser = None

        # self.epoch = None
        # self.visibility = None
        # self.predict_visibility = None

        self.c_direction = None
        self.c_speed = None
        self.c_temp = None
        self.c_humid = None
        self.c_pressure = None
        self.c_visibility = None
        self.previous_visibility = None

    def run(self):
        while self.flag:
            try:
                self.write_aws = b'\x01\x03\x00\x00\x00\x29\x84\x14'
                self.ser = serial.Serial(port="COM4", baudrate=9600, parity=serial.PARITY_EVEN,
                                        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,
                                        timeout=1)
                if self.ser.readable():
                    self.ser.write(self.write_aws)
                    res = self.ser.readline()
                    result = binascii.b2a_hex(res)
                    result = result.decode()

                    # Weather sensor value parsing, replace processing
                    wind_speed_hex = f"{result[16:18] + ' ' + result[14:16] + ' ' + result[20:22] + ' ' + result[18:20]}".replace(
                        "0x0 ", "0x00 ").replace("0x1 ", "0x10 ").replace("0x2 ", "0x20 ").replace("0x3 ", "0x30 ").replace(
                        "0x4 ", "0x40 ").replace("0x5 ", "0x50 ").replace("0x6 ", "0x60 ").replace("0x7 ", "0x70 ") \
                        .replace("0x8 ", "0x80 ").replace("0x9 ", "0x90 ").replace("0xa ", "0xa0 ").replace("0xb ", "0xb0 ") \
                        .replace("0xc ", "0xc0 ").replace("0xd ", "0xd0 ").replace("0xe ", "0xe0 ").replace("0xf ", "0xF0 ") \
                        .replace("0x00 0x00 0x00 0x0", "0x00 0x00 0x00 0x00")
                    temp_hex = f"{result[24:26] + ' ' + result[22:24] + ' ' + result[28:30] + ' ' + result[26:28]}".replace(
                        "0x0 ", "0x00 ").replace("0x1 ", "0xA0 ").replace("0x2 ", "0xB0 ").replace("0x3 ",
                                                                                                   "0xC0 ").replace(
                        "0x4 ", "0x40 ").replace("0x5 ", "0x50 ").replace("0x6 ", "0x60 ").replace("0x7 ", "0x70 ") \
                        .replace("0x8 ", "0x80 ").replace("0x9 ", "0x90 ").replace("0xa ", "0xa0 ").replace("0xb ",
                                                                                                            "0xb0 ") \
                        .replace("0xc ", "0xc0 ").replace("0xd ", "0xd0 ").replace("0xe ", "0xe0 ").replace("0xf ",
                                                                                                            "0xF0 ")
                    humid_hex = f"{result[32:34] + ' ' + result[30:32] + ' ' + result[36:38] + ' ' + result[34:36]}".replace(
                        "0x0 ", "0x00 ").replace("0x1 ", "0xA0 ").replace("0x2 ", "0xB0 ").replace("0x3 ",
                                                                                                   "0xC0 ").replace(
                        "0x4 ", "0x40 ").replace("0x5 ", "0x50 ").replace("0x6 ", "0x60 ").replace("0x7 ", "0x70 ") \
                        .replace("0x8 ", "0x80 ").replace("0x9 ", "0x90 ").replace("0xa ", "0xa0 ").replace("0xb ",
                                                                                                            "0xb0 ") \
                        .replace("0xc ", "0xc0 ").replace("0xd ", "0xd0 ").replace("0xe ", "0xe0 ").replace("0xf ",
                                                                                                            "0xF0 ")
                    pressure_hex = f"{result[40:42]  + ' ' + result[38:40] + ' ' + result[44:46] + ' ' + result[42:44]}".replace(
                        "0x0 ", "0x00 ").replace("0x1 ", "0xA0 ").replace("0x2 ", "0xB0 ").replace("0x3 ",
                                                                                                   "0xC0 ").replace(
                        "0x4 ", "0x40 ").replace("0x5 ", "0x50 ").replace("0x6 ", "0x60 ").replace("0x7 ", "0x70 ") \
                        .replace("0x8 ", "0x80 ").replace("0x9 ", "0x90 ").replace("0xa ", "0xa0 ").replace("0xb ",
                                                                                                            "0xb0 ") \
                        .replace("0xc ", "0xc0 ").replace("0xd ", "0xd0 ").replace("0xe ", "0xe0 ").replace("0xf ",
                                                                                                            "0xF0 ")
                    pm25_hex = f"{result[108:110] + ' ' + result[106:108] + ' ' + result[112:114] + ' ' + result[110:112]}".replace(
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
                    # IEEE754 Format Conversion.
                    wind_speed = struct.unpack('<f', binascii.unhexlify(wind_speed_non.replace(' ', '')))
                    temp = struct.unpack('<f', binascii.unhexlify(temp_non.replace(' ', '')))
                    humid = struct.unpack('<f', binascii.unhexlify(humid_non.replace(' ', '')))
                    pressure = struct.unpack('<f', binascii.unhexlify(pressure_non.replace(' ', '')))
                    pm25 = struct.unpack('<f', binascii.unhexlify(pm25_non.replace(' ', '')))
                    # Convert Value
                    self.c_direction = float(int(binascii.hexlify(res[5:7]), 16))
                    self.c_speed = round(wind_speed[0], 1)
                    self.c_temp = round(temp[0], 1)
                    self.c_humid = round(humid[0], 1)
                    self.c_pressure = round(pressure[0], 1)

                    self.ser.close()

                # Optical Visibility
                self.write_aws = b'\x01\x03\x00\x00\x00\x02\xc4\x0b'
                self.ser = serial.Serial(port="COM6", baudrate=9600, parity=serial.PARITY_EVEN,
                                        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,
                                        timeout=1)
                if self.ser.readable():
                    self.ser.write(self.write_aws)
                    res = self.ser.readline()
                    result = binascii.b2a_hex(res)
                    result = result.decode()
                    self.c_visibility = int(result[6:10], 16)
                    # print(result)
                    # print(self.c_visibility)
                    if self.c_visibility == 10:
                        # self.c_visibility = self.previous_visibility
                        self.c_visibility = 1000

                client = InfluxDBClient('localhost', 8086)
                # epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                save_time = time.time_ns()

                client.create_database("Sijung")
                client.switch_database("Sijung")
                points = [{"measurement": "JS06",
                        "tags": {"name": "Sijung"},
                        "fields": {"vis": float(self.c_visibility),
                                   "temp": self.c_temp, "humid": self.c_humid, "direction": self.c_direction,
                                   "speed": self.c_speed, "pressure": self.c_pressure},
                        "time": save_time}]
                # self.previous_visibility = self.c_visibility
                # client.query(f'DELETE FROM predict WHERE time < {time.time_ns()}')
                client.write_points(points=points, protocol="json")
                client.close()

                time.sleep(60)

            except struct.error:
                self.ser.close()
                pass

            except serial.serialutil.SerialException:
                self.ser.close()
