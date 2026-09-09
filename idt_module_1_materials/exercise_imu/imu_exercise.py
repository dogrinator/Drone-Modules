#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMU exercise
# Copyright (c) 2015-2024 Kjeld Jensen kjen@mmmi.sdu.dk kj@kjen.dk

##### Insert initialize code below ###################

## Uncomment the file to read ##
# fileName = "imu_razor_data_pitch_55deg.txt"
# fileName = "imu_razor_data_pitch_55deg.txt"
# fileName = "imu_razor_data_roll_65deg.txt"
fileName = "imu_razor_data_yaw_90deg.txt"

## IMU type
# imuType = 'vectornav_vn100'
imuType = "sparkfun_razor"

## Variables for plotting ##
showPlot = True
plotDataPitch = []
plotDataRoll = []
plotFiltDataPitch = []
plotFiltDataRoll = []

## Initialize your variables here ##
pitch = 0.0
roll = 0.0

######################################################

# import libraries
from math import pi, sqrt, atan2
import matplotlib.pyplot as plt
import math

# open the imu data file
f = open(fileName, "r")

# initialize variables
count = 0


# Define functions
def acc2euler(ax, ay, az):
    pitch = atan2(ay, sqrt(ax**2 + az**2))
    roll = atan2(-ax, az)
    return [pitch, roll]


class Gyro2euler:
    def __init__(self, ts, ang_x=0.0, ang_y=0.0, ang_z=0.0):
        self.ang_x = ang_x
        self.ang_y = ang_y
        self.ang_z = ang_z
        self.ts = ts

    def update(self, gyro_x, gyro_y, gyro_z):
        self.ang_x += gyro_x * self.ts
        self.ang_y += gyro_y * self.ts
        self.ang_z += gyro_z * self.ts
        return [self.ang_x, self.ang_y, self.ang_z]


class LowPassFilter:
    def __init__(self, cutoff_freq, dt, initial_value=0.0):
        rc = 1.0 / (2.0 * math.pi * cutoff_freq)
        self.alpha = dt / (rc + dt)
        self.y = initial_value

    def update(self, x):
        self.y += self.alpha * (x - self.y)
        return self.y


# looping through file

for line in f:
    count += 1

    # split the line into CSV formatted data
    line = line.replace("*", ",")  # make the checkum another csv value
    csv = line.split(",")

    # keep track of the timestamps
    ts_recv = float(csv[0])
    if count == 1:
        ts_now = ts_recv  # only the first time
    ts_prev = ts_now
    ts_now = ts_recv

    if imuType == "sparkfun_razor":
        # import data from a SparkFun Razor IMU (SDU firmware)
        acc_x = int(csv[2]) / 1000.0 * 4 * 9.82
        acc_y = int(csv[3]) / 1000.0 * 4 * 9.82
        acc_z = int(csv[4]) / 1000.0 * 4 * 9.82
        gyro_x = int(csv[5]) * 1 / 14.375 * pi / 180.0
        gyro_y = int(csv[6]) * 1 / 14.375 * pi / 180.0
        gyro_z = int(csv[7]) * 1 / 14.375 * pi / 180.0
    elif imuType == "vectornav_vn100":
        # import data from a VectorNav VN-100 configured to output $VNQMR
        acc_x = float(csv[9])
        acc_y = float(csv[10])
        acc_z = float(csv[11])
        gyro_x = float(csv[12])
        gyro_y = float(csv[13])
        gyro_z = float(csv[14])

    ##### Insert loop code below #########################

    # Variables available
    # ----------------------------------------------------
    # count		Current number of updates
    # ts_prev	Time stamp at the previous update
    # ts_now	Time stamp at this update
    # acc_x		Acceleration measured along the x axis
    # acc_y		Acceleration measured along the y axis
    # acc_z		Acceleration measured along the z axis
    # gyro_x	Angular velocity measured about the x axis
    # gyro_y	Angular velocity measured about the y axis
    # gyro_z	Angular velocity measured about the z axis

    ## Insert your code here ##
    # [pitch, roll] = acc2euler(acc_x, acc_y, acc_z)

    if count == 2:
        # init of filter
        freq = 1.5
        dt = ts_now - ts_prev
        lpFilterP = LowPassFilter(freq, dt, pitch * 180.0 / pi)
        lpFilterR = LowPassFilter(freq, dt, roll * 180.0 / pi)
        gyro2euler = Gyro2euler(dt)

    if count >= 2:
        [pitch, roll, yaw] = gyro2euler.update(gyro_x, gyro_y, gyro_z)

        # in order to show a plot use this function to append your value to a list:
        plotDataPitch.append(pitch * 180.0 / pi)
        plotDataRoll.append(yaw * 180.0 / pi)

        # filt data
        # plotFiltDataPitch.append(lpFilterP.update(plotDataPitch[-1]))
        # plotFiltDataRoll.append(lpFilterR.update(plotDataRoll[-1]))

    ######################################################

# closing the file
f.close()

# show the plot
if showPlot == True:
    fig, ax = plt.subplots(1, 2)
    ax[0].plot(plotDataPitch)
    ax[0].plot(plotFiltDataPitch)
    ax[0].set_title("Pitch")
    ax[1].plot(plotDataRoll)
    ax[1].plot(plotFiltDataRoll)
    ax[1].set_title("Roll")
    plt.savefig("imu_exerciseRoll_plot.png")
    plt.show()
