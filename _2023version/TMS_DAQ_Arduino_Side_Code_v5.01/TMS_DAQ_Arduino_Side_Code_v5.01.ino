#include <HX711.h>
#include <max6675.h>
#include <Wire.h>

// Serial Communication Config
const unsigned long BAUD_RATE = 115200;

// Set Sampling Rate
const float SAMPLING_RATE = 80.0; // Hz, for PT and Load Cell
const float SAMPLING_RATE_TEMP = 4.0; // Hz, for two thermocouples. 4 Hz is maximum sampling rate for thermocouple.

// HX711 (Load Cell) Pin Config
HX711 scale;
uint8_t dataPin = 6;
uint8_t clockPin = 7;

// K-type Thermocouple 1 Pin Config
uint8_t SO_1 = 4;              // SO pin of MAX6675
uint8_t CS_1 = 3;             // CS pin on MAX6675
uint8_t SCK_1 = 2;             // SCK pin of MAX6675

// K-type Thermocouple 2 Pin Config
uint8_t SO_2 = 11;              
uint8_t CS_2 = 10;             
uint8_t SCK_2 = 9;

// Thermocouple Reading Config
MAX6675 thermocouple1(SCK_1, CS_1, SO_1); // Initialize Thermocouple 1
MAX6675 thermocouple2(SCK_2, CS_2, SO_2); // Initialize Thermocouple 2

// Pressure Transducer
const uint8_t PT_SENSOR_PIN = A0; // Voltage Reading Pin
const float RESISTOR_VALUE = 200; // Ohm
const float MAX_CURR = 0.02; // Ampere
const float MIN_CURR = 0.004; // Ampere
const float MAX_VOLTAGE = MAX_CURR * RESISTOR_VALUE; // Volt
const float MIN_VOLTAGE = MIN_CURR * RESISTOR_VALUE; // Volt
const float MAX_PRESSURE = 68.9476; // bar (1kpsi)
float LOAD_CELL_CALIBRATION_FACTOR = 86.39632;

// Variables for storing sensor readings
double load, temp1, temp2, pressure;

// Loop Time Measurement Variables
unsigned long start, end, delta;

// For syncronizing sampling rate
const float SAMPLING_PERIOD_IN_SEC  = 1.0 / SAMPLING_RATE; // second
const float SAMPLING_PERIOD_TEMP_IN_SEC = 1.0 / SAMPLING_RATE_TEMP; // second

const unsigned int interval = (int) (SAMPLING_PERIOD_IN_SEC * 1000); // milli-seconds
const unsigned int interval_temp = (int) (SAMPLING_PERIOD_TEMP_IN_SEC * 1000); // milli-seconds
unsigned long currentMicros, prevTime, prevTime_temp;

// Time Stamp
unsigned long DAQ_startTime;
unsigned long timeStamp;

void setup()
{
  // Begin Serial Communication with computer
  Serial.begin(BAUD_RATE);

  // Setup Load Cell and tare the scale
  scale.begin(dataPin, clockPin);
  scale.set_scale(LOAD_CELL_CALIBRATION_FACTOR);       // TODO you need to calibrate this yourself.
  scale.tare();  // reset the scale to zero = 0
  delay(3000); // Wait for 3 seconds to stablize sensors

  DAQ_startTime = millis();
  prevTime = DAQ_startTime;
  prevTime_temp = DAQ_startTime;
}

void loop()
{
  currentMicros = millis(); // get the current time
  read_load_pressure_loop();
  read_temp_loop();
}

void read_load_pressure_loop(void) {
  if (currentMicros - prevTime >= interval) // test whether the interval for reading load and pressure has elapsed
  {
    timeStamp = millis() - DAQ_startTime;
    load = scale.get_units(); // Read Load_Cell, gram
    pressure = readPressure(); // Read Pressure Transducer, bar
    
    // Serial.print("TIME (ms): ");
    // Serial.print(timeStamp);
    // Serial.print(" LOAD, PRESSURE: ");
    // Serial.print(load);
    // Serial.print(" ");
    // Serial.println(pressure);

    sendLoadPressureToPC(&timeStamp, &load, &pressure);

    prevTime = currentMicros; // After reading two sensor values, set the prevTime.
  }
}

void read_temp_loop(void) {
  if (currentMicros - prevTime_temp >= interval_temp) {
    timeStamp = millis() - DAQ_startTime;
    temp1 = thermocouple1.readCelsius(); // Read thermocouple 1, degC
    temp2 = thermocouple2.readCelsius(); // Read thermocouple 2, degC

    // Serial.print("TIME (ms): ");
    // Serial.print(timeStamp);
    // Serial.print(", TEMP1: ");
    // Serial.print(temp1);
    // Serial.print(", TEMP2: ");
    // Serial.println(temp2);

    sendTempToPC(&timeStamp, &temp1, &temp2);

    prevTime_temp = currentMicros;
  }
}

float readPressure(void) {
  unsigned int adc_reading = analogRead(PT_SENSOR_PIN);
  float voltage = adc_reading * (5.0 / 1023.0); // Voltage of PT_SENSOR_PIN
  float gage_pressure = (voltage - MIN_VOLTAGE) * (MAX_PRESSURE / (MAX_VOLTAGE - MIN_VOLTAGE)); // barg
  return gage_pressure; // return gage pressure in the unit of bar
}

void sendLoadPressureToPC(unsigned long* timeStamp, double* load, double* pressure) {
  // Send load and pressure with corresponding timestamp to PC
  byte* timeData = (byte*)(timeStamp);
  byte* loadData = (byte*)(load);
  byte* pressureData = (byte*)(pressure);
  byte buf[13] = {0,
                timeData[0], timeData[1], timeData[2], timeData[3], 
                loadData[0], loadData[1], loadData[2], loadData[3],
                pressureData[0], pressureData[1], pressureData[2], pressureData[3]};
  Serial.write(buf, 13);
}

void sendTempToPC(unsigned long* timeStamp, double* temp1, double* temp2) {
  // Send two thermocouple readings with corresponding timestamp to PC
  byte* timeData = (byte*)(timeStamp);
  byte* temp1Data = (byte*)(temp1);
  byte* temp2Data = (byte*)(temp2);
  byte buf[13] = {255,
                timeData[0], timeData[1], timeData[2], timeData[3], 
                temp1Data[0], temp1Data[1], temp1Data[2], temp1Data[3],
                temp2Data[0], temp2Data[1], temp2Data[2], temp2Data[3]};
  Serial.write(buf, 13);
}