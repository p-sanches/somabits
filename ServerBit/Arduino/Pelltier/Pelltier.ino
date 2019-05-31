/*

  This example connects to an unencrypted WiFi network.
  Then to a broadcasting OSC server in Processing
  Then it accepts commands to control LED and vibration patterns using the Adafruit_DRV2605
  Based on Oscuino

  Circuit:
   WiFi shield attached

  Created 2019-02-26
  by p_sanches

  Based on tutorials:
  created 13 July 2010
  by dlf (Metodo2 srl)
  modified 31 May 2012
  by Tom Igoe

*/
#include <SPI.h>  
#include <WiFiNINA.h>
#include <WiFiUdp.h>
#include <OSCMessage.h>
#include <OSCBundle.h>
#include <OSCBoards.h>

// If you use the WiFiNINA with the OSC library make sure you remove 
// "SLIPEncodedSerial.cpp" and "SLIPEncodedSerial.h" from 
// the arduino --> osc library. (#slavic_warrior_solution)


int coldOn_A = 0;
int coldIntensity_A = 0;

int coldOn_B = 0;
int coldIntensity_B = 0;

#include "arduino_secrets.h"
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;     // the WiFi radio's status

unsigned int localPort = 12000;      // local port to listen on

char packetBuffer[255]; //buffer to hold incoming packet

WiFiUDP Udp;

const IPAddress serverIp(192, 168, 1, 105);
const unsigned int serverPort = 32000;

// motor shield paramters init 

int dirA = 12;
int pwmA = 3;
int brakeA = 9;
const int currentSenseA = A0;

int dirB = 13;
int pwmB = 11;
int brakeB = 8;
const int currentSenseB = A1;

const double currentFactor = 2/3.3; //3.3V per 2A which is 0.909


void setup() {

  //Initialize serial and wait for port to open:
  
  Serial.begin(9600);
  while (!Serial) {
    
    ; // wait for serial port to connect. Needed for native USB port only
  }


  //Setup Channel A on Motorshield

  pinMode(dirA, OUTPUT); //Initiates Motor Channel A pin
  pinMode(brakeA, OUTPUT); //Initiates Brake Channel A pin
  
  pinMode(dirB, OUTPUT);    //Initiates Motor Channel B pin
  pinMode(brakeB, OUTPUT);     //Initiates Brake Channel B pin

  pinMode(currentSenseA, INPUT);
  pinMode(currentSenseB, INPUT);

  pinMode(A5, INPUT);
  pinMode(6, OUTPUT);
  pinMode(7, INPUT);

  //initialize LED
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);


  // check for the presence of the shield:
  
  if (WiFi.status() == WL_NO_SHIELD) {
        Serial.println("WiFi shield not present");
    //don't continue:
    while (true);
  }


  // attempt to connect to WiFi network:
  
  while ( status != WL_CONNECTED) {
        Serial.print("Attempting to connect to WPA SSID: ");
        Serial.println(ssid);
    // Connect to network:
    status = WiFi.begin(ssid);

    // wait 10 seconds while blinking for connection:

    for (int i = 0; i <= 10; i++) {
      digitalWrite(13, HIGH);
      delay(500);
      digitalWrite(13, LOW);
      delay(500);
    }

    digitalWrite(13, HIGH);
    delay(3000);
    digitalWrite(13, LOW);

  }

  digitalWrite(13, HIGH);
  delay(3000);
  digitalWrite(13, LOW);

  //  you're connected now, so print out the data:
    Serial.print("You're connected to the network");
    printCurrentNet();
    printWiFiData();

    Serial.print("\nStarting listening on port:");
    Serial.print(localPort);

    
  //  if you get a connection, report back via serial:
  Udp.begin(localPort);

  //register with server
  connectToServer();
  delay(50);
}


