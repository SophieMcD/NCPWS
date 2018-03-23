import time, threading, datetime
import RPi.GPIO as GPIO
import socket
import sys
import os
import signal
import paho.mqtt.client as mqtt
from sht1x.Sht1x import Sht1x as SHT1x
import select
import json
import select
import random

time.sleep(5)

#  set the pins numbering mode 
GPIO.setmode(GPIO.BOARD)

#with open("/home/pi/NCPWSstartup/json_config_files/configFile_1b.json") as f:
#    config = json.load(f)

filePath = sys.argv[1]
with open(filePath) as f:
    config = json.load(f)

#jason vars
plantID = config["plantIDj"]
dataPin = config["dataPinj"]
#redLed = config["redLEDj"]
PORTsub = config["PORTsubj"]
PORTpub = config["PORTpubj"]
topic_Sub = config["topic_Subj"]
topic_Pub = config["topic_Pubj"]
#pumpPin = config["pumpPinj"]
clientSub = config["clientSubj"]
pwSub = config["pwSubj"]
clientPub = config["clientPubj"]
pwPub = config["pwPubj"]

#make new hardware pin vars =
shutdownButton = 37

disconnectButton = 15 #red
ledDisconnect = 24 #red

waterButton = 11 #blue
ledPump = 18  #blue
pumpPin = 36 

inviteButton = 13 #yellow
ledInvite = 16 #yellow

acceptButton = 7 #gree
ledAccept = 22 #green

servoWaterDonor = 12
servoWaterRecipient = 32

GPIO.setup(disconnectButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ledDisconnect, GPIO.OUT)
GPIO.output(ledDisconnect, False)

GPIO.setup(inviteButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ledInvite, GPIO.OUT)
GPIO.output(ledInvite, False)

GPIO.setup(acceptButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ledAccept, GPIO.OUT)
GPIO.output(ledAccept, False)

GPIO.setup(waterButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ledPump, GPIO.OUT)
GPIO.output(ledPump, False)
GPIO.setup(pumpPin, GPIO.OUT)

#servo setup
GPIO.setup(servoWaterDonor, GPIO.OUT)
servoD = GPIO.PWM(servoWaterDonor, 50)
servoD.start(0)

GPIO.setup(servoWaterRecipient, GPIO.OUT)
servoR = GPIO.PWM(servoWaterRecipient, 50)
servoR.start(0)


#SUB incoming data
HOST = "localhost"
sIncomingSUB = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sIncomingSUB.bind((HOST, PORTsub))


def send_data_to_broker (data):
    print(data)
    sensor_data = str(data)
    mqttc = mqtt.Client(clientPub)
    mqttc.username_pw_set("woolfie", pwPub)
    mqttc.connect("mqtt.opensensors.io", 1883, 60)
    mqttc.publish("/users/woolfie/" + topic_Pub, sensor_data, qos=1)

# watering lock for user to deactivate their private plant from the system for n hours
class WateringLock(object):

    def __init__(self):
        self.timer = None
        self.locked = False

    def press_button(self):
        if self.locked:
            self.turn_watering_lock_off()
            send_data_to_broker("this plants water lock off")
        else:
            self.turn_watering_lock_on()
            send_data_to_broker("this plants water lock on")

    def turn_watering_lock_off(self):
        GPIO.output(ledWL, 0)
        if self.timer is not None:
            self.timer.cancel()
        self.timer = None
        self.locked = False

    def turn_watering_lock_on(self):
        GPIO.output(ledWL, 1)
        if self.timer is not None:
            self.timer.cancel()
        self.locked = True
        self.timer = threading.Timer(4 * 60 * 60, lambda: self.turn_watering_lock_off())
        self.timer.start()


def on_publish(client, userdata, mid):
       print(str(datetime.datetime.now())+ " On publish: " + str(mid))

       
def on_connect(client, userdata, rc):
       print(str(datetime.datetime.now())+ " On connect")
    
def pump_ON():
    GPIO.output(pumpPin, 1)
    GPIO.output(ledPump,1)


def pump_OFF():
    GPIO.output(pumpPin, 0)
    GPIO.output(ledPump,0)







numPlants = 12

def selectNextPlant():
  #  plant_list = ["plant1","plant2","plant3","plant4","plant5"]
    plant_list = [1,2,3,4,5,6,7,8]
    nextPlant = random.choice(plant_list)
    return nextPlant

nextPlant = selectNextPlant()    


try:
    while True:
        
        
        
        if GPIO.input(disconnectButton):
            GPIO.output(ledDisconnect,1)
           # p.start(11)  # turn towards 90 degree
            servoD.ChangeDutyCycle(nextPlant)  # turn towards 90 degree
            servoR.ChangeDutyCycle(nextPlant)  # turn towards 90 degree

            time.sleep(1)
            servoD.ChangeDutyCycle(0)
            servoR.ChangeDutyCycle(0)
            #time.sleep(1) # sleep 1 second
            print ("disconnectButton pressed")
        else:
            GPIO.output(ledDisconnect,0) 
 
            

        if GPIO.input(waterButton):
            GPIO.output(ledPump,1)
            GPIO.output(pumpPin,1)
            print ("water pump pressed")
            nextPlant = selectNextPlant() #select the next plant to be watered
            print (nextPlant)
            #send nextPlant data            
        else:
            GPIO.output(ledPump,0)
            GPIO.output(pumpPin,0)


        if GPIO.input(inviteButton):
            GPIO.output(ledInvite,1)
            print ("invite")
        else:
            GPIO.output(ledInvite,0)
    
        if GPIO.input(acceptButton):
            GPIO.output(ledAccept,1)
            print ("accept")
        else:
            GPIO.output(ledAccept,0)

            
except KeyboardInterrupt:
    servoD.stop()
    servoR.stop()
    GPIO.cleanup()
