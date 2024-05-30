# SolidRocketMotor_TMS_DAQ

## Introduction

S/W for DAQ system on solid rocket motor TMS. This S/W is used for gathering measured data during SRM hot-fire test, and logging all measurements in csv file.

The newest version is designed for DAQ system utilizing Teensy 4.1 as its MCU.
You can check the old version of software for Arduino Uno in '_2023version' folder. 

This S/W is based on [Real-Time-Serial-Plotter](https://github.com/KAIST-THRUST/Real-Time-Serial-Plotter/tree/main) by THRUST.


## Features

- Chamber Pressure, Chamber Temperature, and Thrust measurements
- Real-time plotting of data received from a serial port
- Supports multiple data series plotting
- Adjustable plot update rate
- Adjustable maximum number of data points displayed
- Adjustable serial data packet style

## Installation

1. Clone or download this repository to your local machine.
2. Install the required Python packages if they are not installed 
in your local computer.

```bash
pip install pyqtgraph pyserial pyQt5 numpy
```

## Hardware Setup

1. Make sure all of the sensors are connected to DAQ board. If you are not sure about the wiring, please contect to relavent PIC.
2. Remove the one side of jumper wire (orange) that is connected to channel A0 of ADS1115 external ADC module.
3. Connect red and black aligator clip to 12VDC battery to power pressure transducer.
4. Re-connect the one side of jumper wire that is connected to channel A0 of ADS1115.
5. Connect Teensy 4.1 and a laptop using a USB cable.
6. After the experiment, disconnect the jumper wire connected to A0 of ADS1115, then remove 12VDC battery.

## Usage

You need to specify which serial port is going to be used. For example, if the DAQ MCU is connected to COM6 port, set port argument to 'COM6'. Also, you can change the sensor rate (ms) and plot update rate (ms). The example below hears COM6 port. DAQ sensor rate is 10 ms (100Hz), and real time plot update rate is 25 ms (40Hz).

```python
# Test code. Reads 6 values from the serial and plot each data.
# Modify the parameters of the `RealtimePlot` to fit your project.
if __name__ == "__main__":
    # Test code. Reads 6 values from the serial and plot each data.
    # Modify the parameters of the `RealtimePlot` to fit your project.
    datas = [
        "time",
        "chamber_press",
        "chamber_press_adc_raw",
        "chamber_temp",
        "thrust",
    ]  # list of datas.
    plotter = RealTimePlot(data_set=datas, port="COM6", update_rate=25, sensor_rate=10)
    plotter.run()
```
After everything is ready, type following command in your terminal.

```bash
python3 tms_daq_realTimePlot.py
```
