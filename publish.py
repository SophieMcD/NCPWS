import time, threading, datetime
import RPi.GPIO as GPIO
import socket
import sys
import os
import paho.mqtt.client as mqtt
from sht1x.Sht1x import Sht1x as SHT1x

#incoming data via udp port / socket
HOST = "localhost"
PORT = 5455
sIncoming = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sIncoming.bind((HOST,PORT))



#print('Reading ADS1x15 values, press Ctrl-C to quit...')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



def on_publish(client, userdata, mid):
       print(str(datetime.datetime.now())+ " On publish: "+str(mid))
       
def on_connect(client, userdata, rc):
       print(str(datetime.datetime.now())+ " On connect")
       

def send_data_to_broker (data):
    sensor_data = str(data)
    mqttc = mqtt.Client("3326")
    mqttc.username_pw_set("woolfie", "xEKCYFKX")
    mqttc.connect("mqtt.opensensors.io", 1883,60)
    mqttc.publish("/users/woolfie/plant1a", sensor_data, qos=1)
    print("published")
    time.sleep(5)
  #  print(sensor_data)
  


# Main loop.
while True:
    incomingMeanData= sIncoming.recv(32)
    print ("this sensor mean: " + incomingMeanData) #already averaged on other end
    if incomingMeanData == str("pump on"):
            print("paired plant's pump is on")
            send_data_to_broker(incomingMeanData)

    elif incomingMeanData == str("0"):
           print("paired plant's is calobrating")
           send_data_to_broker("")
    else:
        send_data_to_broker(incomingMeanData)
            
    sys.stdout.flush()

GPIO.cleanup()
        
    


