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

#include "arduino_secrets.h"
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;     // the Wifi radio's status

IPAddress server_ip;

WiFiUDP udp;
MDNS mdns(udp);
WiFiServer server(5555);

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

  Serial.println("\nStart listening to get our servers IP");
  server.begin();                           // start the web server on port 80

  Serial.println("\nStarting Service Discovery...");

  // Initialize the mDNS library. You can now reach or ping this
  // Arduino via the host name "arduino.local", provided that your operating
  // system is mDNS/Bonjour-enabled (such as MacOS X).
  // Always call this before any other method!
  mdns.begin(WiFi.localIP(), "arduino_1");

  // Now let's register the service we're offering (a web service) via Bonjour!
  // To do so, we call the addServiceRecord() method. The first argument is the
  // name of our service instance and its type, separated by a dot. In this
  // case, the service type is _http. There are many other service types, use
  // google to look up some common ones, but you can also invent your own
  // service type, like _mycoolservice - As long as your clients know what to
  // look for, you're good to go.
  // The second argument is the port on which the service is running. This is
  // port 80 here, the standard HTTP port.
  // The last argument is the protocol type of the service, either TCP or UDP.
  // Of course, our service is a TCP service.
  // With the service registered, it will show up in a mDNS/Bonjour-enabled web
  // browser. As an example, if you are using Apple's Safari, you will now see
  // the service under Bookmarks -> Bonjour (Provided that you have enabled
  // Bonjour in the "Bookmarks" preferences in Safari).
  // FIXME: Ugly hack
  uint8_t* s1 = "sensor1=/light:0%127";
  char s2[30] = "sensor2=/accelerometer";
  char a1[30] = "actuator1=/sound:0%255";


  char txt[100] = {'\0'};

  txt[0] = (uint8_t) strlen(s1);
  int txt_len = 1;
  for (uint8_t i = 0; i < strlen(s1); i++) {
    if (s1[i] != '\0'); {
      txt[txt_len] = s1[i];
     txt_len++;
    }
  }

  txt[txt_len] = (uint8_t) strlen(a1);
  txt_len++;
  for (uint8_t i = 0; i < strlen(a1); i++) {
    if (a1[i] != '\0') {
      txt[txt_len] = a1[i];
      txt_len++;
    }
 }
  
  Serial.println(txt);

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
}



void loop() {
	// This actually runs the mDNS module. YOU HAVE TO CALL THIS PERIODICALLY,
	// OR NOTHING WILL WORK! Preferably, call it once per loop().
	mdns.run();

	WiFiClient client = server.available();   // listen for incoming clients

	if (client) {                             // if you get a client,
		Serial.println("We get the servers IP :-)");     // print a message out the serial port
		String currentLine = ""; // make a String to hold incoming data from the client
		while (client.connected()) {        // loop while the client's connected
			//Serial.println("test");
			if (client.available()) { // if there's bytes to read from the client
				//Serial.println("there");
				char c = NULL;
				do {
					c = client.read();
					currentLine += c;    // add it to the end of the currentLine
				} while (c != -1);
			}
			currentLine += "\n";
			Serial.println(currentLine);
		}


		// close the connection:
		client.stop();
		Serial.println("Client disonnected");
		server_ip.fromString(currentLine);
		Serial.print("Server IP: ");
		Serial.println(server_ip);
	}
}
