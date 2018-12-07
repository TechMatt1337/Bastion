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
MOTORS = {"horizontal":1,"vertical":2}

class MotorController:

	def __init__(self,motor,steps = 200,addr = 0x60):
                motorPort = MOTORS[motor]
		self.motorPort = motorPort
		self.steps = steps
		self.hatAddress = addr
		global MH
                MH = Adafruit_MotorHAT(addr)
		self.stepperMotor = MH.getStepper(steps, motorPort)
		self.stepperMotor.setSpeed(180)

	def rotateMotor(self,degree,dir = "cw",step = "single"):
                """
                Rotate motor for a certain degree from where it is located 
                at in a specified direction.
                Inputs: degree  -   Degrees to rotate
                        dir     -   cw or ccw rotation
                        step    -   Type of step motor should make for 
                                    rotation. By default it is set to 'double';
                                    which provides the highest torque that
                                    the motor is able to provide.
                                    Other types types of steps include 
                                    'single', 'interleave', and 'microstep'.
                """
                # print("ROTATING MOTOR")
                x = 0
                if step == "interleave":
                    x = int(degree/STEPRES)*2
                else:
                    x = int(degree/STEPRES)
                self.stepperMotor.step(x,DIRECTIONS[dir],STEPTYPES[step])


	def turnOffMotors():
                """
                Turn off all motors
                """
	        MH.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	        MH.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	        MH.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	        MH.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
	 
	# recommended for auto-disabling motors on shutdown!
	atexit.register(turnOffMotors)

if __name__ == '__main__':
    m = MotorController(motor="vertical")
    m.rotateMotor(degree=1000,step="double")
   # m.rotateMotor(degree=360,step="double",dir="ccw")
