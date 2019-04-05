#include <Encoder.h>
#include <EEPROM.h>

const byte interruptPin = 2;
int val = 0;

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

}





void loop() {

  //read inputs (OSC)
  

  //gotozero();
  
  // put your main code here, to run repeatedly:

  int together = -1001;
  

  if (Serial.available() > 0) {      //checking if any data is available from Xbee
    together = Serial.read()*10;
    together = together - 1000;

//      if(together == 0){
//        stopActuator();
//        return;
//      }
  }
//  else{
//    stopActuator();
//    return;
//  }

  if(together < -1000 || together > 1000){
    //stopActuator();
    return;
  }
  

  
  
      //Serial.println(together); //DEBUG

      PWM = constrain(map(abs(together), 0, 1000-baseline, 0, 255), 0, 255);
      //PWM = constrain(map(abs(together), 1000-baseline, 0, 0, 255), 0, 255);

      if(together > 10){ //the difference between pressures needs to be more than a certain baseline, so that we can also stop the actuators in balance

        //extract remote
        extendActuator();
        //Serial.print("Extracting remote; PWM:"); Serial.print(PWM); Serial.print("Inverse_PWM:"); Serial.println(Inverse_PWM);
         
      }
      else if(together < -10){

        //retract remote
        retractActuator();
       // Serial.print("Retracting remote; PWM:"); Serial.print(PWM); Serial.print("Inverse_PWM:"); Serial.println(Inverse_PWM);
      }
      else stopActuator();

  long newPosition = myEnc.read();  //check the encoder to see if the position has changed
  if (newPosition != oldPosition) {
    oldPosition = newPosition;
    currentPosition = newPosition + correction; //caliberating the motor position
    EEPROMWriteInt(0, currentPosition); //saving motor position in EEPROM
  }
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
    extendActuator();
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

