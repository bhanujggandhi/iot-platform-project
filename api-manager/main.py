import json
import time
import jwt
from pymongo import MongoClient
from fastapi import FastAPI
from typing import Union
from pydantic import BaseModel


class Item(BaseModel):
    token: str
    app_id: Union[str, None] = None
    api_name: Union[str, None] = None
    pm1: Union[str, None] = None
    pm2: Union[str, None] = None
    pm3: Union[str, None] = None
    pm4: Union[str, None] = None
    pm5: Union[str, None] = None
    pm6: Union[str, None] = None
    pm7: Union[str, None] = None
    pm8: Union[str, None] = None
    pm9: Union[str, None] = None
    pm10: Union[str, None] = None


with open("config.ini") as f:
    config = json.load(f)
    mongoKey = config["mongoKey"]

client = MongoClient(mongoKey)
db = client.token
appcollection = db.apptoken
usercollection = db.usertoken
usernamecollection = db.user
apicollection = db.api

secret = "58e550b216ff7b714cb81ed8b10efd96"
algorithm = "HS256"

JWT_SECRET = secret
JWT_ALGORITHM = algorithm


def token_response(token: str):
    return {"access_token": token}


def signJWT(userID: str):
    payload = {"userID": userID, "expiry": time.time() + 123456789}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decode_token if decode_token["expiry"] >= time.time() else None
    except:
        return {}


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/verify")
def verify(item: Item):
    dec = decodeJWT(item.token)
    if dec["userID"] != "":
        ret = usernamecollection.find_one({"user_name": dec["userID"]})
        if ret != None:
            if float(dec["expiry"]) < time.time():
                return {"status": 400, "message": "User id expired"}
        else:
            return {"status": 400, "message": "Invalid User id"}

    if item.api_name == "":
        return {"status": 400, "message": "Empty API call"}

    ret = apicollection.find({})
    api_lis = []
    for x in ret:
        api_lis.append(x["name"])
    if item.api_name not in api_lis:
        return {"status": 400, "message": "Invalid API"}

    ret = usercollection.find_one({"user_name": dec["userID"]})
    if ret != None:
        if item.api_name not in ret["acc_list"]:
            return {"status": 400, "message": "No access to API"}
        else:
            return {"status": 200, "message": "Successful"}
    else:
        return {"status": 400, "message": "No Access to user"}


@app.get("/generate_token")
def gen_token(item: Item):
    return signJWT(item.user_id)
