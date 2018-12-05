from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
 
import time
import atexit

class MotorControler:

	STEPRES = 1.8 # Step resulition in units of degree/step
	DIRECTIONS = {	"forward":Adafruit_MotorHAT.FORWARD,
					"backwards":Adafruit_MotorHAT.BACKWARD}
	STEPTYPES = {	"single":Adafruit_MotorHAT.SINGLE,
					"double":Adafruit_MotorHAT.DOUBLE,
					"interleave":Adafruit_MotorHAT.INTERLEAVE,
					"micro":Adafruit_MotorHAT.MICROSTEP}

	# create a default object, no changes to I2C address or frequency
	def __init__(self,motorPort = 1,steps = 200,addr = 0x60):
		self.motorPort = motorPort
		self.steps = steps
		self.hatAddress = addr
		self.mh = Adafruit_MotorHAT(addr)
		self.stepperMotor = self.mh.getStepper(steps, motorPort)
		self.stepperMotor.setSpeed(30)

	def rotateMotor(self,motorPort = 1,degree = 0,dir = "forward",step = "single"):
		x = int(degree/STEPRES)
		self.stepperMotor.step(x,DIRECTIONS[dir],STEPTYPES[step])


	# recommended for auto-disabling motors on shutdown!
	def turnOffMotors(self):
	        self.mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	        self.mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	        self.mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	        self.mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
	 
	atexit.register(turnOffMotors)