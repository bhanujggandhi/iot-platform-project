from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import websockets
import time
import json
from pymongo import MongoClient


app = FastAPI()

lastStoredTimestamp=0
mongoKey = ""
minutes=0.2

# get MongoDB key from config file
with open('./Sensor Manager/config.ini') as f:
    config = json.load(f)
    mongoKey = config['mongoKey']
with open('data.json', 'w') as f:
    json_str = json.dumps({"data":[]})
    f.write(json_str)



@app.get("/fetch_realtime_data")
async def get():
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        while True:
            response = await websocket.recv()
            #print(response)
            if response=="Done":
                await websocket.close()
                break

            with open("data.json", "r") as outfile:
                data = json.loads(outfile.read())

            response = json.loads(response)
            print(response)
            data['data'].extend(response['data'])
            print(len(data['data']))
            with open('data.json', 'w') as f:
                json_str = json.dumps(data)
                f.write(json_str)
        # with open('data.json', 'w') as f:
        #     json_str = json.dumps(data)
        #     f.write(json_str)
    return {"message": "Done"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global lastStoredTimestamp
    global minutes
    await websocket.accept()
    print("connecting...")
    client = MongoClient(mongoKey)
    print("connected...")
    db = client.SensorDB
    collection = db.SensorData
    sensor = {"sensorType":"Label_Sensor-1"}
    t_end = time.time() + 60 * minutes
    
    while time.time() < t_end:
        cursor = collection.find(sensor)
        data=[]
        for record in cursor:
            for i in range(len(record['data'])):
                #print(record['data'][i])
                li = json.loads(record['data'][i])
                if(int(li[0])> lastStoredTimestamp):
                    data.append((int(li[0]),int(li[-1])))
                    lastStoredTimestamp = int(li[0])
            if len(data)>0:
                await websocket.send_json({"data":data})

        time.sleep(4)
    await websocket.send_text("Done")
