#!/usr/bin/env python3

import RPi.GPIO as gp
import argparse
import os
import time

gp.setmode(gp.BOARD)

SEL = 7
EN1 = 11
EN2 = 12

# gp.setup(15, gp.OUT)
# gp.setup(16, gp.OUT)
# gp.setup(21, gp.OUT)
# gp.setup(22, gp.OUT)
# 
# gp.output(11, True)
# gp.output(12, True)
# gp.output(15, True)
# gp.output(16, True)
# gp.output(21, True)
# gp.output(22, True)


def capture(cam: int, filename: str):
    """Take a picture from a specified camera
    
    """
    cmd = f"raspistill -hf -vf -e png -o {filename}.png"
    
    if cam == 1:
        i2c = "i2cset -y 1 0x70 0x00 0x04"
        gp.output(SEL, False)
        gp.output(EN1, False)
        gp.output(EN2, True)
    elif cam == 2:
        i2c = "i2cset -y 1 0x70 0x00 0x05"
        gp.output(SEL, True)
        gp.output(EN1, False)
        gp.output(EN2, True)
    elif cam == 3:
        i2c = "i2cset -y 1 0x70 0x00 0x06"
        gp.output(SEL, False)
        gp.output(EN1, True)
        gp.output(EN2, False)
    elif cam == 4:
        i2c = "i2cset -y 1 0x70 0x00 0x07"
        gp.output(7, True)
        gp.output(11, True)
        gp.output(12, False)
    else:
        raise ValueError("cam should be <= 4")

    os.system(i2c)
    os.system(cmd)

def init_gpio():
    gp.setup(SEL, gp.OUT)
    gp.setup(EN1, gp.OUT)
    gp.setup(EN2, gp.OUT)

def restore_gpio():
    gp.output(SEL, False)
    gp.output(EN1, False)
    gp.output(EN2, False)


def main(args: argparse.Namespace):
    if not args.q:
        gp.setwarnings(False)

    if args.v:
        print("Initialize GPIO pins")
    init_gpio()

    epoch = str(int(time.time()))
    if args.v:
        print("Take a photo using the NO-IR camera.")
    capture(2, epoch + "_v2") 
    if args.v:
        print("Take a photo using the NO-IR camera.")
    capture(4, epoch + "_noir") 


    if args.v:
        print("Restore GPIO pins")
    restore_gpio()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="take a picture.")
    parser.add_argument("-v", action="store_true", 
                        help="increase output verbosity")
    parser.add_argument("-q", action="store_true",
                        help="supress warning")
    args = parser.parse_args()
    main(args)

