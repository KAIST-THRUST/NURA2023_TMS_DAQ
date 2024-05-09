import os
from threading import Thread
import serial
import time
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import struct
from datetime import datetime
import pandas as pd

# DAQ Config
TERMINAL_LOG = True # True: Print real-time sensor value on terminal, False: not verbose
LOG_FOLDER = "./log" # acquired data will be saved into ./log directory

# Note: DAQ sampling rates are designated in the arduino code.

# Communication Config
PORT_NAME = 'COM7' # Change properly. Designate correct port of arduino
BAUDRATE = 115200 # Recommend 115200 as default

# DO NOT MODIFY BELOW
PACKET_SIZE = 13 # packet size (bytes), packet structure: 1 + 4 + 4 + 4 (tag + timeStamp + Sensor1 + Sensor2)
NUM_SENSORS = 4 # number of plots, i.e., number of sensors
PLOT_RATE = 60 # Hz, plot update rate.
PLOT_LENGTH = 50 # How much data points you want to see from each fram of the plot animation

class SerialData:
    def __init__(self, serialPort = '/dev/ttyUSB0', serialBaud = 115200, plotLength = 100, dataNumBytes = 13, numPlots = 4):
        
        # Communication and Background Thread Related
        self.dataNumBytes = dataNumBytes
        self.packet = bytearray(dataNumBytes)
        self.isRun = True
        self.isReceiving = False
        self.thread = None

        # CSV Related
        self.csvData_Thrust_Pressure = [["Time", "Thrust", "Pressure"]]
        self.csvData_Temp = [["Time", "Temp1", "Temp2"]]

        # Data Plot Related
        self.plotMaxLength = plotLength
        self.numPlots = numPlots # i.e., num of sensors
        self.plotTimer = 0 # millisec
        self.previousTimer = 0 # millisec

        # Real-time Plot Related
        self.recentSensorValues = [0, 0, 0, 0] # store most recent sensor values
        # self.recentTimeStamps = [0, 0, 0, 0] # store most recent timestamp values

        self.plotBuffer = []
        # self.timeStampBuffer = []
        for i in range(numPlots):
            self.plotBuffer.append(deque([0] * plotLength, maxlen = plotLength))
            # self.timeStampBuffer.append(deque([0] * plotLength, maxlen = plotLength))

        # Make connection between arduino and python
        print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout = 4)
            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
            quit()

    def readSerialStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()
            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.1)
    
    def updatePlot(self, frame, lines, lineValueTexts, lineLabels, timeTexts):
        currentTimer = time.perf_counter()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000)  # millisec, the first reading will be erroneous
        self.previousTimer = currentTimer
        timeTexts[0].set_text('Plot Interval = ' + str(self.plotTimer) + 'ms')
        
        for i in range(self.numPlots):
            # timeStamp = self.recentTimeStamps[i] 
            value = self.recentSensorValues[i]
            # self.timeStampBuffer[i].append(timeStamp) # get the latest timestamp and append it to our array
            self.plotBuffer[i].append(value) # get the latest data point and append it to our array

            # update data to be plotted
            lines[i].set_data(range(self.plotMaxLength), self.plotBuffer[i])
            lineValueTexts[i].set_text('[' + lineLabels[i] + '] = ' + f"{value:.4f}")

        return (lines[0], lines[1], lines[2], lines[3], lineValueTexts[0], lineValueTexts[1], lineValueTexts[2], lineValueTexts[3], timeTexts[0])


    def backgroundThread(self):    # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        while (self.isRun):
            self.serialConnection.readinto(self.packet)
            self.isReceiving = True
            tag = self.packet[0] # 0x00 or 0xff

            if tag == 0x00: # Tag 0x00 => timeStamp, thrust, pressure
                timeStamp = struct.unpack('I', self.packet[1:5])[0] / 1000 # unit: second
                thrust = struct.unpack('f', self.packet[5:9])[0] * (9.8 / 1000) # unit: Newton
                pressure = struct.unpack('f', self.packet[9:13])[0] # unit: bar
                
                if TERMINAL_LOG: # Print real-time value on terminal
                    print("Time, Thrust, Pressure", timeStamp, "sec,", thrust, "N,", pressure, "bar")

                # accumulate sensor values to the list to be saved into csv file.
                self.csvData_Thrust_Pressure.append([timeStamp, thrust, pressure])

                # update most recent sensor values and time stamp
                # self.recentTimeStamps[0] = timeStamp
                # self.recentTimeStamps[1] = timeStamp
                self.recentSensorValues[0] = thrust
                self.recentSensorValues[1] = pressure

            elif tag == 0xff: # Tag 0xff => timeStamp, temp1, temp2
                timeStamp = struct.unpack('I', self.packet[1:5])[0] / 1000 # unit: second
                temp1 = struct.unpack('f', self.packet[5:9])[0] # unit: degC
                temp2 = struct.unpack('f', self.packet[9:13])[0] # unit: degC

                if TERMINAL_LOG:  # Print real-time value on terminal
                    print("Time, Temp1, Temp2", timeStamp, "sec,", temp1, "degC,", temp2, "degC")

                # accumulate sensor values to the list to be saved into csv file.
                self.csvData_Temp.append([timeStamp, temp1, temp2])

                # update most recent sensor values and time stamp
                # self.recentTimeStamps[2] = timeStamp
                # self.recentTimeStamps[3] = timeStamp
                self.recentSensorValues[2] = temp1
                self.recentSensorValues[3] = temp2

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')
        saveToCsv(self.csvData_Thrust_Pressure, "thrust_pressure")
        saveToCsv(self.csvData_Temp, "temperature")

