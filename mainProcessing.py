import time, threading, datetime
import RPi.GPIO as GPIO
# Import the ADS1x15 module.
import Adafruit_ADS1x15
import socket
import sys
import os
import paho.mqtt.client as mqtt
from sht1x.Sht1x import Sht1x as SHT1x

#incoming data via udp port / socket
HOST = "localhost"
#SUB incoming data
HOST = "localhost"
PORTsub = 5459
# SUBdata = "SUBincoming"
sIncomingSUB = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sIncomingSUB.bind((HOST,PORTsub))


#send data to PUB
PORTpub = 5455
# PUBdata = "sendPUBdata"
socketPUB = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# remote energenie: set the pins numbering mode - from ENER200
GPIO.setmode(GPIO.BOARD)

# remote energenie: Select the GPIO pins used for the encoder K0-K3 data inputs
GPIO.setup(11, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)

# remote energenie: Select the signal to select ASK/FSK
GPIO.setup(18, GPIO.OUT)

# remote energenie: Select the signal used to enable/disable the modulator
GPIO.setup(22, GPIO.OUT)

#remote energenie: Disable the modulator by setting CE pin lo
GPIO.output (22, False)

# remote energenie: Set the modulator to ASK for On Off Keying 
# by setting MODSEL pin lo
GPIO.output (18, False)

# remote energenie: Initialise K0-K3 inputs of the encoder to 0000
GPIO.output (11, False)
GPIO.output (15, False)
GPIO.output (16, False)
GPIO.output (13, False)


#print('Reading ADS1x15 values, press Ctrl-C to quit...')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#sensor pins
dataPin = 37
clkPin = 7
PORTsub
redLed = 36
GPIO.setup (redLed,GPIO.OUT)
GPIO.output (redLed,False)

def read_sensor():
    sht1x = SHT1x(dataPin, clkPin)
    temperature = sht1x.read_temperature_C()
    humidity = sht1x.read_humidity()
    dewPoint = sht1x.calculate_dew_point(temperature, humidity)
    print("Temperature: {} Humidity: {} Dew Point: {}".format(temperature, humidity, dewPoint))  
    time.sleep(0.5)
    return humidity

    
def pump_ON():
    pump_on_time = 3;
    print "sending code 1111 socket 1 on"
    GPIO.output (11, True)
    GPIO.output (15, True)
    GPIO.output (16, True)
    GPIO.output (13, True)
    # let it settle, encoder requires this
    time.sleep(0.1)	
    # Enable the modulator
    GPIO.output (22, True)
    # keep enabled for a period
    time.sleep(pump_on_time)
    # Disable the modulator
    GPIO.output (22, False)
    pump_OFF()
    time.sleep(3)
   

def pump_OFF():
    print "sending code 1111 socket 1 off"
    GPIO.output (11, True)
    GPIO.output (15, True)
    GPIO.output (16, True)
    GPIO.output (13, False)
    # let it settle, encoder requires this
    time.sleep(0.1)	
    # Enable the modulator
    GPIO.output (22, True)
    # keep enabled for a period
    time.sleep(0.25)
    # Disable the modulator
    GPIO.output (22, False)    

thisSensor_last_5_num =[]
thisSensor_mean = 0
maxMoist = 9.99

# Main loop.
while True:
    sensor_1 = read_sensor()

    if len(thisSensor_last_5_num)<5:
        thisSensor_last_5_num.append(sensor_1)
        print (thisSensor_last_5_num)
        thisSensor_mean = sensor_1
       # bytesSent = socketPUB.sendto(str(thisSensor_mean),(HOST,PORTpub))

    else: 
        # latest 5 readings from this sensor
        thisSensor_last_5_num.append(sensor_1)
        thisSensor_last_5_num.pop(0)
        #average reading from the last 5 numbers
        thisSensor_mean = sum(thisSensor_last_5_num)/len(thisSensor_last_5_num)
        print ("this Sensors mean is: " + str(thisSensor_mean))
        #send_data_to_broker(thisSensor_mean)
        bytesSent = socketPUB.sendto(str(thisSensor_mean),(HOST,PORTpub))
            

        if sIncomingSUB.recv:
            incomingData= sIncomingSUB.recv(32)
            print ("incoming: " + incomingData) #already averaged on other end

            if incomingData == str("pump on"):
                print("paired plant's pump is on")
               
            else:
                difference_of_incoming__and_thisSensor = float(incomingData)- thisSensor_mean
                print ("differenc: " +str(difference_of_incoming__and_thisSensor))

                if sensor_1 > maxMoist:
                    #turn LED on
                    GPIO.output (redLed,True)
                    pump_OFF()
                    print ("soil saturated, pump disabled. Red light indicates not to water")
                
                elif sensor_1 < maxMoist and difference_of_incoming__and_thisSensor > 5:
               # if sensor_1 > 100:
                    pump_ON()
                    bytesSent = socketPUB.sendto("pump on",(HOST,PORTpub))
                    pump_OFF() #keep this in just for back up
                    GPIO.output (redLed,False)
                    print ("paired plant has been watered, this pump has been actived.")

                else:
                    GPIO.output (redLed,False)

        else:
            print("no incoming data")
            #bytesSent = socketPUB.sendto(str(sensor_1),(HOST,PORTpub))
            bytesSent = socketPUB.sendto(str(thisSensor_mean),(HOST,PORTpub))
            

sys.stdout.flush()

GPIO.cleanup()
        
    


