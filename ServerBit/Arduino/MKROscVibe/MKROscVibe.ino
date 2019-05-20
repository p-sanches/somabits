/*

 This example connects to an unencrypted WiFi network.
 Then to a broadcasting OSC server in Processing
 Then it accepts commands to control LED and vibration patterns using the Adafruit_DRV2605
 Based on Oscuino

 Circuit:
 * WiFi shield attached

Created 2019-02-26
by p_sanches

Based on tutorials:
 created 13 July 2010
 by dlf (Metodo2 srl)
 modified 31 May 2012
 by Tom Igoe



 
 */
#include <SPI.h>
#include <WiFi101.h>
#include <WiFiUdp.h>
#include <OSCMessage.h>
#include <OSCBundle.h>
#include <OSCBoards.h>
#include <Wire.h>
#include "Adafruit_DRV2605.h"


Adafruit_DRV2605 drv;

uint8_t effect = 1; //Pre-made vibe Effects
boolean effectMode = false;

unsigned long time_now = 0;

int vibeIntensity1=0;
int vibeIntensity2=0;
int vibeTime1=1;
int vibeTime2=1;

boolean vibe1 = true;


#include "arduino_secrets.h" 
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;     // the WiFi radio's status

unsigned int localPort = 12000;      // local port to listen on

char packetBuffer[255]; //buffer to hold incoming packet

WiFiUDP Udp;

const IPAddress serverIp(192,168,1,101);
const unsigned int serverPort = 32000;


void setup() {

  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  //Initialize actuators

  //initialize LED
  pinMode(LED_BUILTIN, OUTPUT); 
  
  //initializeVibe
  drv.begin();
  drv.selectLibrary(1);
  drv.useLRA();
  // I2C trigger by sending 'go' command 
  // default: realtime
  drv.setMode(DRV2605_MODE_REALTIME); 


  // check for the presence of the shield:
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue:
    while (true);
  }

  // attempt to connect to WiFi network:
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    // Connect to network:
    status = WiFi.begin(ssid);

    // wait 10 seconds for connection:
    delay(10000);
  }

  // you're connected now, so print out the data:
  Serial.print("You're connected to the network");
  printCurrentNet();
  printWiFiData();

  Serial.print("\nStarting listening on port:");
  Serial.print(localPort);
  // if you get a connection, report back via serial:
  Udp.begin(localPort);

  
  
  //register with server
  connectToServer();
  delay(50);
}

void loop() {
//   //if there's data available, read a packet
//  int packetSize = Udp.parsePacket();
//  if (packetSize)
//  {
//    Serial.print("Received packet of size ");
//    Serial.println(packetSize);
//    Serial.print("From ");
//    IPAddress remoteIp = Udp.remoteIP();
//    Serial.print(remoteIp);
//    Serial.print(", port ");
//    Serial.println(Udp.remotePort());
//
//    // read the packet into packetBufffer
//    int len = Udp.read(packetBuffer, 255);
//    if (len > 0) packetBuffer[len] = 0;
//    Serial.println("Contents:");
//    Serial.println(packetBuffer);
//  }

  char incomingByte = 0;   // for incoming serial data
  if (Serial.available() > 0) {
        // read the incoming byte:
        incomingByte = Serial.read();
        if(incomingByte=='c'){
          connectToServer();
          delay(50);
        }
    }

   OSCBundle bundleIN;
   int size;
 
   if( (size = Udp.parsePacket())>0)
   {

         while(size--)
           bundleIN.fill(Udp.read());
    
        if(!bundleIN.hasError())
        {
            bundleIN.dispatch("/actuator/led", routeLED);
            //bundleIN.dispatch("/actuator/vibeeffect", routeVibeEffect);
            bundleIN.dispatch("/actuator/vibeintensity1", routeVibeIntensity1);
            bundleIN.dispatch("/actuator/vibeintensity2", routeVibeIntensity2);
            bundleIN.dispatch("/actuator/vibetime1", routeVibeTime1);
            bundleIN.dispatch("/actuator/vibetime2", routeVibeTime2);
        }
   }

//   if(effectMode)
//      playVibeEffect();
//   else
      playVibeRT();
}

