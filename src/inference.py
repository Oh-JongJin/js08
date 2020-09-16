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

import argparse
import io
import time

import numpy as np
import tflite_runtime.interpreter as tflite


def set_input_tensor(interpreter, image):
    """Feed input to the model"""

    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = image


def classify_image(interpreter, image):
    """Returns a sorted array of classification results."""

    set_input_tensor(interpreter, image)
    interpreter.invoke()
    output_details = interpreter.get_output_details()[0]
    output = np.squeeze(interpreter.get_tensor(output_details['index']))
    # print(output)
    predict = np.argmax(output)
    return predict, output[predict]

def readmodel():
    "tflite 모델을 읽어온다."
    interpreter = tflite.Interpreter("test20200910_01.tflite")
    return interpreter

def inference(image: np.ndarray):
    'ndarray에 저장된 영상에대해 영상 식별을 수행한다.'
    interpreter = readmodel()
    interpreter.allocate_tensors()
    _, height, width, _ = interpreter.get_input_details()[0]['shape']

    # input_data = image.reshape((1, width, height, 3))

    label_id, prob = classify_image(interpreter, image)
    return int(label_id)

def main():
    """Main procedure"""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m', '--model',
                        help='File path of .tflite file.',
                        required=True)
    args = parser.parse_args(['-m', 'andrew_1583797361.tflite'])

    interpreter = tflite.Interpreter(args.model)
    interpreter.allocate_tensors()
    _, height, width, _ = interpreter.get_input_details()[0]['shape']    

    label = ['fog', 'clear']
    with picamera.PiCamera(resolution=(640, 480), framerate=30) as camera:
        camera.rotation = 180
        camera.start_preview()
        try:
            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream,
                                               format='jpeg',
                                               use_video_port=True):
                stream.seek(0)
                input_image = Image.open(stream).convert('RGB')
                input_image = input_image.resize((width, height), Image.ANTIALIAS)
                input_data = np.array(input_image, dtype=np.float32) / 255
                input_data = input_data.reshape((1, width, height, 3))

                # input_image.save("rpi_cam.jpg", "JPEG")
                # np.save('rpi_cam.npy', input_data)
                start_time = time.time()
                label_id, prob = classify_image(interpreter, input_data)
                elapsed_ms = (time.time() - start_time) * 1000

                stream.seek(0)
                stream.truncate()
                camera.annotate_text = '%s %.2f\n%.1fms' % (label[label_id],
                                                            prob, elapsed_ms)
        finally:
            camera.stop_preview()


if __name__ == '__main__':
    main()
