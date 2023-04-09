import requests
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import json
from pymongo import MongoClient

with open('config.ini') as f:
    config=json.load(f)
    mongoKey=config['mongoKey']

client=MongoClient(mongoKey)
db=client.token

class Item(BaseModel):

    token: str 
    app_id: str 
    api_name: str
    pm1: Union[str,None]= None
    pm2: Union[str,None]= None
    pm3: Union[str,None]= None
    pm4: Union[str,None]= None
    pm5: Union[str,None]= None
    pm6: Union[str,None]= None
    pm7: Union[str,None]= None
    pm8: Union[str,None]= None
    pm9: Union[str,None]= None
    pm10: Union[str,None]= None

app = FastAPI()

url="http://127.0.0.1:8000/"

@app.post("/")
def root(item:Item):

    if(item.api_name!="signup"):

        payload={"token":item.token, "api_name": item.api_name}
        response=requests.post(url+"verify",json=payload).json()
        print(response["message"])
        if response["status"] == 200:
            return {"call completed"}
        else:
            return {"call failed"}
        
        
    
        
