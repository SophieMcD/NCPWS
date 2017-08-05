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
GPIO.setup(ledPump, GPIO.OUT)
GPIO.output(ledPump, False)
GPIO.setup(ledWL, GPIO.OUT)
GPIO.output(ledWL, False)
#user temporary deactivation

#SUB incoming data
HOST = "localhost"
sIncomingSUB = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sIncomingSUB.bind((HOST,PORTsub))
#send data to PUB
socketPUB = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# watering lock for user to deactivate their private plant from the system for n hours
class WateringLock(object):

    def __init__(self):
        self.timer = None
        self.locked = False

    def press_button(self):
        if self.locked:
            self.turn_watering_lock_off()
            print("Turning Lock OFF")
        else:
            self.turn_watering_lock_on()
            print("Turning Lock ON")

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
       print(str(datetime.datetime.now())+ " On publish: "+str(mid))

       
def on_connect(client, userdata, rc):
       print(str(datetime.datetime.now())+ " On connect")      

       
def send_data_to_broker (data):
    sensor_data = str(data)
    mqttc = mqtt.Client(clientPub)
    mqttc.username_pw_set("woolfie", pwPub)
    mqttc.connect("mqtt.opensensors.io", 1883, 60)
    mqttc.publish("/users/woolfie/" + topic_Pub, sensor_data, qos=1)

    
def pump_ON():
    GPIO.output(pumpPin, 1)
    GPIO.output(ledPump,1)


def pump_OFF():
    GPIO.output(pumpPin, 0)
    GPIO.output(ledPump,0)


wl = WateringLock()

# Shutdown interrupt

shuttingDown = False

def cb_shutdown(channel):
    print "shutting down"
    shuttingDown = True
    os.system("sudo shutdown")
    lightsOn = False
    while True:
        GPIO.output(ledPump, lightsOn)
        GPIO.output(ledWL, not lightsOn)
        lightsOn = not lightsOn
        time.sleep(0.5)

GPIO.add_event_detect(shutdownButton, GPIO.FALLING, callback=cb_shutdown)

# Waterlock interrupt

wl_last_pressed = 0.0

def cb_waterlock(channel):
    global wl_last_pressed
    now = time.time()
    if now - wl_last_pressed < 1.5:
        print "debouncing, ignoring waterlock button press"
    else:
        wl.press_button() #this has the flag and will turn on/off as apropriate
        send_data_to_broker("this plants water lock on")
    wl_last_pressed = now
        
GPIO.add_event_detect(wlButtonPin, GPIO.RISING, callback=cb_waterlock)

# Pump interrupt

def cb_pump_on():
     print "Local BUTTON PRESSED"
     pump_ON()
     print("local pump ON, activated by local user")
     send_data_to_broker("pump on, activated by local user")

def cb_pump_off():
    print "no pumps on"
    pump_OFF()
    send_data_to_broker("pump off")

def cb_pump(channel):
    if GPIO.input(pumpButton):
        cb_pump_on()
    else:
        cb_pump_off()
    
GPIO.add_event_detect(pumpButton, GPIO.BOTH, callback=cb_pump)

# Setup kill handler

exit_program = False

def kill_handler(signum, frame):
    print 'Signal handler called with signal', signum
    global exit_program
    exit_program = True
    
signal.signal(signal.SIGINT, kill_handler)


# Main loop.

def handle_incoming_data(incomingData):
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

        
def cleanup_and_quit(exit_code=0):
    GPIO.cleanup()
    sys.exit(exit_code)
        
send_data_to_broker("reactivated system")
    
while not exit_program:

    # don't allow any other buttons to be pressed when we're shutting down
    if shuttingDown:
        while True:
            time.sleep(1)
        
    try:
        ready = select.select([sIncomingSUB], [], [], 10)
        if ready[0]:
            incomingData = sIncomingSUB.recv(32)
            print ("incoming: " + incomingData) #already averaged on other end
            handle_incoming_data(incomingData)
        else:
            print("no incoming data")
            send_data_to_broker("no incoming data received")
        sys.stdout.flush()
    except:
        print("Something wen't wrong while receiving data")
        cleanup_and_quit(1)
         

cleanup_and_exit(0)