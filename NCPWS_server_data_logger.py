import paho.mqtt.client as mqtt
import time, threading, datetime

filePath = sys.argv[1]

with open(filePath) as f:
    config = json.load(f)

password = config['password']

#subscribing to opensensors.io
def on_publish(client, userdata, mid):
    print(str(datetime.datetime.now())+ " On publish: "+str(mid))
       
def on_connect(client, userdata, flags, rc):
    print(str(datetime.datetime.now())+ " On connect")

    client.subscribe("/users/woolfie/plant1a")
    client.subscribe("/users/woolfie/plant1b")
    client.subscribe("/users/woolfie/plant2a")
    client.subscribe("/users/woolfie/plant2b")
    client.subscribe("/users/woolfie/plant3a")
    client.subscribe("/users/woolfie/plant3b")
    client.subscribe("/users/woolfie/plant4a")
    client.subscribe("/users/woolfie/plant4b")
    client.subscribe("/users/woolfie/plant5a")
    client.subscribe("/users/woolfie/plant5b")
    client.subscribe("/users/woolfie/plant6a")
    client.subscribe("/users/woolfie/plant6b")

       
def on_message(client, userdata, msg):
    print(msg.topic+ " incoming data " +str(msg.payload))
    data = msg.payload
    print ("data: "+ data)
    # write topics to file
    # take the last portion of the topic name (e.g. test3text, feb1, plant1a, instead of /users/woolfie/test3text)
    topic_name = msg.topic.split('/')[-1]
    # take the date, e.g. 2016-03-21
    date_name = str(datetime.datetime.now().date())
    # open a different file per topic and per day
    with open('data_%s_%s.csv' % (topic_name, date_name), 'a') as topic_file:
        # write data to file as csv
        topic_file.write(str(datetime.datetime.now())+ "," + topic_name + "," + data + "\n")
  

if __name__ == '__main__':
    
    mqttc = mqtt.Client("3444")

    mqttc.username_pw_set("woolfie", password)
    print('subscibed')

    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect("mqtt.opensensors.io", 1883,60)

    mqttc.loop_forever()


