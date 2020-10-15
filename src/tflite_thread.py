#!/usr/bin/env python3
"""
Observate Visibility using TF Lite version of JS-02 model with the Hanhwa camera image.

This code is based on the
https://github.com/tensorflow/examples/tree/master/lite/examples/image_classification/raspberry_pi

Usage example:
python3 js02_lamp.py --model andrew_1583797361.tflite

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cv2
import argparse
import io
import time

import numpy as np

import tflite_runtime.interpreter as tflite

from PyQt5 import QtWidgets, QtGui, QtCore

class TfliteThread(QtCore.QThread):
    update_oxlist_signal = QtCore.pyqtSignal(list)

    def __init__(self, crop_imagelist100: list = []):
        super().__init__()
        self.run_flag = False
        self.crop_imagelist100 = crop_imagelist100
        self.oxlist = []
        self.interpreter = tflite.Interpreter("andrew_20200910.tflite")
        self.interpreter.allocate_tensors()
    
    def __del__(self):
        self.wait()
    
    def set_input_tensor(self, interpreter, image):
        """Feed input to the model"""

        tensor_index = interpreter.get_input_details()[0]['index']
        input_tensor = interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = image

    def classify_image(self, interpreter, image):
        """Returns a sorted array of classification results."""

        self.set_input_tensor(interpreter, image)
        interpreter.invoke()
        output_details = interpreter.get_output_details()[0]
        output = np.squeeze(interpreter.get_tensor(output_details['index']))
        predict = np.argmax(output)
        return predict, output[predict]

    def run(self):
        """영상목표를 모델에 넣어 결과를 전송한다."""        
        while self.run_flag == True:
            epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            if self.crop_imagelist100:                
                for index, image in enumerate(self.crop_imagelist100): 
                    image = cv2.resize(image, dsize = (224, 224), interpolation = cv2.INTER_LINEAR)                    
                    _, height, width, _ = self.interpreter.get_input_details()[0]['shape']
                    label_id, prob = self.classify_image(self.interpreter, image)
                    self.oxlist.append(label_id)
                self.update_oxlist_signal.emit(self.oxlist)
                self.oxlist = []                
    
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.run_flag = False        
        self.terminate()