void loop() {

  OSCBundle bundleIN;
  int size;

  if ( (size = Udp.parsePacket()) > 0)
  {

    while (size--)
      bundleIN.fill(Udp.read());

    if (!bundleIN.hasError())
    {
      
      bundleIN.dispatch("/actuator/coldona", routeColdOn_A);
      bundleIN.dispatch("/actuator/coldintensitya", routeColdIntensity_A);
      bundleIN.dispatch("/actuator/coldonb", routeColdOn_B);
      bundleIN.dispatch("/actuator/coldintensityb", routeColdIntensity_B);
      
    }
  }
  
  playCold_A();
  playCold_B();
  
}


//called whenever an OSCMessage's address matches "/coldon/"

void routeColdOn_A(OSCMessage &msg) {
    Serial.println("Cold On A");
    
   //returns true if the data in the first position is a float
  
  if (msg.isFloat(0)) {
    //get that float
    float data = msg.getFloat(0);

        Serial.println(data);

    coldOn_A = data;  

  }
}

void routeColdOn_B(OSCMessage &msg) {
    Serial.println("Cold On B");
    
   //returns true if the data in the first position is a float
  
  if (msg.isFloat(0)) {
    //get that float
    float data = msg.getFloat(0);

        Serial.println(data);

    coldOn_B = data;  

  }
}


//called whenever an OSCMessage's address matches "/coldintensity/"
void routeColdIntensity_A(OSCMessage &msg) {
    Serial.println("Cold Intensity A");

  //returns true if the data in the first position is a float.

  //RANGE: 0...255
  
  if (msg.isFloat(0)) {
    //get that float
    float data = msg.getFloat(0);

    coldIntensity_A = (int) data;
    
  }
  Serial.println(coldIntensity_A);
}


void routeColdIntensity_B(OSCMessage &msg) {
    Serial.println("Cold Intensity B");

  //returns true if the data in the first position is a float.

  //RANGE: 0...255
  
  if (msg.isFloat(0)) {
    //get that float
    float data = msg.getFloat(0);

    coldIntensity_B = (int) data;
    
  }
  Serial.println(coldIntensity_B);
}


void playCold_A() {

  if (coldOn_A == 1)
  {
     Serial.println("Cold is on A");
     digitalWrite(dirA, HIGH);      //Establishes forward direction of Channel A
     digitalWrite(brakeA, LOW);    //Disengage the Brake for Channel A
     analogWrite(pwmA, coldIntensity_A);      //coldIntensity
     digitalWrite(13, HIGH);          // Switch ON LED
     double currentV = map(analogRead(currentSenseA), 0, 1024, 0, 5000)/1000;
     Serial.print("Current is: ");
     Serial.println(currentV*currentFactor);
  }

  else
  { 
    digitalWrite(brakeA, HIGH);       //Engage the Brake for Channel A
    digitalWrite(13, LOW);           // Switch off LED
  }

}



void playCold_B() {

  if (coldOn_B == 1)
  {
     Serial.println("Cold is on B");
     digitalWrite(dirB, HIGH);      //Establishes forward direction of Channel B
     digitalWrite(brakeB, LOW);    //Disengage the Brake for Channel B
     analogWrite(pwmB, coldIntensity_B);      //coldIntensity
     digitalWrite(13, HIGH);          // Switch ON LED
     double currentV = map(analogRead(currentSenseB), 0, 1024, 0, 5000)/1000;
     Serial.print("Current is: ");
     Serial.println(currentV*currentFactor);
  }

  else
  { 
    digitalWrite(brakeB, HIGH);       //Engage the Brake for Channel B
    digitalWrite(13, LOW);           // Switch off LED
  }

}


void connectToServer() {

    Serial.print("\nConnecting to server bit at ");
    Serial.print(serverIp); Serial.print(":"); Serial.println(serverPort);

  OSCMessage msg("/actuator/startConnection/");

  Udp.beginPacket(serverIp, serverPort);
  msg.send(Udp); // send the bytes to the SLIP stream

  Udp.endPacket();

  msg.empty(); // free space occupied by message
}

void printWiFiData() {
  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
    Serial.print("IP Address: ");
    Serial.println(ip);
    Serial.println(ip);

  // print your MAC address:
  byte mac[6];
  WiFi.macAddress(mac);
    Serial.print("MAC address: ");
    printMacAddress(mac);

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
