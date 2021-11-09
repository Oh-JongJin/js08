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
Required Python packages that can be installed using `pip`:
  - python >= 3.8
  - PyQt5 >= 5.13
  - PyQtChart >= 5.13
  - pymongo >= 3.12.0
  - opencv-python >= 4.4.0
  - numpy
  - onnxruntime

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
Before execution of JS-08, you need an woring MongoDB. We recommend installing 
MongoDB with Docker. Please follow the description on the following link:
- https://hub.docker.com/_/mongo
You can create and execute a container with MongoDB:
```bash
docker run --name mongodb -d -p 27017:27017 mongo
```

### Video Codecs
#### Windows
For Windows, DirectShow filters are required to play RTSP video streams. Download one of the following filter packs:
- LAV filter: https://github.com/Nevcairiel/LAVFilters/releases

#### Ubuntu 18.04  
For Linux, install GStreamer: 
```bash
sudo apt install gstreamer1.0-libav ubuntu-restricted-extras
```

## Frequently Asked Questions
### Codec Missing
The following error occurs when the video codec is not installed correctly:
```
DirectShowPlayerService::doSetUrlSource: Unresolved error code 0x800c000d (?? ?? ???? ?????????? ??????????.)
```
Please, refer to the 'Video Codec' section, and install the appropriate codec in your environment.

### Missing Redistributable for Visual Studio 2019
The onnxruntime package for Windows, requires the Redistributable for Visual Studio;
```
ImportError: Microsoft Visual C++ Redistributable for Visual Studio 2019 not installed on the machine.
```
Please, download and install the required packages from:
https://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170


### JS-08 freezes after a few minutes after starting on Windows.
It is known that JS-08 with K-Lite Codec Pack crashes after a few minutes after 
starting on Windows 10. Please, use the LAV filter instead.