//called whenever an OSCMessage's address matches "/led/"
void routeLED(OSCMessage &msg){
  Serial.println("LED COntrol");
  //returns true if the data in the first position is a float
  if (msg.isFloat(0)){
    //get that float
    float data = msg.getFloat(0);

    Serial.println(data);

    if (data==0) 
      digitalWrite(LED_BUILTIN, LOW);
    else if(data==1) digitalWrite(LED_BUILTIN, HIGH);
  }
}

//called whenever an OSCMessage's address matches "/led/"
void routeVibeEffect(OSCMessage &msg){
  Serial.println("Vibe Effect");
  //setEffectMode();
  //returns true if the data in the first position is a float
  if (msg.isFloat(0)){
    //get that float
    float data = msg.getFloat(0);

    Serial.println(data);
    effect = data;
  }
}

//void setEffectMode(){
//  if(!effectMode){
//    effectMode=true;
//    drv.setMode(DRV2605_MODE_INTTRIG); 
//  }
//}

void setRTMode(){

  if(effectMode){
    effectMode=false;
    drv.setMode(DRV2605_MODE_REALTIME); 
  }
}

//called whenever an OSCMessage's address matches "/led/"
void routeVibeIntensity1(OSCMessage &msg){
  Serial.println("Vibe Intensity 1");
  //setRTMode(); 
  //returns true if the data in the first position is a float
  if (msg.isFloat(0)){
    //get that float
    float data = msg.getFloat(0);

    Serial.println(data);
    vibeIntensity1 = data;
  }
}

//called whenever an OSCMessage's address matches "/led/"
void routeVibeIntensity2(OSCMessage &msg){
  Serial.println("Vibe Intensity 2");
  //setRTMode(); 
  //returns true if the data in the first position is a float
  if (msg.isFloat(0)){
    //get that float
    float data = msg.getFloat(0);

    Serial.println(data);
    vibeIntensity2 = data;
  }
}

//called whenever an OSCMessage's address matches "/led/"
void routeVibeTime1(OSCMessage &msg){
  Serial.println("Time 1");
  setRTMode();
  //returns true if the data in the first position is a float
  if (msg.isFloat(0)){
    //get that float
    float data = msg.getFloat(0);

    Serial.println(data);
    vibeTime1 = data;
  }
}

//called whenever an OSCMessage's is meant to change the time off
void routeVibeTime2(OSCMessage &msg){
  Serial.println("Time 2");
  //setRTMode();
  //returns true if the data in the first position is a float
  if (msg.isFloat(0)){
    //get that float
    float data = msg.getFloat(0);

    Serial.println(data);
    vibeTime2 = data;
  }
}

//void playVibeEffect(){
//  // set the effect to play
//  drv.setWaveform(0, effect);  // play effect 
//  drv.setWaveform(1, 0);       // end waveform
//
//  // play the effect!
//  drv.go();
//  delay(20);
//}


void playVibeRT(){

  //if 1
  //if delay is more than delay1
  //turn 2
  //else (if 2)
  //if delay is more than delay2
  //turn 1
  
  
  if(vibe1){
    if(millis() > time_now + vibeTime1){
      time_now = millis();
      drv.setRealtimeValue(vibeIntensity2);
      vibe1=false;
    }
  }
  else{ //we're on square 2
    if(millis() > time_now + vibeTime2){
      time_now = millis();
      drv.setRealtimeValue(vibeIntensity1);
      vibe1=true;
    }
    
  }
}




void connectToServer(){

    Serial.print("\nConnecting to server bit at ");
    Serial.print(serverIp);Serial.print(":");Serial.println(serverPort);

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
