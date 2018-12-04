import RPi.GPIO as GPIO
import time
import termios
import sys
import tty
import threading

class Driver:

    engage=False
    speed=25
    freq=100
    backSpeed = 0

    def __init__(self,mode="eco"):
        self.gpioSetup()
        self.mode = mode
        self.fdir = False
        self.bdir = False
        print("finished setup")
        # self.start_thread()

    def gpioSetup(self):
        GPIO.setmode(GPIO.BCM)

        forward = 23
        backward = 24
        self.left = 17
        self.right = 27

        GPIO.setup(forward,GPIO.OUT)
        GPIO.setup(backward,GPIO.OUT)
        GPIO.setup(self.left,GPIO.OUT)
        GPIO.setup(self.right,GPIO.OUT)

        self.f = GPIO.PWM(forward,self.freq)
        self.b = GPIO.PWM(backward,self.freq)


        self.f.start(0)
        self.b.start(0)


    def accelerate(self):
        self.fdir = True
        self.speed += 2
        if(self.speed > 100):
            self.speed = 100
        self.b.ChangeDutyCycle(0)
        self.f.ChangeDutyCycle(self.speed)
        print('going forward ',self.speed)

    def deaccelerate(self):
        self.speed-=2
        if(self.speed < 5):
            self.backSpeed += 2
            self.f.ChangeDutyCycle(0)
            self.b.ChangeDutyCycle(self.backSpeed)
            print('going backward ',self.backSpeed)
        self.f.ChangeDutyCycle(self.speed)
        print("slowing down ", self.speed)

    def start_thread(self):
        self.t = threading.Thread(target=self.speed_decay)
        self.t.daemon = True
        self.t.start()

    # def speed_decay(self):
    #     while True:
    #         if not self.engage:
    #             if self.fdir:
    #                 self.speed -= 2
    #                 if(self.speed < 0):
    #                     self.speed = 0
    #                 time.sleep(0.25)
    #                 self.b.ChangeDutyCycle(0)
    #                 self.f.ChangeDutyCycle(self.speed)
    #         else:
    #             print("ENGAGED")

    def cleanup(self):
        self.speed = 0
        self.f.ChangeDutyCycle(self.speed)
        self.b.ChangeDutyCycle(self.speed)
        # GPIO.cleanup()

    def turnRight(self):
        GPIO.output(self.right,GPIO.LOW)
        GPIO.output(self.left,GPIO.HIGH)
        print("right")

    def turnLeft(self):
        GPIO.output(self.right,GPIO.HIGH)
        GPIO.output(self.left,GPIO.LOW)
        print("left")

    def listen(self):
        orig_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin)
        key=0
        while key != chr(27):
            key = sys.stdin.read(1)[0]
            if key == 'w':
                self.engage=True
                self.accelerate()
                print("forward")
                continue
            if key == 's':
                self.engage=True
                self.deaccelerate()
            if key == 'a':
                self.engage=True
                self.turnLeft()
            if key == 'd':
                self.engage=True
                self.turnRight()
            print("disengaged")
            self.engage=False
        termios.tcsetattr(sys.stdin,termios.TCSADRAIN,orig_settings)

if __name__ == '__main__':
    driver = Driver()
    driver.listen()
    driver.t.join()
    GPIO.cleanup()
