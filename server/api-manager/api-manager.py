import requests
from typing import Union
from fastapi import FastAPI, UploadFile, Path
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pymongo import MongoClient
import json
import uvicorn


class Item(BaseModel):
    token: Union[str, None] = None
    app_id: Union[str, None] = None
    api_name: Union[str, None] = None
    sensorID: Union[str, None] = None
    fetchType: Union[str, None] = None
    duration: Union[int, None] = None
    startTime: Union[int, None] = None
    endTime: Union[int, None] = None
    sensorName: Union[str, None] = None
    sensorType: Union[str, None] = None
    sensorLocation: Union[str, None] = None
    sensorDescription: Union[str, None] = None
    file: Union[UploadFile, None] = None
    Bearer: Union[str, None] = None
    # header : {}


with open("config.ini") as f:
    config = json.load(f)
    mongoKey = config["mongoKey"]

client = MongoClient(mongoKey)
db = client.apps
appcollection = db.app


app = FastAPI()

url = "http://192.168.47.246:8001"


@app.post("/")
async def root(item: Item):
    # if(item.api_name!="signup"):

    #     payload={"token":item.token, "api_name": item.api_name}
    #     response=requests.post(url+"verify",json=payload).json()
    #     print(response["message"])
    #     if response["status"] == 200:
    #         return {"call completed"}
    #     else:
    #         return {"call failed"}

    if item.api_name == "fetch":
        args = {
            "sensorID": item.sensorID,
            "fetchType": item.fetchType,
            "duration": item.duration,
            "startTime": item.startTime,
            "endTime": item.endTime,
        }
        response = requests.get(url + "/" + item.api_name, params=args).json()
        print(response)
        return response

    if item.api_name == "register":
        args = {
            "sensorName": item.sensorName,
            "sensorType": item.sensorType,
            "sensorLocation": item.sensorLocation,
            "sensorDescription": item.sensorDescription,
        }
        response = requests.post(url + "/" + item.api_name, params=args).json()
        return response

    if item.api_name == "bind":
        args = {
            "sensorName": item.sensorName,
            "sensorType": item.sensorType,
            "sensorLocation": item.sensorLocation,
            "sensorDescription": item.sensorDescription,
        }
        response = requests.get(url + "/" + item.api_name, params=args).json()
        return response

    if item.api_name == "deregister":
        args = {
            "sensorID": item.sensorID,
        }
        response = requests.delete(url + "/" + item.api_name, params=args).json()
        return response

    if item.api_name == "deploy":
        args = {"file": item.file}
        response = requests.post(
            url + "/" + item.api_name, params=args, headers=item.header
        ).json()
        return response


@app.get("/apps/{app_name:path}")
async def apps(app_name: str = Path(...)):
    arr = app_name.split("/")
    ret = appcollection.find_one({"name": arr[0]})
    if ret == None:
        return HTMLResponse(
            content="""<html><head><title>some title</title></head><body><h1>Invalid Application</h1></body></html>""",
            status_code=400,
        )
    else:
        if ret["active"] == False:
            return HTMLResponse(
                content="""<html><head><title>some title</title></head><body><h1>Application is not Running</h1></body></html>""",
                status_code=400,
            )
        else:
            url = "http://" + ret["ip"] + ":" + str(ret["port"])
            for i in range(1, len(arr)):
                url += "/" + str(arr[i])

            response = requests.get(url).json()

    return HTMLResponse(content=response, status_code=200)


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", log_level="info", port=80, workers=4, reload=True
    )
