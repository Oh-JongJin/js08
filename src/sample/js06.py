#!/usr/bin/env python3
# 
# A sample implementation of a main window for JS-06
#
# required packages: python3-serial, python3-binascii, python3-struct, python3-threading, python3-influxdb
# required program: InfluxDB Server(VMware-Ubuntu)
# This example illustrates the following techniques:
# * Layout design using Qt Designer
# * Open an image file
# * Open RTSP video source
# *
# Reference: https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1

import sys
import serial
import time
import binascii
import struct
import cv2
import numpy as np

from PyQt5 import QtWidgets, QtGui, QtCore
from influxdb import InfluxDBClient
from main_window import Ui_MainWindow
# from plot import Ui_PlotWindow


class AWSThread(QtCore.QThread):
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
                    wind_direction = int(binascii.hexlify(res[5:7]), 16)
                    # print(f"\nWind direction: {wind_direction}°")

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
                    # print(f"Wind Speed: {round(wind_speed[0], 2)} m/s \nTemperature: {round(temp[0], 2)} °C"
                    #       f"\nAtmospheric Pressure: {round(pressure[0], 2)} hPa \nHumidity: {round(humid[0], 2)} %"
                    #       f"\nPM2.5: {round(pm25[0], 2)} ug/m3")

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
                    # print("- Save complete at InfluxDB")
                    time.sleep(1)
                    self.ser.close()

            # except (TypeError, IndexError, binascii.Error) as e:
            #     self.ser.close()
            #     pass
            except Exception as e:
                self.ser.close()
                pass

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.run_flag = False
        self.wait()


class PolarThread(QtCore.QThread):
    def __init__(self):
        super().__init__()



class VideoThread(QtCore.QThread):
    update_pixmap_signal = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, src: str = 0):
        super().__init__()
        self._run_flag = True
        self.src = src
        self.img_width = 0
        self.img_height = 0

    def run(self):

        cap = cv2.VideoCapture(self.src)

        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.update_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class Js06MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.video_thread = None
        self.aws_thread = AWSThread()

    def setupUi(self, MainWindow: QtWidgets.QMainWindow):
        super().setupUi(MainWindow)

        self.actionImage_File.triggered.connect(self.open_img_file_clicked)
        self.actionCamera_1.triggered.connect(self.open_cam1_clicked)
        self.actionCamera_2.triggered.connect(self.open_cam2_clicked)
        self.actionCamera_3.triggered.connect(self.open_cam3_clicked)
        self.actionON.triggered.connect(self.aws_clicked)
        self.actionPolar_Plot.triggered.connect(self.polar_clicked)

    def closeEvent(self, event):
        print("DEBUG: ", type(event))
        if self.video_thread is not None:
            self.video_thread.stop()
        event.accept()

    def open_img_file_clicked(self):
        if self.video_thread is not None:
            self.video_thread.stop()

        fname = QtWidgets.QFileDialog.getOpenFileName()[0]
        if fname != '':
            cv_img = cv2.imread(fname)
            # convert the image to Qt format
            qt_img = self.convert_cv_qt(cv_img)
            # display it
            self.image_label.setPixmap(qt_img)

    def open_cam1_clicked(self):
        """Connect to webcam"""
        if self.video_thread is not None:
            self.video_thread.stop()

        # create the video capture thread
        self.video_thread = VideoThread(0)
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()

    def open_cam2_clicked(self):
        """Get video from Hanwha PNM-9030V"""
        if self.video_thread is not None:
            self.video_thread.stop()

        # create the video capture thread
        self.video_thread = VideoThread('rtsp://admin:sijung5520@192.168.100.121/profile2/media.smp')
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()

    def open_cam3_clicked(self):
        """Get video from Hanwha XNO-8080R"""
        if self.video_thread is not None:
            self.video_thread.stop()

        # create the video capture thread
        self.video_thread = VideoThread('rtsp://admin:G85^mdPzCXr2@192.168.100.115/profile2/media.smp')
        # connect its signal to the update_image slot
        self.video_thread.update_pixmap_signal.connect(self.update_image)
        # start the thread
        self.video_thread.start()

    def aws_clicked(self):
        """Start saving AWS sensor value at InfluxDB"""

        if self.actionON.isChecked():   # True
            if not self.aws_thread.run_flag:
                print("AWS Thread Start.")
                self.aws_thread.run_flag = True
                self.aws_thread.start()

        elif not self.actionON.isChecked():     # False
            if self.aws_thread.run_flag:
                print("AWS Thread Stop")
                self.aws_thread.run_flag = False

    def polar_clicked(self):
        """Print Polar Plot"""
        self.plt_window = PolarPlotWindow()
        self.plt_window.setupUI(MainWindow)
        MainWindow.show()

    @QtCore.pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        # width, height = (w // 4, h // 4) if w > 1920 else (w, h)
        display_width, display_height = w // 4, h // 4
        p = convert_to_Qt_format.scaled(display_width, display_height, QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Js06MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
