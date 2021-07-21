# !/usr/bin/env python3
#
# Copyright 2020-21 Sijung Co., Ltd.
# Authors:
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cv2
import io
import time
import numpy as np

import tflite_runtime.interpreter as tflite
from PyQt5.QtCore import QThread, pyqtSignal


class TfliteThread(QThread):
    update_oxlist_signal = pyqtSignal(list)

    def __init__(self, crop_imagelist100=None):
        super().__init__()
        if crop_imagelist100 is None:
            crop_imagelist100 = []
        self.run_flag = False
        self.crop_imagelist100 = crop_imagelist100
        self.oxlist = []
        self.interpreter = tflite.Interpreter("Model/JS06N21011201.tflite")
        self.interpreter.allocate_tensors()
    # end of __init__

    def __del__(self):
        self.wait()

    def set_input_tensor(self, interpreter, image):
        """Feed input to the model"""

        tensor_index = interpreter.get_input_details()[0]['index']
        input_tensor = interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = image
    # end of set_input_tensor

    def classify_image(self, interpreter, image):
        """Returns a sorted array of classification results."""

        self.set_input_tensor(interpreter, image)
        interpreter.invoke()
        output_details = interpreter.get_output_details()[0]
        output = np.squeeze(interpreter.get_tensor(output_details['index']))
        predict = np.argmax(output)
        return predict, output[predict]
    # end of classify_image

    def run(self):
        """영상목표를 모델에 넣어 결과를 전송한다."""
        while self.run_flag:
            if self.crop_imagelist100:
                for index, image in enumerate(self.crop_imagelist100):
                    image = cv2.resize(image, dsize=(224, 224), interpolation=cv2.INTER_LINEAR)
                    _, height, width, _ = self.interpreter.get_input_details()[0]['shape']
                    label_id, prob = self.classify_image(self.interpreter, image)
                    self.oxlist.append(label_id)
                self.update_oxlist_signal.emit(self.oxlist)
                self.oxlist = []

        if self.run_flag is False:
            print("flag is False.\nPlease shut this program.")
            self.stop()
    # end of run

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.run_flag = False
        self.terminate()
    # end of stop


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = TfliteThread()
    window.run()
    sys.exit(app.exec_())
# end of tflite_thread.py
