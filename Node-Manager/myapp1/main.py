from typing import Union

import requests
import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/sensor/data")
def read_item(item_id: int, q: Union[str, None] = None):
    # res = requests.get(
    #     f"http://172.20.10.10:8082/fetch?sensorID=27785ce4-f175-4f48-8e46-db42f4671f4e&fetchType=RealTime&duration=10&startTime=12&endTime=14"
    # )

    # print({"data": res.text})

    # return {"data": res.text}
    return {
        "data": '{"data":["[1681063368, 0, 133]","[1681063368, 0, 133]","[1681063368, 0, 133]","[1681063368, 0, 133]","[1681063368, 0, 133]","[1681063368, 0, 133]","[1681063368, 0, 133]","[1681063368, 0, 133]","[1681063368, 0, 133]","[1681063368, 0, 133]"]}'
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", log_level="info", port=80)
