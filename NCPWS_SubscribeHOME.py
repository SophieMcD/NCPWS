import time, threading, datetime
import RPi.GPIO as GPIO
import socket
import sys
import os
import paho.mqtt.client as mqtt
import json



with open("/home/pi/NCPWSstartup/jason_config_files/configFile_1b.json") as f:
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


# HOST & PORT are for sending the incoming data to the
# publishing and sensor data prog for analysis
HOST = "localhost"
data = "incoming"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#subscribing to opensensors.io
def on_publish(client, userdata, mid):
       print(str(datetime.datetime.now())+ " On publish: "+str(mid))
       
def on_connect(client, userdata, flags, rc):
       print(str(datetime.datetime.now())+ " On connect")
       mqttc.subscribe("/users/woolfie/plant1b")

def on_message(client, userdata, msg):
    print(msg.topic+ " incoming data " + msg.payload)
    data = msg.payload
    bytesSent = s.sendto(data,(HOST,PORTsub))
    #print(bytesSent)
    sys.stdout.flush()
    

mqttc = mqtt.Client("3328")

mqttc.username_pw_set("woolfie", "QXBV7yK3")
print('on subscibe')
mqttc.on_connect = on_connect
print('on connect')
mqttc.on_message = on_message
print('on msg')
mqttc.connect("mqtt.opensensors.io", 1883,60)
#data = mqttc.on_message
print(data)
mqttc.loop_forever()


    