def saveToCsv(dataList, fileName):   
    # ct stores current time
    ct = datetime.now()
    year = ct.strftime("%Y")
    month = ct.strftime("%m")
    day = ct.strftime("%d")
    time = ct.strftime("%H%M%S")
    timeName = f"{year}_{month}_{day}_{time}"

    # Create directory if data log folder does not exist
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
        print(f'Created new directory "{LOG_FOLDER}"')
    
    # Save dataList to csv file
    df1 = pd.DataFrame(dataList)
    df1.to_csv(f'{LOG_FOLDER}/{timeName}_{fileName}.csv')

    print(f'Successfully stored {fileName} data.')

def makeFigure(numSubplot, xLims, yLims, lineLabelText, title, style):
    fig = plt.figure()
    axes = []
    lines = []
    timeTexts = []
    lineValueTexts = []
    for i in range(numSubplot):
        ax = fig.add_subplot(2, 2, i+1)
        ax.set_title(title[i])
        ax.set_xlabel("Sample")
        ax.set_ylabel("Value")
        ax.set_xlim(xLims[i])
        ax.set_ylim(yLims[i])
        line = ax.plot([], [], style[i], label=lineLabelText[i])[0]
        timeText = ax.text(0.50, 0.95, '', transform=ax.transAxes)
        lineValueText = ax.text(0.50, 0.90, '', transform=ax.transAxes)
        
        axes.append(ax)
        lines.append(line)
        timeTexts.append(timeText)
        lineValueTexts.append(lineValueText)

    return fig, axes, lines, timeTexts, lineValueTexts

def main():
    s = SerialData(PORT_NAME, BAUDRATE, PLOT_LENGTH, PACKET_SIZE, NUM_SENSORS)  # initializes all required variables
    s.readSerialStart()  # starts background thread. continuously acquire sensor values
    
    # Real-time plot config
    pltInterval = int((1/PLOT_RATE) * 1000) # Period at which the plot animation updates [ms]
    lineLabelText = ['Thrust (N)', 'Pressure (barg)', 'Temp1 (degC)', 'Temp2 (degC)']
    title = ['Thrust', 'PT01', 'TT01', 'TT02']
    xLimit = [(0, PLOT_LENGTH), (0, PLOT_LENGTH), (0, PLOT_LENGTH), (0, PLOT_LENGTH)]
    yLimit = [(0, 300), (-20, 50), (0, 1800), (0, 800)]
    style = ['k-', 'b-', 'g-', 'r-']    # linestyles for the different plots

    fig, axes, lines, timeTexts, lineValueTexts = makeFigure(s.numPlots, xLimit, yLimit, lineLabelText, title, style)
    fig.suptitle("TMS DAQ")
    anim = animation.FuncAnimation(fig, s.updatePlot, fargs = (lines, lineValueTexts, lineLabelText, timeTexts), interval = pltInterval, blit = True, repeat = False, cache_frame_data = False)
    plt.show()

    s.close() # close serial connection


if __name__ == '__main__':
    main()