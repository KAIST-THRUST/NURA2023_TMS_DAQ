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