# JS-08
The successor of JS-06. The design goal of JS-08 is to provide higher spatial resolution for each azimuthal direction and support various operating systems and platforms, including IoT platforms.

## Key Features
- Measure visibility on each cardinal and ordinal section.
- Report the directional visibility and prevailing visibility.

## Supported Flatforms
JS-08 supports Windows 10 and Ubuntu 18.04 on usual personal computer platforms, including the following IoT platforms:
- [Raspberry PI Model B with 8MB RAM](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/)
- [NVIDIA Jetson Nano](https://developer.nvidia.com/embedded/jetson-nano-developer-kit)
- [NVIDIA Xavier NX](https://developer.nvidia.com/embedded/jetson-xavier-nx-devkit)

## Supported Cameras
- IP cameras
  - [Hanwha PNM-9030V](https://www.hanwha-security.com/en/products/camera/network/multi-sensor/PNM-9030V/overview/)
  - [Hanwha PNM-9022V](https://www.hanwha-security.com/en/products/camera/network/multi-sensor/PNM-9022V/overview/)
  - [Hanwha XNO-8080R](https://www.hanwha-security.com/en/products/camera/network/bullet/XNO-8080R/overview/)

## Setting Up Development Environment
- Visual Studio Code with the end of line sequence to **LF**. You can set git to resolve the issue automatically:
### Windows
```bash
  git config --global core.autocrlf true
```
### Linux and MacOS
```bash
  git config --global core.autocrlf input
```

## Setting Up Execution Environment
### Python Packages
#### Windows 10
We recommend using Anaconda Python distribution for the Windows environment.
- Anaconda Python 3.8 64-bit or later
- Required Python packages that can be installed using `conda`:
  - pyqt >= 5.9.2
  - pymongo >= 3.12.0

#### Ubuntu 18.04
You can install most of the prerequisites using Ubuntu package manager, apt.

### TensorFlow Lite
#### Windows 10
```shell
pip3 install --index-url https://google-coral.github.io/py-repo/ tflite_runtime
```

#### Ubuntu 18.04
If you're running Debian Linux or a derivative of Debian (including Raspberry Pi OS)
```bash
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install python3-tflite-runtime
```

### MongoDB
We recommend installing MongoDB with Docker. Please follow the description on the following link:
- https://hub.docker.com/_/mongo

### Video Codecs
#### Windows
For Windows, DirectShow filters are required to play RTSP video streams. Download one of the following filter packs:
- LAV Filter: https://github.com/Nevcairiel/LAVFilters/releases
- K-Lite:: https://files3.codecguide.com/K-Lite_Codec_Pack_1625_Basic.exe

#### Ubuntu 18.04  
For Linux, install GStreamer: 
```bash
sudo apt install gstreamer1.0-libav ubuntu-restricted-extras
```
