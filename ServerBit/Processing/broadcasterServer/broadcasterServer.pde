/**
 * SOMA BITS broadcasting server 
 * Created 2019-02-26
 * by p_sanches
 *
 * Based on:
 *
 * oscP5broadcaster by andreas schlegel
 * an osc broadcast server.
 * osc clients can connect to the server by sending a connect and
 * disconnect osc message as defined below to the server.
 * incoming messages at the server will then be broadcasted to
 * all connected clients. 
 * an example for a client is located in the oscP5broadcastClient exmaple.
 * oscP5 website at http://www.sojamo.de/oscP5
 *
 */
 
import oscP5.*;
import netP5.*;
import java.util.Map;


OscP5 oscP5;
NetAddressList SensorNetAddressList = new NetAddressList();
NetAddressList ActuatorNetAddressList = new NetAddressList();

NetAddress wekinator;


//data structure to hold all sensor data
HashMap<String,Object[]> sensorInputs = new HashMap<String,Object[]>();


/* listeningPort is the port the server is listening for incoming messages */
int myListeningPort = 32000;
/* the broadcast port is the port the clients should listen for incoming messages from the server*/
int myBroadcastPort = 12000;

String SensorConnectPattern = "/sensor/startConnection/";
String SensorDisconnectPattern = "/sensor/endConnection/";

String ActuatorConnectPattern = "/actuator/startConnection/";
String ActuatorDisconnectPattern = "/actuator/endConnection/";


void setup() {
  oscP5 = new OscP5(this, myListeningPort);
  wekinator = new NetAddress("127.0.0.1",6448);
  frameRate(25);
}

void draw() {
  background(0);
}

void oscEvent(OscMessage theOscMessage) {
  /* check if the address pattern fits any of our patterns */
  if (theOscMessage.addrPattern().equals(SensorConnectPattern)) {
    connectSensor(theOscMessage.netAddress().address());
  }
  else if (theOscMessage.addrPattern().equals(SensorDisconnectPattern)) {
    disconnectSensor(theOscMessage.netAddress().address());
  }
  else if (theOscMessage.addrPattern().equals(ActuatorConnectPattern)) {
    connectActuator(theOscMessage.netAddress().address());
  }
  else if (theOscMessage.addrPattern().equals(ActuatorDisconnectPattern)) {
    disconnectActuator(theOscMessage.netAddress().address());
  }
  /**
   * if pattern matching was not successful, then broadcast the incoming
   * message to all actuators in the ActuatorAddresList. 
   */
   //check if sender is on sensor list (TBD: currently any OSC command is just blindly forwarded to the actuators without checking)

  else {
    
    //add it to a data structure with all known OSC addresses (hashmap: addrPattern, arguments)
    sensorInputs.put(theOscMessage.addrPattern(), theOscMessage.arguments());
    printAllSensorInputs();
   
    
    //optionally do something else with it, e.g. wekinator, store data, smart data layer
    //trainWekinator(theOscMessage);
    
    //printOSCMessage(theOscMessage);
    //oscP5.send(theOscMessage, ActuatorNetAddressList);
    sendAllSensorData();
  }
}

void sendAllSensorData(){
  
    /* create an osc bundle */
  OscBundle myBundle = new OscBundle();
  OscMessage myMessage = new OscMessage(""); 
  
   for (Map.Entry me : sensorInputs.entrySet()) {
       myMessage.setAddrPattern( (String) me.getKey());
       myMessage.setArguments ( (Object[])me.getValue() );

        /* add an osc message to the osc bundle */
        myBundle.add(myMessage);
        
         /* reset and clear the myMessage object for refill. */
        myMessage.clear();
    }
  
  myBundle.setTimetag(myBundle.now() + 10000);
  /* send the osc bundle, containing 2 osc messages, to a remote location. */
  oscP5.send(myBundle, ActuatorNetAddressList);
  
 
}

void printAllSensorInputs(){
   println("### Current sensor inputs (" + sensorInputs.size()+"):");
     // Using an enhanced loop to iterate over each entry
      for (Map.Entry me : sensorInputs.entrySet()) {
        print(me.getKey() + " is ");
        println(me.getValue());
      }
}


/* incoming osc message are forwarded to the oscEvent method. */
void printOSCMessage(OscMessage theOscMessage) {
  /* print the address pattern and the typetag of the received OscMessage */
  print("### received an osc message.");
  print(" addrpattern: "+theOscMessage.addrPattern());
  println(" typetag: "+theOscMessage.typetag());
}

 private void connectSensor(String theIPaddress) {
     if (!SensorNetAddressList.contains(theIPaddress, myBroadcastPort)) {
       SensorNetAddressList.add(new NetAddress(theIPaddress, myBroadcastPort));
       println("### adding "+theIPaddress+" to the sensor list.");
     } else {
       println("### Sensor "+theIPaddress+" is already connected.");
     }
     println("### currently there are "+SensorNetAddressList.list().size()+" sensors connected.");
 }



private void disconnectSensor(String theIPaddress) {
if (SensorNetAddressList.contains(theIPaddress, myBroadcastPort)) {
    SensorNetAddressList.remove(theIPaddress, myBroadcastPort);
       println("### removing sensor "+theIPaddress+" from the list.");
     } else {
       println("### Sensor "+theIPaddress+" is not connected.");
     }
       println("### Sensors: currently there are "+SensorNetAddressList.list().size());
 }
 
 
  private void connectActuator(String theIPaddress) {
     if (!ActuatorNetAddressList.contains(theIPaddress, myBroadcastPort)) {
       ActuatorNetAddressList.add(new NetAddress(theIPaddress, myBroadcastPort));
       println("### adding "+theIPaddress+" to the actuator list.");
     } else {
       println("### Actuator "+theIPaddress+" is already connected.");
     }
     println("### currently there are "+ActuatorNetAddressList.list().size()+" actuators connected.");
 }



private void disconnectActuator(String theIPaddress) {
if (ActuatorNetAddressList.contains(theIPaddress, myBroadcastPort)) {
    ActuatorNetAddressList.remove(theIPaddress, myBroadcastPort);
       println("### removing actuator "+theIPaddress+" from the list.");
     } else {
       println("### Actuator "+theIPaddress+" is not connected.");
     }
       println("### Actuators: currently there are "+ActuatorNetAddressList.list().size());
 }
 
 
void trainWekinator(OscMessage msg) {
  OscMessage wekaMsg = new OscMessage("/wek/inputs");
  wekaMsg.setArguments(msg.arguments());
 
  oscP5.send(wekaMsg, wekinator);
}
