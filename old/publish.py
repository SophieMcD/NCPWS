import json
import time, threading, datetime
import RPi.GPIO as GPIO
import socket
import sys
import os
import paho.mqtt.client as mqtt
from sht1x.Sht1x import Sht1x as SHT1x



with open("/home/pi/NCPWSstartup/json_config_files/configFile_1b.json") as f:
    config = json.load(f)



#jason vars
plantID = config["plantIDj"]
dataPin = config["dataPinj"]
redLed = config["redLEDj"]
PORTsub = config["PORTsubj"]
PORTpub = config["PORTpubj"]
topic_Sub = config["topic_Subj"]
topic_Pub = config["topic_Pubj"]
pumpPin = config["pumpPinj"]
clientSub = config["clientSubj"]
pwSub = config["pwSubj"]
clientPub = config["clientPubj"]
pwPub = config["pwPubj"]

#SUB incoming data
HOST = "localhost"

#incoming data via udp port / socket
HOST = "localhost"
#PORT = 5455
sIncoming = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sIncoming.bind((HOST,PORTpub))



#print('Reading ADS1x15 values, press Ctrl-C to quit...')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



def on_publish(client, userdata, mid):
       print(str(datetime.datetime.now())+ " On publish: "+str(mid))
       
def on_connect(client, userdata, rc):
       print(str(datetime.datetime.now())+ " On connect")
       

def send_data_to_broker (data):
    sensor_data = str(data)
    mqttc = mqtt.Client(clientPub)
    mqttc.username_pw_set("woolfie", pwPub)
    mqttc.connect("mqtt.opensensors.io", 1883,60)
    mqttc.publish("/users/woolfie/plant1a", sensor_data, qos=1)
    print("published")
    time.sleep(1)
  #  print(sensor_data)
  


# Main loop.
while True:
    incomingMeanData= sIncoming.recv(32)
    
    if incomingMeanData == str("pump on"):
            print("paired plant's pump is on")
            send_data_to_broker(incomingMeanData)

    elif incomingMeanData == str("no incoming data received"):
           print("no incoming data: paired plant's lost connection")
           send_data_to_broker("no incoming data")
    else:
       print ("this sensor mean: " + incomingMeanData) #already averaged on other end
       send_data_to_broker(incomingMeanData)
            
    sys.stdout.flush()

GPIO.cleanup()
        
    

