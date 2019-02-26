#include <Encoder.h>
#include <EEPROM.h>
const int relay1 = 12;
const int relay2 = 9;

int leftmotorForward = 8;    // pin 8 --- left motor (+) green wire
int leftmotorBackward = 11; // pin 11 --- left motor (-) black wire
int leftmotorspeed = 9;     // pin 9 --- left motor speed signal

int PWM = 0;
int Inverse_PWM = 0;
int level = 0;

Encoder myEnc(2, 7); //  Set up the linear actuator encoder using pins which support interrupts, avoid using pins with LEDs attached i.e. 13
long oldPosition  = -99999; //   intializing it with random negative value
long oldPressure  = -99999; //   intializing it with random negative value
int currentPosition  = -99999; //   intializing it with random negative value
int correction = 0;


const int PressureLocal = A5;// Pressure Sensing 
const int PressureRemote = A4;// Pressure Sensing

const int baseline = 200; //minimum pressure for anything to happen at all, arbitrary value. Could be something to calibrate



// Define the number of samples to keep track of. The higher the number, the
// more the readings will be smoothed, but the slower the output will respond to
// the input. Using a constant rather than a normal variable lets us use this
// value to determine the size of the readings array.
const int numReadings = 100;

int readings[numReadings];      // the readings from the analog input
int readIndex = 0;              // the index of the current reading
int total = 0;                  // the running total
int average = 0;                // the average



void setup() {
  // put your setup code here, to run once:

  pinMode(leftmotorForward, OUTPUT);
  pinMode(leftmotorBackward, OUTPUT);
  pinMode(leftmotorspeed, OUTPUT);

  Serial.begin(9600);
  correction = EEPROMReadInt(0); // reading the last position of motor from EEPROM to later caliberate HallEffect sensor values


  // initialize all the readings to 0:
  for (int thisReading = 0; thisReading < numReadings; thisReading++) {
    readings[thisReading] = 0;
  }
  
  getMiddlePoint();
}

void loop() {
  
  // put your main code here, to run repeatedly:

  long localPressure = analogRead(PressureLocal); //pressure from this one (values from 0 to 1000)
  long remotePressure = analogRead(PressureRemote); //pressure from the other one (values from 0 to 1000)

//  Serial.print(localPressure);
//  Serial.print(";");
//  Serial.println(remotePressure);

  //there needs to be some pressure from both sides, otherwise it shouldn't move at all
  if(localPressure > baseline && remotePressure > baseline){

      int together = localPressure - remotePressure; //calculate the sum of both pressures with range -1000 to 1000, but needs to be adjusted to the baseline

      //Calculate moving average of together the last X samples (e.g. X=10, AVG = 10; low variance;X=10, AVG = 100; high variance)
      movingAverage(together);

      

//      Serial.print(together);
//      Serial.print("; AVG:");
//      Serial.println(average);

//      Serial.print("Together:");
//      Serial.print(together);
      
      
      //newTogether = together x FACTOR. FACTOR = MAX/AVG and //constrain newTogether to valid values
      if(abs(average)>2){ //prevent bouncing
        together = together * (((1000-baseline)/abs(average)));

//        Serial.print("; Corrected:");
//        Serial.print(together);

//        if(together>0){
//          together = constrain(map(together, 160, 10000, 160, 1000-baseline), 160, 1000-baseline);
//        }
//        else{
//          together = constrain(map(together, -10000, 160, -(1000-baseline), 160), -(1000-baseline), 160) ;
//        }

        together = constrain (together, -1000, 1000);

//        Serial.print("; Constrained:");
//        Serial.print(together);
        
      }
      //160 - 128000 
      
//      Serial.print("; AVG:");
//      Serial.println(average);
      
      
      
//      Serial.print(localPressure); //DEBUG
//      Serial.print("-");
//      Serial.print(remotePressure);
//      Serial.print("=");
//      Serial.println(together);
  
      //Serial.println(together); //DEBUG
      //send through Serial
      char c;
      c = (together+1000)/10; //(0-200)
      //Serial.println((together)/10);
      
      Serial.write(c); // sending pressure value through Xbee



      PWM = constrain(map(abs(together), 0, 1000-baseline, 0, 255), 0, 255);
     // Inverse_PWM = constrain(map(abs(together), 1000-baseline, 0, 0, 255), 0, 255);

     
      
  
      if(together > 10){ //the difference between pressures needs to be more than a certain baseline, so that we can also stop the actuators in balance
                
        //retract local
        retractActuator();
        
        //extend remote (i.e. send through bluetooth a PWM to remote)
        //Serial.print("Extracting remote; PWM:"); Serial.print(PWM); Serial.print("Inverse_PWM:"); Serial.println(Inverse_PWM);
      }
      else if(together < -10){

        //extract local
        extendActuator();
        
        //retract remote (i.e. send through bluetooth a PWM to remote)
        //Serial.print("Retracting remote; PWM:"); Serial.print(PWM); Serial.print("Inverse_PWM:"); Serial.println(Inverse_PWM);
      }
      else stopActuator();
  }
  else{
    char c;
    c = (1000)/10; //(0-200)
    Serial.write(c);
   // Serial.println("STOP!");
    stopActuator();
  }

  long newPosition = myEnc.read();  //check the encoder to see if the position has changed
  if (newPosition != oldPosition) {
    oldPosition = newPosition;
    currentPosition = newPosition + correction; //caliberating the motor position
    EEPROMWriteInt(0, currentPosition); //saving motor position in EEPROM
  }
}

void movingAverage(int newValue)
{
  // subtract the last reading:
  total = total - readings[readIndex];
  // read from the sensor:
  readings[readIndex] = newValue;
  // add the reading to the total:
  total = total + readings[readIndex];
  // advance to the next position in the array:
  readIndex = readIndex + 1;

  // if we're at the end of the array...
  if (readIndex >= numReadings) {
    // ...wrap around to the beginning:
    readIndex = 0;
  }

  // calculate the average:
  average = total / numReadings;
}

void getMiddlePoint()
{
   PWM = 255;

  while(1){
    
     long newPosition = myEnc.read()+ correction;  //check the encoder to see if the position has changed
     EEPROMWriteInt(0, newPosition); //saving motor position in EEPROM
      

     if(newPosition > 6100)
     {
        retractActuator();
     }
     else if(newPosition < 6000)
     {
        extendActuator();
     }
     else return;
  }
   
 
  
}

void extendActuator()
{
//  Serial.print("Extending:");
//  Serial.println(PWM);
  analogWrite(9, PWM);
  digitalWrite(11, LOW); // Drives LOW outputs down first to avoid damage
  digitalWrite(8, HIGH);
}

void retractActuator()
{
//  Serial.print("Retracting");
//  Serial.println(PWM);
  analogWrite(9, PWM);
  digitalWrite(8, LOW); // Drives LOW outputs down first to avoid damage
  digitalWrite(11, HIGH);
}

void stopActuator() // Sets speed pins to LOW disabling both motors
{
  
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
