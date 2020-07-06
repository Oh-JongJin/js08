#!/usr/bin/env python3
#
# Capture 10bit image from the RPi camera module V2 and save it to 16bits PNG.
#
# This code is based on the following references:
# https://techoverflow.net/2019/11/21/how-to-save-raspberry-pi-raw-10-bit-image-as-16-bit-png-using-pypng/
# https://picamera.readthedocs.io/en/release-1.13/recipes2.html#raw-bayer-data-captures
#
# required packages: python3-png, python3-pickle
#
# TODO: The capturing process should be provided as a function.
#

import picamera
import picamera.array

import numpy as np
import png
import time

def fix_cam_attr(camera:picamera.camera.PiCamera, iso:int=300):
    """Set and fix flim speed of camera module.

    Args:
      iso: film speed, allowed values are 100, 200, 320, 400, 500, 640, 800.

    The detailed setup refers to:
    https://picamera.readthedocs.io/en/release-1.13/recipes1.html#capturing-consistent-images

    """
    camera.iso = iso
    # Wait for the automatic gain control to settle
    time.sleep(2)
    # Now fix the values
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g

def main():
    print("Capturing raw Bayer data...")
    with picamera.PiCamera() as camera:
        fix_cam_attr(camera, iso=800)

        with picamera.array.PiBayerArray(camera) as stream:
            camera.capture(stream, 'jpeg', bayer=True)
            # Write to demosaic data and raw image
            rawimg = stream.demosaic().astype(np.uint16)

    print("Saving to 48(16*3)-bit png...")
    filename = str(int(time.time())) + '.png'
    with open(filename, 'wb') as outfile:
        writer = png.Writer(width=rawimg.shape[1],
                            height=rawimg.shape[0],
                            bitdepth=16, greyscale=False)
        # rawimg is a (w, h, 3) RGB uint16 array
        # but PyPNG needs a (w, h*3) array
        png_data = np.reshape(rawimg, (-1, rawimg.shape[1] * 3))
        png_data *= int(2**6)
        writer.write(outfile, png_data)

if __name__ == '__main__':
    main()
