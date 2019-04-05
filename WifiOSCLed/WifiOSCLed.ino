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

#include "Wire.h"

#include "arduino_secrets.h"
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;     // the Wifi radio's status

OSCErrorCode error;



// A UDP instance to let us send and receive packets over UDP
WiFiUDP Udp;

IPAddress server_ip(192, 168, 11, 103); //change it to your server IP address
const unsigned int server_port = 3333;
const unsigned int local_port = 3333;
int interval = 1000;
unsigned int ledState = LOW;
unsigned long previousMillis = 0;


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

  mdns.begin(WiFi.localIP(), "arduino_3");
  uint8_t* s1 = "actuator1=/light:100%-1000";

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
  success = mdns.addServiceRecord("Arduino with Accelerometer_3._osc",
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

  pinMode(LED_BUILTIN, OUTPUT);

}


void led(OSCMessage &msg) {
  interval = msg.getInt(0);

}


void loop() {
  mdns.run();

  OSCMessage recieve_msg("/accelerometer");

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;

    // if the LED is off turn it on and vice-versa:
    if (ledState == LOW) {
      ledState = HIGH;
    } else {
      ledState = LOW;
    }

    // set the LED with the ledState of the variable:
    digitalWrite(LED_BUILTIN, ledState);
  }


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
