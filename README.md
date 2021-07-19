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

## Setting Up Development Environment
- Visual Studio Code with the end of line sequence to **LF**. You can set git to resolve the issue automatically:
  - Windows
```bash
  git config --global core.autocrlf true
  ```
  - Linux and MacOS
```bash
  git config --global core.autocrlf input
  ```
  
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
  - InfluxDB
  
- To execute TensorFlow Lite models with Python, TensorFlow Lite interpreter is required to execute TensorFlow Lite models:
  - If you're running Debian Linux or a derivative of Debian (including Raspberry Pi OS)
```bash
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install python3-tflite-runtime
```
  - For all other systems:
```shell
pip3 install --index-url https://google-coral.github.io/py-repo/ tflite_runtime
```

- Video Codecs
  - For Windows, DirectShow filters are required to play RTSP video streams. Download the one of the following filter packs:
    - LAV Filter: https://github.com/Nevcairiel/LAVFilters/releases
    - K-Lite:: https://files3.codecguide.com/K-Lite_Codec_Pack_1625_Basic.exe

  - For Linux, install GStreamer: 
    ```bash
    sudo apt install gstreamer1.0-libav ubuntu-restricted-extras
    ```

- Install InfluxDB and Grafana
  - For Windows
    - InfluxDB: https://dl.influxdata.com/influxdb/releases/influxdb-1.8.6_windows_amd64.zip
    - Grafana: https://dl.grafana.com/oss/release/grafana-8.0.2.windows-amd64.msi

  - For Linux
    - InfluxDB: 
  ```bash
  sudo apt-get update && sudo apt-get install influxdb influxdb-client python3-influxdb
  ```
  
    - Grafana:
  ```bash
  sudo apt-get install -y adduser libfontconfig1
  wget https://dl.grafana.com/oss/release/grafana_8.0.4_amd64.deb
  sudo dpkg -i grafana_8.0.4_amd64.deb
  ```

  Configure the InfluxDB, Grafana server to start at boot:
  ```bash
  sudo service influxdb start
  sudo service grafana-server start
  ```
  
