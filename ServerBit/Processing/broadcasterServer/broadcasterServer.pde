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
import controlP5.*;

//import org.apache.commons.collections4.*;

boolean fileStarted=false;


OscP5 oscP5;
NetAddressList SensorNetAddressList = new NetAddressList();
NetAddressList ActuatorNetAddressList = new NetAddressList();

int indexIP = 0;
HashMap<String, Integer> DeviceIPs = new HashMap<String, Integer>();

NetAddress wekinator;


//data structure to hold all sensor data
HashMap<String,Object[]> sensorInputs = new HashMap<String,Object[]>();

HashMap<String,Object[]> actuatorInputs = new HashMap<String,Object[]>();



/* listeningPort is the port the server is listening for incoming messages */
int myListeningPort = 32000;
/* the broadcast port is the port the clients should listen for incoming messages from the server*/
int myBroadcastPort = 12000;

String SensorConnectPattern = "/sensor/startConnection/";
String SensorDisconnectPattern = "/sensor/endConnection/";

String ActuatorConnectPattern = "/actuator/startConnection/";
String ActuatorDisconnectPattern = "/actuator/endConnection/";

String wekaPattern = "/wek/outputs";

ControlP5 cp5;
PrintWriter output;

int myColor = color(255);
int c1,c2;

float n,n1;


void setup() {
  oscP5 = new OscP5(this, myListeningPort);
  wekinator = new NetAddress("127.0.0.1",6448);
  
  connectActuator("127.0.0.1");
  
  size(400,600);
  noStroke();
  cp5 = new ControlP5(this);
  
  // create a new button with name 'buttonA'
  cp5.addButton("Write")
     .setValue(0)
     .setPosition(100,100)
     .setSize(200,99)
     ;
  
  // and add another 2 buttons
  cp5.addButton("EndFile")
     .setValue(100)
     .setPosition(100,200)
     .setSize(200,99)
     ;
  
  frameRate(25);
}

// function Start will receive changes from 
// controller with name Start
public void Write(int theValue) {
  
  //checks if there are sensors
  if(!sensorInputs.isEmpty()){
    
    String filename= "sensors"+System.currentTimeMillis()+".txt";
    
    output = createWriter(filename); 
    
    output.print("millis"+"\t");
    
    //writes headers of files
    Set<String> keys = sensorInputs.keySet();
    for(String key: keys){
        output.print(key+"\t"); // Write the header to the file
        //text(key+"\t", 10, 10, 70, 80);  // Text wraps within text box
    }
    Set<String> keys2 = actuatorInputs.keySet();
    for(String key: keys2){
        output.print(key+"\t"); // Write the header to the file
        //text(key+"\t", 10, 10, 70, 80);  // Text wraps within text box
    }
    output.print("\n");
    
    println("Starting writing to file: "+filename);
    c1 = c2;
    c2 = color(0,160,100);
    fileStarted=true;
  }
  else println("There are no sensor inputs for now.");
}

// function End will receive changes from 
// controller with name End
public void EndFile(int theValue) {
  
  if(fileStarted){
     println("Ending file");
    output.flush(); // Writes the remaining data to the file
    output.close(); // Finishes the file
    c1 = c2;
    c2 = color(150,0,0);
    fileStarted=false;
  }
  
 
}

void draw() {
  background(myColor);
  myColor = lerpColor(c1,c2,n);
  n += (1-n)* 0.1; 
  
  if(fileStarted){
    
     output.print(millis()+"\t");
    
      //writes headers of files
      Set<String> keys = sensorInputs.keySet();
      for(String key: keys){
          output.print(sensorInputs.get(key)[0]+"\t"); // Write the header to the file
      }
      Set<String> keys2 = actuatorInputs.keySet();
      for(String key: keys2){
          output.print(actuatorInputs.get(key)[0]+"\t"); // Write the header to the file
      }
      output.print("\n");
  }
  //background(0);
  //if(sensorInputs.size()>0)
  //  printAllSensorInputs();
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
    
   // printAllSensorInputs();
    
    //optionally do something else with it, e.g. wekinator, store data, smart data layer
    //trainWekinatorMsg(theOscMessage);
    //trainWekinatorWithAllSensors();
    
    //printOSCMessage(theOscMessage);
    //oscP5.send(theOscMessage, ActuatorNetAddressList);
    //sendAllSensorData();
  }
  else if(theOscMessage.addrPattern().contains("/actuator")){
    
    int id = messageContainsID(theOscMessage);
    
    if(id == -1)
      sendToAllActuators(theOscMessage);
    else{
      theOscMessage.setAddrPattern(cleanActuatorPattern(theOscMessage));
      sendToOneActuator(theOscMessage,id);
    }
    addToActuatorInputs(theOscMessage.addrPattern(),theOscMessage.arguments()); //put it in the actuator input history
    printOSCMessage(theOscMessage);
  }
  else{
   // print("## Sending OSC Message directly to Wekinator");
    //printOSCMessage(theOscMessage);
   // trainWekinatorMsg(theOscMessage);
  }
}

private void addToActuatorInputs(String osckey, Object[] values){
  if(actuatorInputs.put(osckey,values) == null && fileStarted){
    println("Received a new actuator: ENDING FILE PREMATURELY");
    EndFile(0);
  }
}

