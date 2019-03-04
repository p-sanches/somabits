# Arduino Uno Wifi OSC Client
This is the example for sending IMU (accelerometer) values to server at address "/acc" and recieve message from server at address "/led" to turn on/off the built-in LED of the Arduino


Use the OSC library from Adrian Freed (version 1.3.5), which is available in the library manager of Arduino. 
In this library, open the file `SLIPEncodedSerial.h` and uncomment line 11: `#include <HardwareSerial.h>`.

Do not forget to create the arduino_sectrets.h with your credentials. It looks as follows:

```
#define SECRET_SSID "MySSID"
#define SECRET_PASS "MyPassword"
``` 

Find and install the SparkFun LSM6DS3 Breakout by SparkFun Electronics library using Library Manager (Tools > Manage Libraries…)
