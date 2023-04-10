from typing import Union

import requests
import uvicorn
from fastapi import FastAPI

from utils.utils import hello

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/sensor/data")
def read_item(start: int = 12, end: int = 14):
    res = requests.get(
        f"http://10.2.138.250:60903/fetch?sensorID=27785ce4-f175-4f48-8e46-db42f4671f4e&fetchType=RealTime&duration=10&startTime={start}&endTime={end}"
    )

    print({"data": res.text})

    return {"data": res.text}


@app.get("/myname")
def my_name(name: str):
    return {"data": hello(name)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", log_level="info", port=80)
