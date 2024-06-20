#ifndef DAQ_SETTING_H
#define DAQ_SETTING_H

#include <ADS1X15.h>
#include <HX711.h>
#include <MAX6675.h>

// Modify the constants here.
/*********************************************************************/
#define SERIAL_BAUDRATE 115200 // serial communication baud rate

#define PT_ADC_CH 0  // ADS1115 ADC channel that corresponds to pressure transducer
#define TT1_CS 36 // MAX6675 Thermocouple 1 chip select
#define TT2_CS 37 // MAX6675 Thermocouple 2 chip select
#define HX711_DATA_PIN 6 // HX711 Data Pin number
#define HX711_CLK_PIN 7 // HX711 Clock Pin number

#define ADS1115_ADDR 0x48 // ADS1115 I2C address, default is 0x48.
#define R_MAGNITUDE 150 // ohm, shunt resistor resistance

#define SENSOR_RATE 10     // sensor rate, in milliseconds

#define LOAD_CELL_CAL_FACTOR  86.39632 // load cell calibration factor
/*********************************************************************/

void print_value_to_serial(unsigned long time);

ADS1115 ADS(ADS1115_ADDR); // Pressure Transducer 4-20mA -> shunt resistor -> ADC // Thermocouple analog reading -> ADC
HX711 scale; // loadcell
MAX6675 tc1(TT1_CS);
MAX6675 tc2(TT2_CS);

#endif
