#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMU exercise
# Copyright (c) 2015-2024 Kjeld Jensen kjen@mmmi.sdu.dk kj@kjen.dk

##### Insert initialize code below ###################

## Uncomment the file to read ##
# fileName = "imu_razor_data_static.txt"
# fileName = "imu_razor_data_pitch_55deg.txt"
# fileName = "imu_razor_data_roll_65deg.txt"
fileName = 'imu_razor_data_yaw_90deg.txt'

## IMU type
# imuType = 'vectornav_vn100'
imuType = "sparkfun_razor"

## Variables for plotting ##
showPlotAcc = False
showPlotGyro = True

plotDataPitch = []
plotDataRoll = []
plotFiltDataPitch = []
plotFiltDataRoll = []
dataGyroAngle_x = []
dataGyroAngle_y = []
dataGyroAngle_z = []

## Initialize your variables here ##
pitch = 0.0
roll = 0.0
gyro_angle_x = 0
gyro_angle_y = 0
gyro_angle_z = 0

gyro_bias_angle_x = 0
gyro_bias_angle_y = 0
gyro_bias_angle_z = 0

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


class LowPassFilter:
    def __init__(self, cutoff_freq, initial_value=0.0):
        self.rc = 1.0 / (2.0 * math.pi * cutoff_freq)
        self.y = initial_value

    def update(self, x, dt):
        self.alpha = dt / (self.rc + dt)
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
    [pitch, roll] = acc2euler(acc_x, acc_y, acc_z)

    dt = ts_now - ts_prev

    if count == 100:
        gyro_bias_angle_x = gyro_angle_x / count
        gyro_bias_angle_y = gyro_angle_y / count
        gyro_bias_angle_z = gyro_angle_z / count
        gyro_angle_x = 0
        gyro_angle_y = 0
        gyro_angle_z = 0

    gyro_angle_x += gyro_x * dt - gyro_bias_angle_x
    gyro_angle_y += gyro_y * dt - gyro_bias_angle_y
    gyro_angle_z += gyro_z * dt - gyro_bias_angle_z



    if count == 2:
        # init of filter
        freq = 1  # Hz
        
        lpFilterP = LowPassFilter(freq, pitch * 180.0 / pi)
        lpFilterR = LowPassFilter(freq, roll * 180.0 / pi)

    # in order to show a plot use this function to append your value to a list:
    plotDataPitch.append(pitch * 180.0 / pi)
    plotDataRoll.append(roll * 180.0 / pi)

    dataGyroAngle_x.append(gyro_angle_x * 180.0 / pi)
    dataGyroAngle_y.append(gyro_angle_y * 180.0 / pi)
    dataGyroAngle_z.append(gyro_angle_z * 180.0 / pi)

    if count >= 2:
        # filt data
        plotFiltDataPitch.append(lpFilterP.update(plotDataPitch[-1], dt))
        plotFiltDataRoll.append(lpFilterR.update(plotDataRoll[-1], dt))

    ######################################################

# closing the file
f.close()

# show the plot
# show the plot
if showPlotAcc == True:
    fig, ax = plt.subplots(2, 2, figsize=(12, 8))
    
    # Pitch
    ax[0, 0].plot(plotDataPitch)
    ax[0, 0].set_title("Pitch")
    ax[0, 0].set_ylabel("pitch [deg]")
    ax[0, 0].set_xlabel("n samples")
    
    ax[0, 1].plot(plotFiltDataPitch)
    ax[0, 1].set_title("Pitch gefiltert")
    ax[0, 1].set_ylabel("pitch [deg]")
    ax[0, 1].set_xlabel("n samples")
    
    # Roll
    ax[1, 0].plot(plotDataRoll)
    ax[1, 0].set_title("Roll")
    ax[1, 0].set_ylabel("roll [deg]")
    ax[1, 0].set_xlabel("n samples")
    
    ax[1, 1].plot(plotFiltDataRoll)
    ax[1, 1].set_title("Roll gefiltert")
    ax[1, 1].set_ylabel("roll [deg]")
    ax[1, 1].set_xlabel("n samples")
    
    plt.tight_layout()
    plt.savefig("imu_exerciseRoll_plot.png")
    plt.show()

if showPlotGyro == True:
    fig, ax = plt.subplots(3, 1, figsize=(12, 8))
    
    # Gyro Angle X
    ax[0].plot(dataGyroAngle_x)
    ax[0].set_title("Gyro Angle X")
    ax[0].set_ylabel("angle [deg]")
    ax[0].set_xlabel("n samples")
    
    # Gyro Angle Y
    ax[1].plot(dataGyroAngle_y)
    ax[1].set_title("Gyro Angle Y")
    ax[1].set_ylabel("angle [deg]")
    ax[1].set_xlabel("n samples")
    
    # Gyro Angle Z
    ax[2].plot(dataGyroAngle_z)
    ax[2].set_title("Gyro Angle Z")
    ax[2].set_ylabel("angle [deg]")
    ax[2].set_xlabel("n samples")
    
    plt.tight_layout()
    plt.savefig("imu_exerciseGyroAngle_plot.png")
    plt.show()
