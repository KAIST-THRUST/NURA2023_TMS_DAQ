#include "daq_setting.h"

float get_pressure(float voltage) {
  // Convert voltage to current (in mA)
  float current = voltage / R_MAGNITUDE * 1000.0; // mA
  return ((current - 4.0) * 68.9476 / 16.0); // bar
}

void print_value_to_serial(unsigned long time) {
  float press_bar, temp_degC, thrust_gram;
  int16_t press_adc_raw_volt;

  press_adc_raw_volt = ADS.readADC(PT_ADC_CH); // pressure raw value reading from ADS1115
  press_bar = get_pressure(ADS.toVoltage(press_adc_raw_volt)); // bar
  temp_degC = tc1.readTempC();
  thrust_gram = scale.get_units(); // gram


  // Print in CSV format into the serial.
  byte buf[18] = {0};
  memcpy(buf, &time, 4);
  memcpy(buf + 4, &press_bar, 4);
  memcpy(buf + 8, &temp_degC, 4);
  memcpy(buf + 12, &thrust_gram, 4);
  memcpy(buf + 16, &press_adc_raw_volt, 2);
  
  Serial.write(buf, 18);
}