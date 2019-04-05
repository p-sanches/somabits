/*

  This example connects to an encrypted Wifi network.
  Then it prints the  MAC address of the Wifi module,
  the IP address obtained, and other network details.

  created 13 July 2010
  by dlf (Metodo2 srl)
  modified 31 May 2012
  by Tom Igoe
*/
#include <SPI.h>
#include <WiFiNINA.h>
#include <WiFiUdp.h>
#include <ArduinoMDNS.h>
#include <OSCMessage.h>
#include <OSCBundle.h>
#include <OSCBoards.h>
#include "SparkFunLSM6DS3.h"
#include "Wire.h"

#include "arduino_secrets.h"
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;     // the Wifi radio's status

OSCErrorCode error;
unsigned int ledState = LOW;


// A UDP instance to let us send and receive packets over UDP
WiFiUDP Udp;

IPAddress server_ip(192, 168, 11, 103); //change it to your server IP address
const unsigned int server_port = 3333;
const unsigned int local_port = 3333;

LSM6DS3 myIMU(SPI_MODE, SPIIMU_SS); // SPI Chip Select

WiFiUDP udp;
MDNS mdns(udp);

void serviceFound(const char* type, MDNSServiceProtocol proto,
                  const char* name, IPAddress ip, unsigned short port,
                  const char* txtContent);


void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv < "1.0.0") {
    Serial.println("Please upgrade the firmware");
  }

  // attempt to connect to Wifi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }

  // you're connected now, so print out the data:
  Serial.print("You're connected to the network");
  printCurrentNet();
  printWifiData();

  mdns.begin(WiFi.localIP(), "arduino_2");
  uint8_t* s1 = "sensor1=/accelerometer:-1%2";

  char txt[100] = {'\0'};

  txt[0] = (uint8_t) strlen(s1);
  int txt_len = 1;
  for (uint8_t i = 0; i < strlen(s1); i++) {
    if (s1[i] != '\0'); {
      txt[txt_len] = s1[i];
      txt_len++;
    }
  }



  int success;
  success = mdns.addServiceRecord("Arduino with Accelerometer_1._osc",
                                  3333,
                                  MDNSServiceUDP,
                                  txt);

  if (success) {
    Serial.println("Successfully registered service");
  } else {
    Serial.println("Something went wrong while registering service");
  }

  Serial.println("\nStarting connection to server...");
  Udp.begin(local_port);

  myIMU.begin();
  pinMode(LED_BUILTIN, OUTPUT);

}


void led(OSCMessage &msg) {
  ledState = msg.getInt(0);
  digitalWrite(LED_BUILTIN, ledState);
  Serial.print("/led: ");
  Serial.println(ledState);
}


void loop() {
  mdns.run();
  OSCMessage send_msg("/accelerometer");
  OSCMessage recieve_msg("/accelerometer");


  Serial.print("Sending packet to ");
  Serial.print(server_ip);
  Serial.print(":");
  Serial.println(server_port);


  send_msg.add(myIMU.readFloatAccelX());
  Serial.print(myIMU.readFloatAccelX());

  Udp.beginPacket(server_ip, server_port);
  send_msg.send(Udp); // send the bytes to the SLIP stream
  Udp.endPacket(); // mark the end of the OSC Packet
  send_msg.empty(); // free space occupied by message

  //// Recieving ////

  int size = Udp.parsePacket();

  if (size > 0) {

    while (size--) {
      recieve_msg.fill(Udp.read());
    }

    if (!recieve_msg.hasError()) {
      recieve_msg.dispatch("/led", led);
    } else {
      error = recieve_msg.getError();
      Serial.print("error: ");
      Serial.println(error);
    }
  }

  delay(10);
}


void nameFound(const char* name, IPAddress ip)
{
  if (ip != INADDR_NONE) {
    Serial.print("The IP address for '");
    Serial.print(name);
    Serial.print("' is ");
    Serial.println(ip);
  } else {
    Serial.print("Resolving '");
    Serial.print(name);
    Serial.println("' timed out.");
  }
}

void serviceFound(const char* type, MDNSServiceProtocol /*proto*/,
                  const char* name, IPAddress ip,
                  unsigned short port,
                  const char* txtContent)
{
  if (NULL == name) {
    Serial.print("Finished discovering services of type ");
    Serial.println(type);
  } else {
    Serial.print("Found: '");
    Serial.print(name);
    Serial.print("' at ");
    Serial.print(ip);
    Serial.print(", port ");
    Serial.print(port);
    Serial.println(" (UDP)");

    // Check out http://www.zeroconf.org/Rendezvous/txtrecords.html for a
    // primer on the structure of TXT records. Note that the Bonjour
    // library will always return the txt content as a zero-terminated
    // string, even if the specification does not require this.
    if (txtContent) {
      Serial.print("\ttxt record: ");

      char buf[256];
      char len = *txtContent++;
      int i = 0;
      while (len) {
        i = 0;
        while (len--)
          buf[i++] = *txtContent++;
        buf[i] = '\0';
        Serial.print(buf);
        len = *txtContent++;

        if (len)
          Serial.print(", ");
        else
          Serial.println();
      }
    }
  }
}

void printWifiData() {
  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("Local IP Address: ");
  Serial.println(ip);

  // print your MAC address:
  byte mac[6];
  WiFi.macAddress(mac);
  Serial.print("MAC address: ");
  printMacAddress(mac);

  IPAddress gateway_ip = WiFi.gatewayIP();
  Serial.print("GateWay IP Address: ");
  Serial.println(gateway_ip);

}

void printCurrentNet() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print the MAC address of the router you're attached to:
  byte bssid[6];
  WiFi.BSSID(bssid);
  Serial.print("BSSID: ");
  printMacAddress(bssid);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.println(rssi);

  // print the encryption type:
  byte encryption = WiFi.encryptionType();
  Serial.print("Encryption Type:");
  Serial.println(encryption, HEX);
  Serial.println();
}

void printMacAddress(byte mac[]) {
  for (int i = 5; i >= 0; i--) {
    if (mac[i] < 16) {
      Serial.print("0");
    }
    Serial.print(mac[i], HEX);
    if (i > 0) {
      Serial.print(":");
    }
  }
  Serial.println();
}
