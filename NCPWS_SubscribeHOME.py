import time, threading, datetime
import RPi.GPIO as GPIO
# Import the ADS1x15 module.
import Adafruit_ADS1x15
import socket
import sys
import os
import paho.mqtt.client as mqtt

# HOST & PORT are for sending the incoming data to the
# publishing and sensor data prog for analysis
HOST = "localhost"
PORT = 5459
data = "incoming"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

clientID = 3328

#subscribing to opensensors.io
def on_publish(client, userdata, mid):
       print(str(datetime.datetime.now())+ " On publish: "+str(mid))
       
def on_connect(client, userdata, flags, rc):
       print(str(datetime.datetime.now())+ " On connect")
       mqttc.subscribe("/users/woolfie/plant1b")

def on_message(client, userdata, msg):
    print(msg.topic+ " incoming data " + msg.payload)
    data = msg.payload
    print ("data data "+ data)
    bytesSent = s.sendto(data,(HOST,PORT))
    #print(bytesSent)
    sys.stdout.flush()
    

mqttc = mqtt.Client("clientID")

mqttc.username_pw_set("woolfie", "rainbow1!")
print('on subscibe')
mqttc.on_connect = on_connect
print('on connect')
mqttc.on_message = on_message
print('on msg')
mqttc.connect("mqtt.opensensors.io", 1883,60)
#data = mqttc.on_message
print(data)
mqttc.loop_forever()


    

