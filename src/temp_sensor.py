#!/usr/bin/env python3
#
# Output the temperature and humidity sensor using SHT 10.
# This code works on RPi. If you want to execute this script on Jetson,
# change the import line:
# import Jetson.GPIO as GPIO
#
# This code is based on the following references:
# https://pypi.org/project/Pi-Sht1x/1.0.8/
#
# required packages: python3-pi-sht1x
#
# TODO: For repeated output of sensor values, apply 'while' loop.
# TODO: Check the module, pi_sht1x for Jetson
#

from time import sleep
from pi_sht1x import SHT1x
import RPi.GPIO as GPIO


def main(data_pin: int, clock_pin: int):
    """Output temperature and humidity values via SHT 10.
    
    :param data_pin: SHT 10 sensor data pin number.
    :param clock_pin: SHT 10 sensor clock pin number.
    
    """
    with SHT1x(data_pin, clock_pin, gpio_mode=GPIO.BCM) as sensor:
        for i in range(5):
            # Repeat the temperature and humidity sensor values five times.
            temp = sensor.read_temperature()
            humidity = sensor.read_humidity(temp)
            sensor.calculate_dew_point(temp, humidity)
            print(sensor)
            sleep(2)
    print('Test complete.')


if __name__ == "__main__":
    # Raspberry Pi pin number to associate with the Clock, Data  pin.
    DATA_PIN = 18
    SCK_PIN = 23

    main(DATA_PIN, SCK_PIN)
