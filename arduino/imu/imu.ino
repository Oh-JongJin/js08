/* 
 * Arduino LSM6DS3 - Gyroscope
 * 
 * This sketch reads the acceleration and gyroscope values from the LSM6DS3
 * sensor and continuously sends them to serial port.
 *
 * The circuit:
 * - Arduino Nano 33 IoT
 * 
 * TODO
 * - Magnetometer is required for a heading reference.
 * - The measured values should be send to I2C or SPI.
*/

#include <Arduino_LSM6DS3.h>

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");

    while (1);
  }

  Serial.print("Accelerometer sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println(" Hz");
  Serial.println("Acceleration in G's");

  Serial.print("Gyroscope sample rate = ");
  Serial.print(IMU.gyroscopeSampleRate());
  Serial.println(" Hz");
  Serial.println("Gyroscope in degrees/second");

  Serial.println("x\ty\tz\tox\toy\toz");
}

void loop() {
  float x, y, z;

  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
    Serial.print(x);
    Serial.print('\t');
    Serial.print(y);
    Serial.print('\t');
    Serial.println(z);
    Serial.print('\t');
  }

  float ox, oy, oz;
    if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(ox, oy, oz);

    Serial.print(ox);
    Serial.print('\t');
    Serial.print(oy);
    Serial.print('\t');
    Serial.println(oz);
    Serial.print('\t');
    }
}
