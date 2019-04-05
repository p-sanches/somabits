#include "Encoder.h"
#include <EEPROM.h>
#include <SPI.h>
#include <WiFiNINA.h>
#include <WiFiUdp.h>

#include <OSCMessage.h>
#include <OSCBundle.h>
#include <OSCBoards.h>

#include "arduino_secrets.h" 
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
int status = WL_IDLE_STATUS;     // the Wifi radio's status

unsigned int localPort = 12000;      // local port to listen on

char packetBuffer[255]; //buffer to hold incoming packet

WiFiUDP Udp;

const IPAddress serverIp(192,168,1,101);
const unsigned int serverPort = 32000;

const byte interruptPin = 2;
int val = 0;

bool retract = true;

const int relay1 = 12;
const int relay2 = 9;

int leftmotorForward = 8;    // pin 8 --- left motor (+) green wire
int leftmotorBackward = 11; // pin 11 --- left motor (-) black wire
int leftmotorspeed = 9;     // pin 9 --- left motor speed signal

int PWM = 0;
int Inverse_PWM = 0;
int level = 0;

Encoder myEnc(2, 7); //  Set up the linear actuator encoder using pins which support interrupts, avoid using pins with LEDs attached i.e. 13
long oldPosition  = -9999; //   intializing it with random negative value
long oldPressure  = -9999; //   intializing it with random negative value
int currentPosition  = -9999; //   intializing it with random negative value
int correction = 0;


//const int PressureLocal = A5;// Pressure Sensing 
//const int PressureRemote = A6;// Pressure Sensing

const int baseline = 200; //minimum pressure for anything to happen at all, arbitrary value. Could be something to calibrate



void setup() {
  // put your setup code here, to run once:

  pinMode(leftmotorForward, OUTPUT);
  pinMode(leftmotorBackward, OUTPUT);
  pinMode(leftmotorspeed, OUTPUT);
  correction = EEPROMReadInt(0); // reading the last position of motor from EEPROM to later caliberate HallEffect sensor values
  
  Serial.begin(9600);
  //getMiddlePoint();

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
    Serial.print("Attempting to connect to open SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid);

    // wait 10 seconds for connection:
    delay(10000);
    connectToServer();
  }

  // you're connected now, so print out the data:
  Serial.print("You're connected to the network");
  printCurrentNet();
  printWifiData();

}

void printWifiData() {
  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
  Serial.println(ip);

  // print your MAC address:
  byte mac[6];
  WiFi.macAddress(mac);
  Serial.print("MAC address: ");
  printMacAddress(mac);

  // print your subnet mask:
  IPAddress subnet = WiFi.subnetMask();
  Serial.print("NetMask: ");
  Serial.println(subnet);

  // print your gateway address:
  IPAddress gateway = WiFi.gatewayIP();
  Serial.print("Gateway: ");
  Serial.println(gateway);
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





void loop() {

  //read inputs (OSC)
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
            bundleIN.dispatch("/actuator/linnorm", routeLinNorm);
            bundleIN.dispatch("/actuator/linup", routeLinUp);
            bundleIN.dispatch("/actuator/lindown", routeLinDown);
        }
   }
  

    if(retract)
      retractActuator();
    else 
      extendActuator();
 
  long newPosition = myEnc.read();  //check the encoder to see if the position has changed
  if (newPosition != oldPosition) {
    oldPosition = newPosition;
    currentPosition = newPosition + correction; //caliberating the motor position
    EEPROMWriteInt(0, currentPosition); //saving motor position in EEPROM
  }
}

//called whenever an OSCMessage's address matches "/linnorm/"
void routeLinNorm(OSCMessage &msg){
  Serial.println("Linear normal control");
 
  //returns true if the data in the first position is a float
  if (msg.isFloat(0)){
    //get that float
    float data = msg.getFloat(0);

    Serial.println(data); //-1 to 1

    if(data < 0)
      retract = true;
    else retract = false;
    
    PWM = constrain(map(abs(data), 0, 1, 0, 255), 0, 255);
  }
}

//called whenever an OSCMessage's address matches "/linnorm/"
void routeLinUp(OSCMessage &msg){
  Serial.println("Linear Up");
 
  //returns true if the data in the first position is a float
  if (msg.isFloat(0)){
    //get that float
    float data = msg.getFloat(0);

    Serial.println(data); //-1 to 1

    retract = false;
    
    
    PWM = constrain(data, 0, 255);
  }
}

//called whenever an OSCMessage's address matches "/linnorm/"
void routeLinDown(OSCMessage &msg){
  Serial.println("Linear down");
 
  //returns true if the data in the first position is a float
  if (msg.isFloat(0)){
    //get that float
    float data = msg.getFloat(0);

    Serial.println(data); //-1 to 1

    retract = true;
    PWM = constrain(data, 0, 255);
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

void extendActuator()
{
//  Serial.print("Extending with InversePWM:");
//  Serial.println(Inverse_PWM);
  analogWrite(9, PWM);
  digitalWrite(11, LOW); // Drives LOW outputs down first to avoid damage
  digitalWrite(8, HIGH);
}

void gotozero(){
  PWM = 255;
  while(1){
    retractActuator();
    EEPROMWriteInt(0, 0);
  }
}

void retractActuator()
{
//  Serial.print("Retracting with PWM:");
//  Serial.println(PWM);
  analogWrite(9, PWM);
  digitalWrite(8, LOW); // Drives LOW outputs down first to avoid damage
  digitalWrite(11, HIGH);
}

void stopActuator() // Sets speed pins to LOW disabling both motors
{
  //Serial.println("Stop actuator");
  digitalWrite(9, LOW);
  digitalWrite(11, LOW);
  digitalWrite(8, LOW);
}

void EEPROMWriteInt(int address, int value)
{
  byte two = (value & 0xFF);
  byte one = ((value >> 8) & 0xFF);

  EEPROM.update(address, two);
  EEPROM.update(address + 1, one);
}

int EEPROMReadInt(int address)
{
  long two = EEPROM.read(address);
  long one = EEPROM.read(address + 1);

  return ((two << 0) & 0xFFFFFF) + ((one << 8) & 0xFFFFFFFF);
}

//void getMiddlePoint()
//{
//   PWM = 255;
//
//  while(1){
//    
//     long newPosition = myEnc.read()+ correction;  //check the encoder to see if the position has changed
//     EEPROMWriteInt(0, newPosition); //saving motor position in EEPROM
//      
//
//     if(newPosition > 6100)
//     {
//        retractActuator();
//     }
//     else if(newPosition < 6000)
//     {
//        extendActuator();
//     }
//     else return;
//  }
//   
// 
//  
//}

