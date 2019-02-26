/*

 This example connects to an unencrypted WiFi network.
 Then it prints the  MAC address of the WiFi shield,
 the IP address obtained, and other network details.

 Circuit:
 * WiFi shield attached

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
boolean effectMode = true;


int vibeIntensityRT=0;
int vibeDelayRT=0;


#include "arduino_secrets.h" 
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;     // the WiFi radio's status

unsigned int localPort = 12000;      // local port to listen on

char packetBuffer[255]; //buffer to hold incoming packet

WiFiUDP Udp;

const IPAddress serverIp(192,168,1,63);
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
  // default, internal trigger when sending GO command
  drv.setMode(DRV2605_MODE_INTTRIG); 


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
    status = WiFi.begin(ssid, pass);

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

  Serial.print("\nConnecting to server bit at ");
  Serial.print(serverIp);Serial.print(":");Serial.println(serverPort);
  
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


   OSCMessage bundleIN;
   int size;
 
   if( (size = Udp.parsePacket())>0)
   {

         while(size--)
           bundleIN.fill(Udp.read());
    
        if(!bundleIN.hasError())
        {
            bundleIN.dispatch("/server/led", routeLED);
            bundleIN.dispatch("/server/vibeeffect", routeVibeEffect);
            bundleIN.dispatch("/server/vibeintensity", routeVibeIntensityRT);
            bundleIN.dispatch("/server/vibedelay", routeVibeDelayRT);
        }
   }

   if(effectMode)
      playVibeEffect();
   else
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
  setEffectMode();
  //returns true if the data in the first position is a float
  if (msg.isFloat(0)){
    //get that float
    float data = msg.getFloat(0);

    Serial.println(data);
    effect = data;
  }
}

void setEffectMode(){
  if(!effectMode){
    effectMode=true;
    drv.setMode(DRV2605_MODE_INTTRIG); 
  }
}

void setRTMode(){

  if(effectMode){
    effectMode=false;
    drv.setMode(DRV2605_MODE_REALTIME); 
  }
}

//called whenever an OSCMessage's address matches "/led/"
void routeVibeIntensityRT(OSCMessage &msg){
  Serial.println("Vibe Intensity");
  setRTMode(); 
  //returns true if the data in the first position is a float
  if (msg.isFloat(0)){
    //get that float
    float data = msg.getFloat(0);

    Serial.println(data);
    vibeIntensityRT = data;
  }
}

//called whenever an OSCMessage's address matches "/led/"
void routeVibeDelayRT(OSCMessage &msg){
  Serial.println("Vibe Delay");
  setRTMode();
  //returns true if the data in the first position is a float
  if (msg.isFloat(0)){
    //get that float
    float data = msg.getFloat(0);

    Serial.println(data);
    vibeDelayRT = data;
  }
}

void playVibeEffect(){
  // set the effect to play
  drv.setWaveform(0, effect);  // play effect 
  drv.setWaveform(1, 0);       // end waveform

  // play the effect!
  drv.go();
  delay(20);
}


void playVibeRT(){
  drv.setRealtimeValue(vibeIntensityRT);
  delay(10);
  drv.setRealtimeValue(0);
  delay(vibeDelayRT);
}




void connectToServer(){

    OSCMessage msg("/server/startConnection/");
  
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
