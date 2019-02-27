# Arduino Uno Wifi OSC Client

Use the OSC library from Adrian Freed (version 1.3.5), which is available in the library manager of Arduino. 
In this library, open the file `SLIPEncodedSerial.h` and uncomment line 11: `#include <HardwareSerial.h>`.

Do not forget to create the arduino_sectrets.h with your credentials. It looks as follows:

```
#define SECRET_SSID "MySSID"
#define SECRET_PASS "MyPassword"
``` 