#include <SPI.h>
#include <WiFiNINA.h>
#include <WiFiUdp.h>
#include <OSCMessage.h>
#include <OSCBundle.h>
#include <OSCBoards.h>
#include "SparkFunLSM6DS3.h"
#include "Wire.h"
#include "arduino_secrets.h"
///////please enter your sensitive data in the Secret tab/arduino_secrets.h

char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;                 // your network key Index number (needed only for WEP)

int status = WL_IDLE_STATUS;     // the Wifi radio's status
OSCErrorCode error;
unsigned int ledState = LOW; 

WiFiUDP Udp;
WiFiServer server(80);
String readString;
IPAddress server_ip(192,168,11,103);   //change it to your server IP address
const unsigned int server_port = 5008;
const unsigned int local_port = 5006;

LSM6DS3 myIMU(SPI_MODE, SPIIMU_SS); // SPI Chip Select for build-in IMU

void setup() {
  Serial.begin(9600); //Initialize serial and wait for port to open:
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!"); 
    while (true); // don't continue
  }

  String fv = WiFi.firmwareVersion();
  if (fv < "1.0.0") {
    Serial.println("Please upgrade the firmware");
  }

  // attempt to connect to Wifi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass); // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    delay(10000);  // wait 10 seconds for connection:
  }
  server.begin(); 
  printWifiStatus(); // you're connected now, so print out the status:
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
  
  WiFiClient client = server.available(); // listen for incoming clients
  if (client) {
    Serial.println("new client");
    boolean currentLineIsBlank = true;  // an http request ends with a blank line
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        if (readString.length() < 100) {   //store characters to string
          readString += c;
        }
        
        // if you've gotten to the end of the line (received a newline
        // character) and the line is blank, the http request has ended,
        // so you can send a reply
        if (c == '\n' && currentLineIsBlank) {
          
          client.println("HTTP/1.1 200 OK");  //now output HTML data header
          client.println("Content-Type: text/html");
          client.println();
          client.println("<HTML>");
          client.println("<HEAD>");
          client.println("<TITLE>Arduino GET test page</TITLE>");
          client.println("</HEAD>");
          client.println("<BODY>");
          client.println("<H1>Change the Server</H1>");
          client.print("Current Server:");
          client.print(server_ip);
          client.print("<BR>");
          client.println("<FORM ACTION='/' method=get >"); //uses IP/port of web page
          client.println("New Server: <INPUT TYPE=TEXT NAME='Server' VALUE='' SIZE='25' MAXLENGTH='50'><BR>");
          client.println("<INPUT TYPE=SUBMIT NAME='submit' VALUE='Change Server'>");
          client.println("</FORM>");
          client.println("<BR>");
          client.println("</BODY>");
          client.println("</HTML>");

          String result = readString.substring(readString.indexOf("=") + 1, readString.indexOf("&"));
          if (server_ip.fromString(result)) {
            Serial.println(result);
            uint8_t ip[4];
            char finalIP[15];
            result.toCharArray(finalIP, 15);
            sscanf(finalIP, "%d.%d.%d.%d", &ip[0], &ip[1], &ip[2], &ip[3]);
            server_ip[0] = ip[0];
            server_ip[1] = ip[1];
            server_ip[2] = ip[2];
            server_ip[3] = ip[3];
            client.println("<font color=\"red\">Server IP is changed. Refresh page now</font>");
          }
          
          readString = "";
          break;
        }
        if (c == '\n') {
          currentLineIsBlank = true;   // you're starting a new line
        } else if (c != '\r') {
          currentLineIsBlank = false;  // you've gotten a character on the current line
        }
      }
    }
    
    delay(1);   // give the web browser time to receive the data
    client.stop();  // close the connection:
    Serial.println("client disonnected");

  }

OSCMessage send_msg("/acc");
  OSCMessage recieve_msg;
 

  Serial.print("Sending packet to ");
  Serial.print(server_ip);
  Serial.print(":");
  Serial.println(server_port);


  send_msg.add("/X").add(myIMU.readFloatAccelX());
  send_msg.add("/Y").add(myIMU.readFloatAccelY());
  send_msg.add("/Z").add(myIMU.readFloatAccelZ());
 
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

  
}


void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}
