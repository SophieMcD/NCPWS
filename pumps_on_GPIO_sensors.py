#import the required modules
import RPi.GPIO as GPIO
import time
from sht1x.Sht1x import Sht1x as SHT1x

# set the pins numbering mode
GPIO.setmode(GPIO.BOARD)



#all sensors
clkPin = 7

#sensor 1 pins
dataPin1 = 29
redLed1 = 37
GPIO.setup (redLed1,GPIO.OUT)
GPIO.output (redLed1,False)
motor1 = 12
GPIO.setup (motor1,GPIO.OUT)
GPIO.output (motor1,False)


#sensor 2 pins
dataPin2 = 32
redLed2 = 36
GPIO.setup (redLed2,GPIO.OUT)
GPIO.output (redLed2,False)
motor2 = 13
GPIO.setup (motor2,GPIO.OUT)
GPIO.output (motor2,False)

#sensor 3 pins
dataPin3 = 33
redLed3 = 40
GPIO.setup (redLed3,GPIO.OUT)
GPIO.output (redLed3,False)
motor3 = 16
GPIO.setup (motor3,GPIO.OUT)
GPIO.output (motor3,False)

def read_sensor(dataPin):
    thisDataPin = dataPin 
    sht1x = SHT1x(thisDataPin, clkPin)
    temperature = sht1x.read_temperature_C()
    humidity = sht1x.read_humidity()
    dewPoint = sht1x.calculate_dew_point(temperature, humidity)
    #print(int(thisDataPin) + str(" sensor reading: "))
    print("Temperature: {} Humidity: {} Dew Point: {}".format(temperature, humidity, dewPoint))  
   # print('moisture level of sensor: ',sensor_id, " is: ", sensor_moist_val)
    time.sleep(0.5)
    return humidity

pump_on_time = 3;



def pump_1_ONoff():
    print "pump 1 on"
    GPIO.output (motor1, True)
    time.sleep(pump_on_time) 
    GPIO.output (motor1, False)

def pump_2_ONoff():
    print "pump 2 on"
    GPIO.output (motor2, True)
    time.sleep(pump_on_time) 
    GPIO.output (motor2, False)

def pump_3_ONoff():
    print "pump 3 on"
    GPIO.output (motor3, True)
    time.sleep(pump_on_time) 
    GPIO.output (motor3, False)
    



try:
    # Main loop.
    while True:
        print("Reading sensor 1")
        sensor_1 = read_sensor(dataPin1)
        print ("activating pump 1")
        pump_1_ONoff()
        GPIO.output (redLed1,True)
        print("LED 1 is ON")
        time.sleep(4)
        GPIO.output (redLed1,False)
        print("LED 1 is OFF")

        
        print("Reading sensor 2")
        sensor_1 = read_sensor(dataPin2)
        print ("activating pump 2")
        pump_2_ONoff()
        GPIO.output (redLed2,True)
        print("LED 2 is ON")
        time.sleep(4)
        GPIO.output (redLed2,False)
        print("LED 2 is OFF")

        print("Reading sensor 3")
        sensor_1 = read_sensor(dataPin3)
        print ("activating pump 3")
        pump_3_ONoff()
        GPIO.output (redLed3,True)
        print("LED 3 is ON")
        time.sleep(4)
        GPIO.output (redLed3,False)
        print("LED 3 is OFF")
        

    GPIO.cleanup()
        
# Clean up the GPIOs for next time
except KeyboardInterrupt:
    GPIO.cleanup()


