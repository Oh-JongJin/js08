# js06-iot
The successor of JS-02. The goal of JS-06 is improved surveillance, sensor integration with integrated user experience compared to JS-02. This code is for an IoT platform, i.e., NVIDIA Jetson, Raspberry Pi, etc.

## Key Features
- Estimate of the concentration of particular matter based on a camera image
- Estimate of visibility based on the extinction ratio of the atmosphere
- Estimate of visibility based on visible targets on a camera image
- Acquisition of weather data from attached sensors.

## Hardware Flatforms
JS-06 is being developed on the following target platforms.
- [Raspberry PI Model B with 8MB RAM](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/)
- [NVIDIA Jetson Nano](https://developer.nvidia.com/embedded/jetson-nano-developer-kit)
- [NVIDIA Xavier NX](https://developer.nvidia.com/embedded/jetson-xavier-nx-devkit)

## Camera Supports
- [Pi Camera Module V2.1](https://www.raspberrypi.org/products/camera-module-v2/)
- [Pi NoIR Camera Module V2.1](https://www.raspberrypi.org/products/pi-noir-camera-v2/)
- IP cameras
  - [Hanwha PNM-9030V](https://www.hanwha-security.com/en/products/camera/network/multi-sensor/PNM-9030V/overview/)
  - [Hanwha XNO-8080R](https://www.hanwha-security.com/en/products/camera/network/bullet/XNO-8080R/overview/)
- Webcams

## Development Environment
- Visual Studio Code with theend of line sequence to **LF**.
- Anaconda Python 3.7 64-bit or less
- Required Python packages that can be installed using `conda`:
  - binascii
  - os
  - serial
  - struct
  - sys
  - OpenCV
  - NumPy
  - Pandas
  - PyQt5
- Required Python packages that can be installed using `pip`:
  - TensorFlow Lite interpreter: https://www.tensorflow.org/lite/guide/python
