from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
 
import time
import atexit

MH = Adafruit_MotorHAT(0x60)
STEPRES = 1.8 # Step resulition in units of degree/step
DIRECTIONS = {	"ccw":Adafruit_MotorHAT.FORWARD,
		"cw":Adafruit_MotorHAT.BACKWARD}
STEPTYPES = {	"single":Adafruit_MotorHAT.SINGLE,
		"double":Adafruit_MotorHAT.DOUBLE,
		"interleave":Adafruit_MotorHAT.INTERLEAVE,
		"micro":Adafruit_MotorHAT.MICROSTEP}

class MotorControler:


	# create a default object, no changes to I2C address or frequency
	def __init__(self,motorPort = 1,steps = 200,addr = 0x60):
		self.motorPort = motorPort
		self.steps = steps
		self.hatAddress = addr
		global MH
                MH = Adafruit_MotorHAT(addr)
		self.stepperMotor = MH.getStepper(steps, motorPort)
		self.stepperMotor.setSpeed(30)

	def rotateMotor(self,degree = 0,dir = "cw",step = "double"):
                # print("ROTATING MOTOR")
                x = 0
                if step == "interleave":
                    x = int(degree/STEPRES)*2
                else:
                    x = int(degree/STEPRES)
                self.stepperMotor.step(x,DIRECTIONS[dir],STEPTYPES[step])


	# recommended for auto-disabling motors on shutdown!
	def turnOffMotors():
	        MH.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	        MH.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	        MH.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	        MH.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
	 
	atexit.register(turnOffMotors)

if __name__ == '__main__':
    m = MotorControler()
    m.rotateMotor(degree=360,step="single")
    m.rotateMotor(degree=360,step="double",dir="ccw")
