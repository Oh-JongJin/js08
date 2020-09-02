#!/usr/bin/env/python3
#
# Saved in database and output weather sensor values through Serial communications.
#
# required packages: python3-serial, python3-binascii, python3-struct, python3-influxdb
#
# TODO(Jongjin): Weather Sensor value parsing Error processing necessary.
#

import serial
import time
import binascii
import struct
import sys
from influxdb import InfluxDBClient


def serial_test():
    """The connected weather sensor outputs six values.

    Wind direction, Wind Speed, Temperature, Humidity, AirPressure, Pm2.5

    Wind direction is located in fifth and sixth places and is expressed in hexadecimal numbers.
    The rest of them are all 32 bit float date in this protocol comply to IEEE754 Standard.
    """
    global i
    try:
        # Send requests for Weather sensors
        write_aws = b'\x01\x03\x00\x00\x00\x29\x84\x14'
        # BAUD=9600, DATABIT=8, PARITY=EVEN, STOPBIT=1, TIMEOUT=1, PORT=COM9
        ser = serial.Serial(port="COM9", baudrate=9600, parity=serial.PARITY_EVEN,
                            stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,
                            timeout=1)
        if ser.readable():
            ser.write(write_aws)
            res = ser.readline()
            wind_direction = int(binascii.hexlify(res[5:7]), 16)
            print(f"\nWind direction: {wind_direction}°")

            # Weather sensor value parsing, replace processing
            wind_speed_hex = f"{hex(res[8]) + ' ' + hex(res[7]) + ' ' + hex(res[10]) + ' ' + hex(res[9])}".replace(
                "0x0 ", "0x00 ").replace("0x1 ", "0xA0 ").replace("0x2 ", "0xB0 ").replace("0x3 ", "0xC0 ").replace(
                "0x4 ", "0xD0 ").replace("0x5 ", "0xE0 ").replace("0xc ", "0xc0 ").replace("0x00 0x00 0x00 0x0", "0x00 0x00 0x00 0x00")
            temp_hex = f"{hex(res[12]) + ' ' + hex(res[11]) + ' ' + hex(res[14]) + ' ' + hex(res[13])}".replace(
                "0x0 ", "0x00 ").replace("0x1 ", "0xA0 ").replace("0x2 ", "0xB0 ").replace("0x3 ", "0xC0 ").replace(
                "0x4 ", "0xD0 ").replace("0x5 ", "0xE0 ").replace("0xc ", "0xc0 ").replace(" 0x0'", " 0x00'")
            humid_hex = f"{hex(res[16]) + ' ' + hex(res[15]) + ' ' + hex(res[18]) + ' ' + hex(res[17])}".replace(
                "0x0 ", "0x00 ").replace("0x1 ", "0xA0 ").replace("0x2 ", "0xB0 ").replace("0x3 ", "0xC0 ").replace(
                "0x4 ", "0xD0 ").replace("0x5 ", "0xE0 ").replace("0xc ", "0xc0 ").replace(" 0x0'", " 0x00'")
            pressure_hex = f"{hex(res[20]) + ' ' + hex(res[19]) + ' ' + hex(res[22]) + ' ' + hex(res[21])}".replace(
                "0x0 ", "0x00 ").replace("0x1 ", "0xA0 ").replace("0x2 ", "0xB0 ").replace("0x3 ", "0xC0 ").replace(
                "0x4 ", "0xD0 ").replace("0x5 ", "0xE0 ").replace("0xc ", "0xc0 ").replace(" 0x0'", " 0x00'")
            pm25_hex = f"{hex(res[54]) + ' ' + hex(res[53]) + ' ' + hex(res[56]) + ' ' + hex(res[55])}".replace(
                "0x0 ", "0x00 ").replace("0x1 ", "0xA0 ").replace("0x2 ", "0xB0 ").replace("0x3 ", "0xC0 ").replace(
                "0x4 ", "0xD0 ").replace("0x5 ", "0xE0 ").replace("0xc ", "0xc0 ").replace("0x00 0x00 0x00 0x0", "0x00 0x00 0x00 0x00")

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
            print(f"Wind Speed: {round(wind_speed[0], 2)} m/s \nTemperature: {round(temp[0], 2)} °C"
                  f"\nAtmospheric Pressure: {round(pressure[0], 2)} hPa \nHumidity: {round(humid[0], 2)} %"
                  f"\nPM2.5: {round(pm25[0], 2)} ug/m3")

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
            print("- Save complete at InfluxDB")

            time.sleep(3)

    except Exception as e:
        print("Error code: ", e)
        # if error occurs, variable i is increase.
        i += 1
        print(f"Error count -> {i}")
        pass


if __name__ == "__main__":
    print("start!")
    i = 0
    while True:
        serial_test()
