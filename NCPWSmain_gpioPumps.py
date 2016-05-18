import time, threading, datetime
import RPi.GPIO as GPIO
import json
import socket
import sys
import os
import paho.mqtt.client as mqtt
from sht1x.Sht1x import Sht1x as SHT1x
import select

#set the pins numbering mode
GPIO.setmode(GPIO.BOARD)

#with open("/home/pi/NCPWSstartup/jason_config_files/thisPlantID.json") as f:
#    config = json.load(f)

filePath = sys.argv[1]
with open(filePath) as f:
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

# SUBdata = "SUBincoming"
sIncomingSUB = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sIncomingSUB.bind((HOST,PORTsub))
sIncomingSUB.setblocking(0)
ready = select.select([sIncomingSUB],[],[],20)
sIncomingSUB.settimeout(10)
#send data to PUB
socketPUB = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)




clkPin = 7
GPIO.setup (redLed,GPIO.OUT)
GPIO.output (redLed,False)

pump_on_time = 3;
#motor pin
GPIO.setup (pumpPin,GPIO.OUT)
GPIO.output (pumpPin,False)

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

    
def read_sensor():
    sht1x = SHT1x(dataPin, clkPin)
    temperature = sht1x.read_temperature_C()
    humidity = sht1x.read_humidity()
    dewPoint = sht1x.calculate_dew_point(temperature, humidity)
    print("Temperature: {} Humidity: {} Dew Point: {}".format(temperature, humidity, dewPoint))  
    time.sleep(0.5)
    return humidity

    
def pump_ON():
    print (plantID + "pump on")
    GPIO.output (pumpPin, True)
    time.sleep(pump_on_time) 
    GPIO.output (pumpPin, False)

def pump_OFF():
    GPIO.output (pumpPin, False)


   

thisSensor_last_5_num =[]
thisSensor_mean = 0
maxMoist = 101.5
max_sensor_difference = 8


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
        #bytesSent = socketPUB.sendto(str(thisSensor_mean),(HOST,PORTpub))
        send_data_to_broker(str(thisSensor_mean))

    #    if ready[0]:
        try:
            incomingData= sIncomingSUB.recv(32)
            print ("incoming: " + incomingData) #already averaged on other end
            time.sleep(5)

            if incomingData == str("pump on"):
                print("paired plant's pump is on")

            elif incomingData == str("no incoming data received"):
                print("paired plant's lost connection")
               
            else:
                difference_of_incoming__and_thisSensor = float(incomingData)- thisSensor_mean
                print ("differenc: " +str(difference_of_incoming__and_thisSensor))

                if sensor_1 > maxMoist:
                    #turn LED on
                    GPIO.output (redLed,True)
                    pump_OFF()
                    print ("soil saturated, pump disabled. Red light indicates not to water")
                
                elif sensor_1 < maxMoist and difference_of_incoming__and_thisSensor > max_sensor_difference:
               # if sensor_1 > 100:
                    pump_ON()
                    #bytesSent = socketPUB.sendto("pump on",(HOST,PORTpub))
                    send_data_to_broker ("pump on")
                    pump_OFF() #keep this in just for back up
                    GPIO.output (redLed,False)
                    print ("paired plant has been watered, this pump has been actived.")
                    

                else:
                    GPIO.output (redLed,False)
        except:
    #    else:
            print("no incoming data")
            #bytesSent = socketPUB.sendto(str(sensor_1),(HOST,PORTpub))
            #bytesSent = socketPUB.sendto("no incoming data received",(HOST,PORTpub))
            #bytesSent = socketPUB.sendto(str(thisSensor_mean),(HOST,PORTpub))
            send_data_to_broker("no incoming data received")
            send_data_to_broker(str(thisSensor_mean))

       time.sleep(10)
            

sys.stdout.flush()

GPIO.cleanup()
        
    

    

        
    

