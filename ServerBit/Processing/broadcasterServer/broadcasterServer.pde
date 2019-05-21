/**
 * SOMA BITS broadcasting server 
 * Created 2019-02-26
 * by p_sanches
 *
 * /sensor/[sid]/[anypath] [float]
 * /actuator/[sid]/[anypath] [float]
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
 
 //pavels IP: 107
 
import oscP5.*;
import netP5.*;
import java.io.*; 
import java.util.*; 


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

String wekaPattern = "/wek/outputs";


void setup() {
  oscP5 = new OscP5(this, myListeningPort);
  wekinator = new NetAddress("127.0.0.1",6448);
  
  connectActuator("127.0.0.1");
  
  frameRate(25);
}

void draw() {
  //background(0);
  //if(sensorInputs.size()>0)
  //  trainWekinatorWithAllSensors();
}

void oscEvent(OscMessage theOscMessage) {
  //println("### OSC MESSAGE ARRIVED");
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
  else if (theOscMessage.addrPattern().equals(wekaPattern)) {
    //custom code to deal with it (replace function when needed)
    WekinatorMKRVibe(theOscMessage);
  }
  /**
   * if pattern matching was not successful, then broadcast the incoming
   * message to all actuators in the ActuatorAddresList. 
   */
   //check if sender is on sensor list (TBD: currently any OSC command is just blindly forwarded to the actuators without checking)

  else if(theOscMessage.addrPattern().contains("/sensor")){
    
    //add it to a data structure with all known OSC addresses (hashmap: addrPattern, arguments)
    addSensorValuetoHashMap(theOscMessage);
    
    //printAllSensorInputs();
   
    //optionally do something else with it, e.g. wekinator, store data, smart data layer
    //trainWekinatorMsg(theOscMessage);
    //trainWekinatorWithAllSensors();
    
    //printOSCMessage(theOscMessage);
    //oscP5.send(theOscMessage, ActuatorNetAddressList);
    //sendAllSensorData();
  }
  else if(theOscMessage.addrPattern().contains("/actuator")){
    sendOneActuatorData(theOscMessage);
    printOSCMessage(theOscMessage);
  }
  else{
   // print("## Sending OSC Message directly to Wekinator");
    //printOSCMessage(theOscMessage);
   // trainWekinatorMsg(theOscMessage);
  }
}

void addSensorValuetoHashMap(OscMessage theOscMessage){
  
  String[] address = new String[2];
  
  address[0]=theOscMessage.netAddress().address();
  address[1]=theOscMessage.addrPattern();
  
  sensorInputs.put(join(address,"/"), theOscMessage.arguments());
  
}

void WekinatorMKRVibe(OscMessage theOscMessage){
  OscBundle myBundle = new OscBundle();
  
  //open wek/outputs
  OscMessage intensity1Message = new OscMessage("/actuator/vibeintensity1"); 
  intensity1Message.add(theOscMessage.get(0).floatValue());
  myBundle.add(intensity1Message);
   
  OscMessage intensity2Message = new OscMessage("/actuator/vibeintensity2"); 
  intensity2Message.add(theOscMessage.get(1).floatValue());
   myBundle.add(intensity2Message);
   
  OscMessage time1Message = new OscMessage("/actuator/vibetime1"); 
  time1Message.add(theOscMessage.get(2).floatValue());
  myBundle.add(time1Message);
  
  OscMessage time2Message = new OscMessage("/actuator/vibetime2"); 
  time2Message.add(theOscMessage.get(3).floatValue());
  myBundle.add(time2Message);
 
  myBundle.setTimetag(myBundle.now() + 10000);
 
  oscP5.send(myBundle, ActuatorNetAddressList);
}

void sendOneActuatorData(OscMessage theOscMessage){
  
    /* create an osc bundle */
  OscBundle myBundle = new OscBundle();
  myBundle.add(theOscMessage);
 
  myBundle.setTimetag(myBundle.now() + 10000);
  /* send the osc bundle, containing 1 osc messages, to all actuators. */
  oscP5.send(myBundle, ActuatorNetAddressList);
}

void sendAllRawSensorData(){
  
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
  int i = 0;
  /* print the address pattern and the typetag of the received OscMessage */
  print("### Printing an osc message.");
  print(" addrpattern: "+theOscMessage.addrPattern());
  print(" typetag: "+theOscMessage.typetag());
  //println(" args: "+theOscMessage.arguments());
  while(i<theOscMessage.arguments().length) {
        print(" ["+(i)+"] ");
        print(theOscMessage.arguments()[i]);
        i++;
      }
   println(" ## Ending of message");
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

void trainWekinatorWithAllSensors() {
  //println("entering");
  OscMessage wekaMsg = new OscMessage("/wek/inputs");
  int i = 0;
  float[] args = new float[sensorInputs.size()];
  
  //println("entering trouble:"+sensorInputs.size());
  
  println("### Training WEKA with all sensors (" + sensorInputs.size()+"):");
     // Using an enhanced loop to iterate over each entry
     
     Iterator entries = sensorInputs.entrySet().iterator();
      while (entries.hasNext()) {
            Map.Entry entry = (Map.Entry) entries.next();
            String key = (String)entry.getKey();
            Object[] value = (Object[])entry.getValue();
            print("["+(i)+"] ");
            print(key + " is ");
            println(value);
            args[i]=(float)value[0];
            i++;
        }
    
     //for (Map.Entry me : sensorInputs.entrySet()) {
        
     //   String key = (String) me.getKey();
     //   Object[] value = (Object[])me.getValue();
     //   print("["+(i)+"] ");
     //   print(key + " is ");
     //   println(value);
     //   args[i]=(float)value[0];
     //   i++;
     // }
      
      
//println("Im REALLY out of trouble");
      //for (Map.Entry me : sensorInputs.entrySet()) {
      //  print("["+(i)+"] ");
      //  print(me.getKey() + " is ");
      //  println(me.getValue());
        
      //  wekaMsg.add((Object[])me.getValue());
      //  //args[i] = (me.getValue())[0];
      //  i++;
      //}

  wekaMsg.add(args);
  
  printOSCMessage(wekaMsg);
 
  oscP5.send(wekaMsg, wekinator);
}
 
void trainWekinatorMsg(OscMessage msg) {
  OscMessage wekaMsg = new OscMessage("/wek/inputs");
  wekaMsg.setArguments(msg.arguments());
  printOSCMessage(wekaMsg);
 
  oscP5.send(wekaMsg, wekinator);
}
