#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMU exercise
# Copyright (c) 2015-2024 Kjeld Jensen kjen@mmmi.sdu.dk kj@kjen.dk

##### Insert initialize code below ###################

## Uncomment the file to read ##
# fileName = "imu_razor_data_static.txt"
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
plotAccPitch = []
plotAccRoll = []
plotDataYaw = []
plotTime = []

# Lower cutoff means smoother accelerometer angles, but more lag.
cutoff_freq = 1.5
# Use a separate stationary recording: some motion files start moving immediately.
calibrationFile = "imu_razor_data_static.txt"

## Initialize your variables here ##
pitch = 0.0
roll = 0.0

######################################################

# import libraries
from math import pi, sqrt, atan2
import matplotlib.pyplot as plt
import math
from pathlib import Path

# open the imu data file
data_dir = Path(__file__).resolve().parent
f = open(data_dir / fileName, "r")

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

    def update(self, gyro_x, gyro_y, gyro_z, dt=None):
        # Integrating body rates is an approximation for separate axis rotations,
        # not a general Euler-angle solution for combined 3D motion.
        dt = self.ts if dt is None else dt
        self.ang_x += gyro_x * dt
        self.ang_y += gyro_y * dt
        self.ang_z += gyro_z * dt
        return [self.ang_x, self.ang_y, self.ang_z]


class LowPassFilter:
    def __init__(self, cutoff_freq, dt, initial_value=0.0):
        self.rc = 1.0 / (2.0 * math.pi * cutoff_freq)
        self.alpha = dt / (self.rc + dt)
        self.y = initial_value

    def update(self, x, dt=None):
        if dt is not None:
            self.alpha = dt / (self.rc + dt)
        # Shortest angular difference avoids a jump at +/- pi.
        difference = (x - self.y + pi) % (2.0 * pi) - pi
        self.y += self.alpha * difference
        return self.y


# Estimate zero-rate offsets from a stationary recording of the same sensor.
# Temperature/time differences between recordings can leave residual drift.
gyro_bias = [0.0, 0.0, 0.0]
if imuType == "sparkfun_razor":
    with open(data_dir / calibrationFile) as calibration:
        stationary = [
            line.replace("*", ",").split(",") for line in calibration if line.strip()
        ]
    gyro_bias = [
        sum(float(row[i]) for row in stationary) / len(stationary) / 14.375 * pi / 180.0
        for i in (5, 6, 7)
    ]
# For VectorNav, supply biases from its own stationary recording above.

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

    # Keep calculations in radians; convert only for plotting.
    pitch_acc, roll_acc = acc2euler(acc_x, acc_y, acc_z)
    dt = ts_now - ts_prev
    if count == 1:
        ts_start = ts_now
        lpFilterP = LowPassFilter(cutoff_freq, 0.0, pitch_acc)
        lpFilterR = LowPassFilter(cutoff_freq, 0.0, roll_acc)
        gyro2euler = Gyro2euler(0.0, pitch_acc, roll_acc)
    elif dt <= 0:
        raise ValueError("IMU timestamps must be strictly increasing")

    pitch, roll, yaw = gyro2euler.update(
        gyro_x - gyro_bias[0],
        gyro_y - gyro_bias[1],
        gyro_z - gyro_bias[2],
        dt,
    )
    plotTime.append(ts_now - ts_start)
    plotDataPitch.append(math.degrees(pitch))
    plotDataRoll.append(math.degrees(roll))
    plotDataYaw.append(math.degrees(yaw))
    plotAccPitch.append(math.degrees(pitch_acc))
    plotAccRoll.append(math.degrees(roll_acc))
    plotFiltDataPitch.append(math.degrees(lpFilterP.update(pitch_acc, dt)))
    plotFiltDataRoll.append(math.degrees(lpFilterR.update(roll_acc, dt)))

    ######################################################

# closing the file
f.close()

# show the plot
if showPlot:
    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(10, 9))
    for ax, title, raw, filtered, gyro in (
        (axes[0], "Pitch", plotAccPitch, plotFiltDataPitch, plotDataPitch),
        (axes[1], "Roll", plotAccRoll, plotFiltDataRoll, plotDataRoll),
    ):
        ax.plot(plotTime, raw, alpha=0.35, label="Accelerometer")
        ax.plot(plotTime, filtered, label="Accelerometer (low-pass)")
        ax.plot(plotTime, gyro, label="Gyro (bias corrected)")
        ax.set_title(title)
        ax.legend()
    axes[2].plot(plotTime, plotDataYaw, label="Gyro (relative yaw)")
    axes[2].set_title("Yaw — accelerometer cannot measure this")
    axes[2].legend()
    for ax in axes:
        ax.set_ylabel("Angle [deg]")
        ax.grid(True)
    axes[2].set_xlabel("Time [s]")
    fig.tight_layout()
    plt.savefig(data_dir / "imu_exercise_plot.png")
    plt.show()
