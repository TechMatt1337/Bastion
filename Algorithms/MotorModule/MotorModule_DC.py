#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import time
import atexit
import math

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

################################# DC motor test!
myMotor = mh.getMotor(3)

def getSpeed(radians):
	return int(math.sin(radians)*150)

def moveMotor(radians):
	speed = getSpeed(radians)
	if speed > 0:
		myMotor.run(Adafruit_MotorHAT.FORWARD);
	else:
		myMotor.run(Adafruit_MotorHAT.BACKWARD);
	speed = abs(speed)
	myMotor.setSpeed(speed)
	time.sleep(0.021)
	myMotor.run(Adafruit_MotorHAT.RELEASE)
	time.sleep(0.021)

def rotateMotor(radians):
	if (radians < 0):
		while (radians < 0):
			moveMotor(radians)
			radians += 0.1
	else:
		while (radians > 0):
			moveMotor(radians)
			radians -= 0.1

rotateMotor(math.pi)
rotateMotor(-math.pi)

