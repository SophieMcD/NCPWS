import time, threading, datetime
import RPi.GPIO as GPIO
import socket
import sys
import os
import paho.mqtt.client as mqtt
from sht1x.Sht1x import Sht1x as SHT1x
import select
import json

time.sleep(5)


#  set the pins numbering mode 
GPIO.setmode(GPIO.BOARD)

with open("/home/pi/NCPWSstartup/json_config_files/configFile_1b.json") as f:
    config = json.load(f)

#filePath = sys.argv[1]
#with open(filePath) as f:
#    config = json.load(f)

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
wlButtonPin = 18
pumpButton = 16
pumpPin = 22
ledPump = 32
ledWL = 36

#sensor pins
#wlButtonPin = button, with software pull down resistor enabled
GPIO.setup(shutdownButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(wlButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pumpButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(pumpPin, GPIO.OUT)

#red LED shows timed Dectivated system status
GPIO.setup (ledPump,GPIO.OUT)
GPIO.output (ledPump,True)
GPIO.setup (ledWL,GPIO.OUT)
GPIO.output (ledWL,False)
#user temporary deactivation

#SUB incoming data
HOST = "localhost"
sIncomingSUB = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sIncomingSUB.bind((HOST,PORTsub))
#sIncomingSUB.setblocking(0)
ready = select.select([sIncomingSUB],[],[],2)
sIncomingSUB.settimeout(10)
#send data to PUB
socketPUB = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# watering lock for user to deactivate their private plant from the system for n hours
class WateringLock(object):

    def __init__(self):
        self.timer = None
        self.locked = False

    def press_button(self):
        print("User pressed lock ON/OFF ")
        if self.locked:
            self.turn_watering_lock_off()
            print("Turning Lock ON ")
        else:
            self.turn_watering_lock_on()
            print("Turning Lock OFF ")

    def turn_watering_lock_off(self):
        print("Turning watering lock off")
        GPIO.output(ledWL,0)
        if self.timer is not None:
            self.timer.cancel()
        self.timer = None
        self.locked = False

    def turn_watering_lock_on(self):
        print("Turning watering lock on, turning off in 10 seconds")
        GPIO.output(ledWL,1)
        if self.timer is not None:
            self.timer.cancel()
        self.locked = True
        self.timer = threading.Timer(10.0, lambda: self.turn_watering_lock_off())
        self.timer.start()




def on_publish(client, userdata, mid):
       print(str(datetime.datetime.now())+ " On publish: "+str(mid))
       
def on_connect(client, userdata, rc):
       print(str(datetime.datetime.now())+ " On connect")      

def send_data_to_broker (data):
    sensor_data = str(data)
    mqttc = mqtt.Client(clientPub)
    mqttc.username_pw_set("woolfie", pwPub)
    mqttc.connect("mqtt.opensensors.io", 1883,60)
    mqttc.publish("/users/woolfie/" + topic_Pub, sensor_data, qos=1)
    print("published")
    time.sleep(1)
    



    
def pump_ON():
    GPIO.output(pumpPin, 1)
    GPIO.output(ledPump,1)


def pump_OFF():
    GPIO.output(pumpPin, 0)
    GPIO.output(ledPump,0)


localWButtonStatus = False
wl = WateringLock()


# send_data_to_broker("reactivated system")



# Main loop.
while True:

    if not GPIO.input(shutdownButton):
        print "shutting down"
        os.system("sudo shutdown")
        lightsOn = False
        while True:
            GPIO.output(ledPump, lightsOn)
            GPIO.output(ledWL, not lightsOn)
            lightsOn = not lightsOn
            time.sleep(0.5)
        

    if GPIO.input(wlButtonPin): # if user override button pressed on/off
        wl.press_button() #this has the flag and will turn on/off as apropriate
        print ("wlButton Pressed, water lock timer started")
        send_data_to_broker("this plants water lock on")

    if GPIO.input(pumpButton) : #  (local Watering Button)== 1
        print "Local BUTTON PRESSED"
        pump_ON()
        print("local pump ON, activated by local user")
        send_data_to_broker("pump on, activated by local user")


        # GPIO.output(24, 1)         # set port/pin value to 1/HIGH/True
    else:
        print "no pumps on"
        pump_OFF()
        send_data_to_broker("pump off")

# deactivate pump
#   GPIO.output(24, 0)         # set port/pin value to 0/LOW/False
       # bytesSent = socketPUB.sendto(str(thisSensor_mean),(HOST,PORTpub))

        #    if ready[0]:
    try:
        incomingData= sIncomingSUB.recv(32)
        print ("incoming: " + incomingData) #already averaged on other end
        time.sleep(5)

        if incomingData == str("pump on"):
            print("paired plant's pump is on")
            if wl.locked():
                print ("watering lock on, do not activate this pump")
                send_data_to_broker("local pump deactivated by user. Wait 4 hours from lock time stamp")
            else:
                print("activating local pump")
                pump_ON()
        
        elif incomingData == str("pump off"):
            print("paired plant pump off, turning local pump off")
            pump_OFF()

        elif incomingData == str("no incoming data received"):
            print("paired plant's lost connection")
        

        else:
            GPIO.output(ledPump,0)
    except:
    #    else:
         print("no incoming data")
            #bytesSent = socketPUB.sendto(str(sensor_1),(HOST,PORTpub))
            #bytesSent = socketPUB.sendto("no incoming data received",(HOST,PORTpub))
            #bytesSent = socketPUB.sendto(str(thisSensor_mean),(HOST,PORTpub))
         send_data_to_broker("no incoming data received")
         time.sleep(5)
            

sys.stdout.flush()

GPIO.cleanup()
