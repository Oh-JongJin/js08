"""Evaluate the discrimination model and generate a report.

usage: inference.py [-h] -i INPUT -m MODEL

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path of image files
  -m MODEL, --model MODEL
                        name of model file

Sijung Corp. Ltd. 2020
"""

#
# The coding style follows the suggestion of
# pylint --enable=F,E,W,C,R --extension-pkg-whitelist=cv2 inference.py
#

# from __future__ import absolute_import

import argparse
import os
import time
from typing import List

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.backend as K
import tensorflow_hub as hub
IMG_SIZE = 224

def decode_img(img: tf.Tensor) -> tf.Tensor:
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])
    img = tf.clip_by_value(img, 0, 1)
    return img

def process_path(file_path: tf.Tensor) -> tf.Tensor:
    # load the raw data from the file as a string
    img = tf.io.read_file(file_path)
    img = decode_img(img)
    return img

def inference(model: tf.Tensor, img_path: str) -> List[int]:    
    """Determine discriminability of given images.

    The return sequense follows the alphanumeric order of file name of 
    input images.

    @params:
        model_path: path to the TF model in hdf5 format
        img_path: directory of images to be determined

    @return:
        list of 1 and 0. 1 for discriminable.
    """  
    num_img = len(os.listdir(img_path))
    img_list_ds = tf.data.Dataset.list_files(os.path.join(img_path, '*'), 
                                             shuffle=False)
    img_ds = img_list_ds.map(process_path)
    image_batch = img_ds.batch(num_img)
    
    # Load .h5 model
    # model = keras.models.load_model(
    #     model_path,
    #     custom_objects={'KerasLayer': hub.KerasLayer},
    #     compile=False)

    # Load .pb directory
    # keras session delete
    K.clear_session()
    # model = keras.models.load_model(model_path, compile=False)
    predict = model.predict(image_batch)
    result = np.argmax(predict, axis=-1)    
    return result

def main():
    """Main procedure
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="path of image files")
    parser.add_argument("-m", "--model", type=str, required=True,
                        help="name of model file")
    args = parser.parse_args()
    # args = parser.parse_args(r"-m C:\Users\ruddy\source\repos\ruddyscent\js-02\tool\1582679839.h5  -i C:\Users\ruddy\Workspace\test".split())
    # args = parser.parse_args(r"-m C:\Users\ruddy\source\repos\ruddyscent\js-02\tool\1582679839 -i C:\Users\ruddy\Workspace\test".split())

    discriminant = inference(args.model, args.input)
    print(' '.join(map(str, discriminant)))
    return

if __name__ == '__main__':
    main()
