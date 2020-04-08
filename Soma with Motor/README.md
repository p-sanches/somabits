# Arduino Uno Wifi MDSN Test

This is the example for sending MDNS messages for service discovery from an Arduino Wifi Rev2 to another device which has Bonjour (MacOS, Windows) or Avahi (Linux) installed.


First install "WiFiNINA" which is a Wifi library for Arduino Wifi Rev2 using Library Manager <b>(Tools > Manage Libraries…)</b>. Download the ArduinoMDSN code (https://github.com/arduino-libraries/ArduinoMDNS) to Arduino's library folder.

To be able to compile the code for the Arduino Wifi Rev2, you should go to the folder, where files for the Arduino Wifi Rev2 board are located. 

In Ubuntu, e.g., 
`/home/martina/.arduino15/packages/arduino/hardware/megaavr/1.6.25/cores/arduino/api`

In Windows, e.g.,
c:\Users\<<User_Name>>\AppData\Local\Arduino15\packages\arduino\hardware\megaavr\1.8.5\cores\arduino\api\

In the `Udp.h` file, add the following line

```
virtual uint8_t beginMulticast(IPAddress, uint16_t) { return 0; }  // initialize, start listening on specified multicast IP address and port. Returns 1 if successful, 0 on failure
```

The code, thus, looks like:

```
public:
  virtual uint8_t begin(uint16_t) =0;   // initialize, start listening on specified port. Returns 1 if successful, 0 if there are no sockets available to use
  virtual uint8_t beginMulticast(IPAddress, uint16_t) { return 0; }  // initialize, start listening on specified multicast IP address and port. Returns 1 if successful, 0 on failure
  virtual void stop() =0;  // Finish with the UDP socket
  ...
```

The project should compile now without errors.
Do not forget to create the arduino_sectrets.h with your credentials. It looks as follows:

```
#define SECRET_SSID "MySSID"
#define SECRET_PASS "MyPassword"
```

However, if you use the TXT record to transmit additional information like OSC paths, the packets become <b>malicious</b>. To fix this, go to `MDNS.cpp` in the ArduinoMDSN code in the function `MDNSError_t MDNS::_sendMDNSMessage(...)` and look for the line `int slen = strlen((char*)this->_serviceRecords[serviceRecord]->textContent)`. This line and the following have to look like:
```
int slen = strlen((char*) this->_serviceRecords[serviceRecord]->textContent);
if (slen > 0) {
	slen -= 1;
}
*((uint16_t*) buf) = ethutil_htons(slen);
```

Now you are done :)
