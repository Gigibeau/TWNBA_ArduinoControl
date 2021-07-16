// Import Libraries
#include <Adafruit_MotorShield.h>
#include <Wire.h>

// Create MotorShield, StepperMotors Objects
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
Adafruit_StepperMotor *myMotor1 = AFMS.getStepper(200, 1);
Adafruit_StepperMotor *myMotor2 = AFMS.getStepper(200, 2);

// Defining parameters
int speed1;   // the current speed for motor 1
int speed2;   // the current speed for motor 2
int xposition;    // the current x position in steps
int yposition;    // the current y position in steps

//============

// Variables necessary for the serial input
const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

// variables to hold the parsed data
char messageFromPC[numChars] = {0};
int firstint = 0;
int secondint = 0;
int thirdint = 0;

boolean newData = false;

//============

void setup() {
    Serial.begin(9600);
    //Serial.println("Arduino is ready");
    //Serial.println();

    // Start MotorShield
    AFMS.begin();

    // Define initial speed
    speed1 = 5;
    speed2 = 5;
    myMotor1->setSpeed(speed1);
    myMotor2->setSpeed(speed2);

    //Set initial position in steps
    xposition = 0;
    yposition = 0;

    // Startup movement (so the coils are hot)
    myMotor1->step(1, BACKWARD, DOUBLE);
    myMotor2->step(1, BACKWARD, DOUBLE);
    
    Serial.println("<Arduino is ready!>");
}

//============

void loop() {
    recvWithStartEndMarkers();
    if (newData == true) {
        strcpy(tempChars, receivedChars);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        parseData();
        executeFunction();
        newData = false;
        //Serial.println("ready for new command");
    }
}

//============

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

//============

void parseData() {      // split the data into its parts

    char * strtokIndx; // this is used by strtok() as an index

    strtokIndx = strtok(tempChars,",");      // get the first part
    firstint = atoi(strtokIndx);     // convert this part to an integer
 
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    secondint = atoi(strtokIndx);     // convert this part to an integer

    strtokIndx = strtok(NULL, ",");
    thirdint = atoi(strtokIndx);     // convert this part to a integer

}

//============

void executeFunction() {
  if (firstint == 1){
    SetSpeed(secondint, thirdint);  // <1, speed in x-direction, speed in y-direction>
  }
  if (firstint == 2){
    MoveXY(secondint, thirdint);   // <2, distance in x-direction, distance in y-direction>
  }
  if (firstint == 3){
    MoveX(secondint, thirdint);   // <3, distance in x-direction, speed in x-direction>
  }
  if (firstint == 4){
    MoveY(secondint, thirdint);   // <4, distance in y-direction, speed in y-direction>
  }
  if (firstint == 5){     
    setOrigin();                  // <5, inconsequential, inconsequential>
  }
  if (firstint == 6){
    returnPosition();             // <6, inconsequential, inconsequential>
  }
  if (firstint == 7){
    returnSpeed();                // <7, inconsequential, inconsequential>
  }
  if (firstint == 8){
    ManualMode();                // <8, inconsequential, inconsequential>
  }
}

//====== Motor Functions ======

// Change the speed of the motors
void SetSpeed(int x, int y){
  speed1 = x;
  speed2 = y;
  myMotor1->setSpeed(speed1);
  myMotor2->setSpeed(speed2);
  Serial.println(String("<") + xposition + String(";") + yposition + String(";y-speed: ") + speed1 + String(" x-speed: ") + speed2 + String(">"));
}

// Move in x and y direction
void MoveXY(int x, int y){
  if (y >= 0) {
    myMotor1->step(y, BACKWARD, DOUBLE);  // up
  }
  else {
    myMotor1->step(abs(y), FORWARD, DOUBLE);    // down
  }

  if (x >= 0) {
    myMotor2->step(x, BACKWARD, DOUBLE);    // right
  }
  else {
    myMotor2->step(abs(x), FORWARD, DOUBLE);  // left
  }

  xposition = xposition + x;
  yposition = yposition + y;
  Serial.print(String("<Moved to x: ") + xposition + String(" y: ") + yposition);
  Serial.println(String(" Current speed x: ") + speed1 + String(" y: ") + speed2 + String(">"));
}

// Move in x direction
void MoveX(int x, int y){
  x = x * 1.7;
  speed1 = y;
  myMotor2->setSpeed(y);
  if (x >= 0) {
    myMotor2->step(x, BACKWARD, DOUBLE);
  }
  else {
    myMotor2->step(abs(x), FORWARD, DOUBLE);
  }
  xposition = xposition + x;
  Serial.print(String("<") + xposition + String(";") + yposition + String(";Moved to x: ") + xposition + String(" y: ") + yposition);
  Serial.println(String(" Current speed y: ") + speed1 + String(" x: ") + speed2 + String(">"));
}

// Move in y direction
void MoveY(int x, int y){
  x = x * 1.7;
  speed2 = y;
  myMotor1->setSpeed(y);
  if (x >= 0) {
    myMotor1->step(x, BACKWARD, DOUBLE);
  }
  else {
    myMotor1->step(abs(x), FORWARD, DOUBLE);
  }
  yposition = yposition + x;
  Serial.print(String("<") + xposition + String(";") + yposition + String(";Moved to x: ") + xposition + String(" y: ") + yposition);
  Serial.println(String(" Current speed y: ") + speed1 + String(" x: ") + speed2 + String(">"));
}

// Define current position as origin
void setOrigin(){
  xposition = 0;
  yposition = 0;
  Serial.println(String("<") + xposition + String(";") + yposition + String(";Current position set as new origin.>"));    
}

// Return current position
void returnPosition(){
  Serial.println(String("<x-position: ") + xposition + String(" y-position: ") + yposition + String(">"));
}

// Return current speed
void returnSpeed(){
  Serial.println(String("<y-speed: ") + speed1 + String(" x-speed: ") + speed2 + String(">"));
}

// Manual Mode: Control xy movement by realtime input
void ManualMode(){
  int eg = 1;
  char input = 0;
  Serial.println(String("<") + xposition + String(";") + yposition + String(";Entering ManualMode.>"));
  while (eg == 1){
    if (Serial.available() > 0) {
    input = Serial.read();
   }

   while (input == 'a') {
   //Serial.println(String("<Links.>"));
   myMotor2->step(1, FORWARD, DOUBLE);   //nach links

   if (Serial.available() > 0) {
    input = Serial.read();
   }
   }

      while (input == 'w') {
   //Serial.println(String("<Oben.>"));
   myMotor1->step(1, BACKWARD, DOUBLE);   //nach oben

   if (Serial.available() > 0) {
    input = Serial.read();
   }
   }

      while (input == 's') {
   //Serial.println(String("<Unten.>"));
   myMotor1->step(1, FORWARD, DOUBLE);  //nach unten

   if (Serial.available() > 0) {
    input = Serial.read();
   }
   }

      while (input == 'd') {
   //Serial.println(String("<Rechts.>"));
   myMotor2->step(1, BACKWARD, DOUBLE); //nach rechts

   if (Serial.available() > 0) {
    input = Serial.read();
   }
   }
   
   while (input == 'f') {
   if (Serial.available() > 0) {  //Keine Bewegung
    input = Serial.read();
   }
   }
   if (input == 'e') {
    Serial.println(String("<") + xposition + String(";") + yposition + String(";Exiting ManualMode.>"));
    eg = 0;
   }
   }
 }   
