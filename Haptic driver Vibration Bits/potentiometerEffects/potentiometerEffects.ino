
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

int vibeEffect = 0;
int vibeIntensity = 0;

boolean on;


int myEffects[6];

void setup() {
  
  //pinMode(ledPin, OUTPUT);  // declare the ledPin as an OUTPUT

  Serial.begin(9600);
  Serial.println("DRV and Potentiometer");
  drv.begin();
  drv.useLRA(); //comment if using ERM


  // Set Real-Time Playback mode
  //drv.setMode(DRV2605_MODE_REALTIME);
  drv.setMode(DRV2605_MODE_INTTRIG); 

  on = true;

  myEffects[0] = 9;
  myEffects[1] = 51;
  myEffects[2] = 57;
  myEffects[3] = 63;
  myEffects[4] = 69;
  myEffects[5] = 75;

}

void loop() {
  pot1Val = analogRead(A1);    // read the value from the potentiometer 1
  pot2Val = analogRead(A0);    // read the value from the potentiometer 2

 
  
  //potentiometer 1
  if((pot1Val + 2) <= curvalue1 || (pot1Val - 2) >= curvalue1){
      

      vibeEffect = myEffects[map(pot1Val, 0, maxPot, 0, 5)];

      Serial.print("Potentiometer 1 changed to make the effect");
      Serial.println(vibeEffect);
      
    }
    
    curvalue1 = pot1Val;
  


  //potentiometer 2
  if((pot2Val + 2) <= curvalue2 || (pot2Val - 2) >= curvalue2){
      

       vibeIntensity = map(pot2Val, 0, maxPot, 0, 6);

      Serial.print("Potentiometer 2 changed for intensity");
      Serial.println(vibeIntensity);
      
    }
    
    curvalue1 = pot1Val;


    drv.setWaveform(0, vibeEffect-vibeIntensity);  // play effect 
    drv.setWaveform(1, 0);       // end waveform
    // play the effect!
    drv.go();
    delay(500);
  

//  
//  if(on==true){
//    // set the effect to play
//  drv.setWaveform(0, vibeEffect);  // play effect 
//  drv.setWaveform(1, 0);       // end waveform
//  // play the effect!
//  drv.go();
//  //delay(100);
//    on = false;
//  }
//  else {
//    drv.setWaveform(0, 0);
//    delay(vibeDelay);
//    on = true;
//
// Serial.println("OFF");
//
//  }


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
