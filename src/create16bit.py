#!/usr/bin/env python3
# To do: Capture the image from the RPi camera module and convert it to 16bits.
# required packages: python3-png, python3-pickle
#

# 'pickle' module can dataize images.

import picamera
import picamera.array
import numpy as np
import png
import pickle

def main():
    print("Capturing image...")
    with picamera.PiCamera() as camera:
        with picamera.array.PiBayerArray(camera) as stream:
            camera.capture(stream, 'jpeg', bayer=True)
            # Write to demosaic data and raw image
            rawimg = stream.demosaic()

    print("Saving 16-bit PNG...")
    with open('16bit.png', 'wb') as outfile:
        writer = png.Writer(width=rawimg.shape[1],
                            height=rawimg.shape[0],
                            bitdepth=16, greyscale=False)
        # rawimg is a (w, h, 3) RGB uint16 array
        # but PyPNG needs a (w, h*3) array
        png_data = np.reshape(rawimg, (-1, rawimg.shape[1]*3))
        # Scale 10 bit data to 16 bit values (else it will appear black)
        # Depending on your images and settings, it might still apeear dark.
        png_data *= int(2**6)
        writer.write(outfile, png_data)
    print("Save to pickle file..")
    with open('list.txt', 'wb') as pk:
        pickle.dump(png_data, pk)
    with open('list.txt', 'rb') as pk:
        data = pickle.load(pk)
    print("Finish")

   
if __name__ == '__main__':
    main()