private void addToSensorInputs(String osckey, Object[] values){
  if(sensorInputs.put(osckey,values) == null && fileStarted){
    println("Received a new sensor: ENDING FILE PREMATURELY");
    EndFile(0);
  }
}

private int messageContainsID(OscMessage theOscMessage){
  
  String[] addrComponents = theOscMessage.addrPattern().split("/");
  //"_/[actuator]/[id]"s
  
    try 
    { 
            // checking valid integer using parseInt() method 
            return Integer.parseInt(addrComponents[2]); 
    }  
    catch (Exception e) //this means that it is not an integer and then it is meant for all actuators 
    { 
       return -1;
    } 
}

private String cleanActuatorPattern(OscMessage theOscMessage){
  
  String[] addrComponents = theOscMessage.addrPattern().split("/");
  String[] newAddress = new String[addrComponents.length-1];
  //"_/[actuator]/[id]"
  
    try 
    { 
            // checking valid integer using parseInt() method 
            Integer.parseInt(addrComponents[2]); 
            
            for(int i=0, j=0;i<newAddress.length;i++,j++){
              if(i==2) i++;
              newAddress[j] = addrComponents[i];
            }
            
            return join(newAddress,"/");
    }  
    catch (Exception e) //this means that it is not an integer and then it is meant for all actuators 
    { 
       return theOscMessage.addrPattern();
    } 

}


// /sensor/x becomes /[id]/sensor/x
void addSensorValuetoHashMap(OscMessage theOscMessage){
  
  int id = getDeviceId(theOscMessage.netAddress());
  if(id == -1)
    id = connectSensor(theOscMessage.netAddress().address());
  
  //remove the "/sensor" part
  String[] addrComponents = theOscMessage.addrPattern().split("/");
  
  //System.out.println("## PRINTING addrComponents"); 
  //for (String a : addrComponents) 
  //          System.out.println(a); 
   
  String[] address = new String[addrComponents.length-1];
  
  address[0] = Integer.toString(id);
  
  for(int i=2;i<addrComponents.length; i++){ //i starts at 2 to jump past the initial blankspace "" and the word "sensor"
    address[i-1] = addrComponents[i];
  }

  addToSensorInputs(join(address,"/"), theOscMessage.arguments());
}

int getDeviceId(NetAddress address){
 Integer id = DeviceIPs.get(address.address());
 if(id==null) return -1;
 else return id;
}

String getDeviceAddress(int id){

   for (HashMap.Entry<String, Integer> entry : DeviceIPs.entrySet()) {
            if (entry.getValue().equals(id)) {
                return(entry.getKey());
            }
        }
    return null;
}


void sendToOneActuator(OscMessage theOscMessage, int id){
  
  System.out.println("## Sending to one actuator with ID "+ id);
  
  String addr = getDeviceAddress(id);
  if(addr==null){
    System.out.println("## ERROR: Actuator with ID "+ id+ " not found");
    return;
  }
  
  NetAddress actuatorNetAddress = ActuatorNetAddressList.get(addr,myBroadcastPort);
  if(actuatorNetAddress==null){
    System.out.println("## ERROR: Actuator with ID "+ id+ " not found");
    return;
  }
    
  /* create an osc bundle */
  OscBundle myBundle = new OscBundle();
  myBundle.add(theOscMessage);
 
  myBundle.setTimetag(myBundle.now() + 10000);
  /* send the osc bundle, containing 1 osc messages, to all actuators. */
  oscP5.send(myBundle, actuatorNetAddress);
}

void sendToAllActuators(OscMessage theOscMessage){
  
    System.out.println("## Sending to ALL actuators");

  
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

private int connectSensor(String theIPaddress) {
  int id = addIPAddress(theIPaddress);
     if (!SensorNetAddressList.contains(theIPaddress, myBroadcastPort)) {
       SensorNetAddressList.add(new NetAddress(theIPaddress, myBroadcastPort));
       println("### adding "+theIPaddress+" to the sensor list. The ID is "+id);
     } else {
       println("### Sensor "+theIPaddress+" is already connected. The ID is "+id);
     }
     println("### currently there are "+SensorNetAddressList.list().size()+" sensors connected.");
     
     return id;
 }

private int addIPAddress(String IPAddress){
  //HashMap<String, Integer>
  Integer id = DeviceIPs.putIfAbsent(IPAddress, new Integer(indexIP));
  
  if(id==null){ //it is new!
    id= DeviceIPs.get(IPAddress);
    indexIP++;
  }
        
  return id;

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
 
 
private int connectActuator(String theIPaddress) {
     int id = addIPAddress(theIPaddress);
     if (!ActuatorNetAddressList.contains(theIPaddress, myBroadcastPort)) {
       ActuatorNetAddressList.add(new NetAddress(theIPaddress, myBroadcastPort));
       println("### adding "+theIPaddress+" to the actuator list. The ID is "+id);
     } else {
       println("### Actuator "+theIPaddress+" is already connected. The ID is "+id);
     }
     println("### currently there are "+ActuatorNetAddressList.list().size()+" actuators connected.");
     return id;
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
