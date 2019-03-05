# Arduino Uno Wifi OSC Client
This is the example for sending build-in IMU (accelerometer) values of Arduino Wifi Rev2 to server at address <b>"/acc"</b> over OSC and recieve message from server at address <b>"/led"</b> to turn on/off the built-in LED of the Arduino Wifi Rev2.


First install "WiFiNINA" which is a Wifi library for Arduino Wifi Rev2 using Library Manager <b>(Tools > Manage Libraries…)</b>. Use the OSC library from Adrian Freed (version 1.3.5), which is available in the library manager of Arduino. 
In this library, open the file `SLIPEncodedSerial.h` and uncomment line 11: `#include <HardwareSerial.h>`.

Do not forget to create the arduino_sectrets.h with your credentials. It looks as follows:

```
#define SECRET_SSID "MySSID"
#define SECRET_PASS "MyPassword"
``` 

You also need to find and install the <b>SparkFun LSM6DS3 Breakout by SparkFun Electronics</b> library using Library Manager
