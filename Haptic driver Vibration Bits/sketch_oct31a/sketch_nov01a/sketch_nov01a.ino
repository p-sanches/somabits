
#include <Wire.h>
#include "Adafruit_DRV2605.h"

int maxPot = 1023; //Use if potentiometer is connected to 5V pin
//int maxPot = 666;  //Use if potentiometer is connected to 3.3V pin

Adafruit_DRV2605 drv;
uint8_t effect = 1;

int pot1Pin = 1;    // select the input pin for the potentiometer
int pot2Pin = 0;    // select the input pin for the potentiometer

int pot1Val = 0;       // variable to store the value coming from the sensor
int pot2Val = 0;
int curvalue1 = -1;
int curvalue2 = -1;

int vibeIntensity = 0;
int vibeDelay = 0;

void setup() {
  
  //pinMode(ledPin, OUTPUT);  // declare the ledPin as an OUTPUT

  Serial.begin(9600);
  Serial.println("DRV and Potentiometer");
  drv.begin();
  drv.useLRA(); //comment if using ERM


  // Set Real-Time Playback mode
  drv.setMode(DRV2605_MODE_REALTIME);

}

void loop() {
  pot1Val = analogRead(A1);    // read the value from the potentiometer 1
  pot2Val = analogRead(A0);    // read the value from the potentiometer 2

// Serial.print("Pot 1 before mapping:");
// Serial.println(pot1Val);
//  Serial.print("Pot 2 before mapping:");
//  Serial.println(pot2Val);
  
  pot1Val = map(pot1Val, 0, maxPot, 0, 127);
  pot2Val = map(pot2Val, 0, maxPot, 0, 500);

// Serial.print("Pot 1 after mapping:");
// Serial.println(pot1Val);
//  Serial.print("Pot 2 after mapping:");
//  Serial.println(pot2Val);
  

  vibeIntensity = pot1Val;
  vibeDelay = pot2Val;
  
//  //potentiometer 1
//  if((pot1Val + 2) <= curvalue || (pot1Val - 2) >= curvalue){
//      Serial.print("Potentiometer 1 changed");
//      Serial.println(pot1Val);
//
//      vibeIntensity = pot1Val;
//      
//    }
//    
//    curvalue1 = pot1Val;
//  }
//
//
//  //potentiometer 2
//  if((pot2Val + 2) <= curvalue2 || (pot2Val - 2) >= curvalue2){
//      Serial.print("Potentiometer 2 changed");
//      Serial.println(pot2Val);
//
//      vibeDelay = pot2Val;
//      
//    }
//    
//    curvalue1 = pot1Val;
//  }
  
  drv.setRealtimeValue(vibeIntensity);
  delay(vibeDelay);

   // play the effect!
  //drv.go();

//  if (rtp_index < sizeof(rtp_current)/sizeof(rtp_current[0])) {
//    drv.setRealtimeValue(rtp_current[rtp_index]);
//    rtp_index++;
//    delay(rtp_current[rtp_index]);
//    rtp_index++;
//  } else {
//    drv.setRealtimeValue(0x00);
//    //delay(1000);
//    rtp_index = 0;
//  }
}
