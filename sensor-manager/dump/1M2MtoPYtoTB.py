import paho.mqtt.client as mqtt
import time
import requests
import json

ACCESS_TOKEN        = '4CzUZW0HNb1Z2S9iLiOE'    #Token of your device
BROKER              = "172.31.226.70"  
PORT                = 1883   #data listening port

# payload = {
#     "datetime": str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
#     "dummy": 20
# }

def on_publish(client,userdata,result):
    print("data published to thingsboard \n")

client1 = mqtt.Client("control1")   #create client object
client1.on_publish = on_publish     #assign function to callback
client1.username_pw_set(ACCESS_TOKEN)   #access token from  thingsboard device
client1.connect(BROKER , PORT , keepalive=60)   #establish connection


# val = 0
payload  = {}
while True:
    url = 'http://10.2.132.73:5089/~/in-cse/in-name/AE-TEST/Node-1/Data?rcn=4'
    headers = {"X-M2M-Origin": "admin:admin",
    'Content-Type': 'application/json;ty=2'}
    response = requests.get(url, headers=headers)

    # print(response)
    # print(response.text)
    dct = json.loads(response.text)
    print(dct['m2m:cnt']['lbl'],dct['m2m:cnt']['st'],dct['m2m:cnt']['cbs'])
    payload['st'] = dct['m2m:cnt']['st']
    payload['cbs'] = dct['m2m:cnt']['cbs']
    ret = client1.publish("v1/devices/me/telemetry", str(payload)) #topic- v1/devices/me/telemetry

    print("Please check LATEST TELEMETRY field of your device")
    print(payload)
    # print('zzzzz')
    time.sleep(2)