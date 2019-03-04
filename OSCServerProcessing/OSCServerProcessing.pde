/**
 * oscP5message by andreas schlegel
 * example shows how to create osc messages.
 * oscP5 website at http://www.sojamo.de/oscP5
 */
 
import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress myRemoteLocation;

float X;
float Y;
int ledState = 0; 

void setup() {
  size(600,600);
  frameRate(25);
  /* start oscP5, listening for incoming messages at port 12000 */
  oscP5 = new OscP5(this,5008);
  
  /* myRemoteLocation is a NetAddress. a NetAddress takes 2 parameters,
   * an ip address and a port number. myRemoteLocation is used as parameter in
   * oscP5.send() when sending osc packets to another computer, device, 
   * application. usage see below. for testing purposes the listening port
   * and the port of the remote location address are the same, hence you will
   * send messages back to this sketch.
   */
  myRemoteLocation = new NetAddress("192.168.11.198",5006);
}


void draw() {
  float XCord = map(X, -2, 2, 0, 600);
  float YCord = map(Y, -2, 2, 0, 600);
  if (mousePressed) {
    background(255);
  } else {
    background(0);
  }
  
  
  fill(255);
  ellipse(XCord, YCord, 50, 50);
}

void mousePressed() {
  /* in the following different ways of creating osc messages are shown by example */
  OscMessage myMessage = new OscMessage("/led");
  
  myMessage.add(ledState); /* add an int to the osc message */
  ledState=1-ledState;

  /* send the message */
  oscP5.send(myMessage, myRemoteLocation); 
}


/* incoming osc message are forwarded to the oscEvent method. */
void oscEvent(OscMessage theOscMessage) {
  /* check if theOscMessage has the address pattern we are looking for. */
  
  if(theOscMessage.checkAddrPattern("/acc")==true) {
    /* check if the typetag is the right one. */
    if(theOscMessage.checkTypetag("sfsfsf")) {
      /* parse theOscMessage and extract the values from the osc message arguments. */
      float firstValue = theOscMessage.get(1).floatValue(); 
      X=firstValue;
      float secondValue = theOscMessage.get(3).floatValue();
      Y=secondValue;
      float thirdValue = theOscMessage.get(5).floatValue();
      print("### received an osc message /acc with typetag sfsfsf.");
      println(" values: "+firstValue+", "+secondValue+", "+thirdValue);
      return;
    }  
  } 
  println("### received an osc message. with address pattern "+theOscMessage.addrPattern());
  redraw();
  //println("### received an osc message. with address pattern "+theOscMessage.typetag());
}
