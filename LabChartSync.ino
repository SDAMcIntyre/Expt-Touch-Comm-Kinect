// SIGNAL VARIABLES
const int signalPins[8] = {0,1,2,3,4,5,6,7};
int signalNo = 0;
const long lagTime = 3064; // ms

// SERIAL COMMUNICATION VARIABLES
String pythonSays;            // for reading commands from python
const bool echoSerial = true; //send back to python any commands received
const int serialBaudRate = 9600; // should match python
const int serialTimeOut = 10; // ms

void setup() {
  for (int i=0; i<8; i++) {
    pinMode(signalPins[i],OUTPUT);
    digitalWrite(signalPins[i],LOW);
  }
  Serial.begin(serialBaudRate);
  Serial.setTimeout(serialTimeOut);

}

void loop() {
  while (Serial.available() <= 0) {
    // wait for serial input
  }
  
  // get instructions from python over serial connection
  pythonSays = Serial.readString();
  
  // CHECK SERIAL CONNECTION
  if (pythonSays == "ping") {
    Serial.println("ack");

  // SIGNALS
  } else if (pythonSays == "signal") {
    signalNo = serial_get_int(echoSerial);
    delay(lagTime);
    digitalWrite(signalPins[signalNo],HIGH);
    delay(1000);
    digitalWrite(signalPins[signalNo],LOW);

  // UNRECOGNISED INSTRUCTIONS
  } else {
    Serial.print("I don't understand: ");
    Serial.println(pythonSays);
  }  

}

// FUNCTIONS

int serial_get_int(boolean echo){
  if (echo) Serial.println(pythonSays);
  int serialInt;
  while (Serial.available() <= 0){
    // wait
  }
  serialInt = Serial.parseInt();
  if (echo) Serial.println(serialInt);
  return serialInt;
}
