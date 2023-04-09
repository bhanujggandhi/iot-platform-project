import requests
import time


def SensorStream(timee):
    while (timee):
        sensorid = "acfec6f0-79d6-446c-beb2-ee22279ae717"
        apiRealT = "http://127.0.0.1:8000/fetch?sensorID=" + \
            sensorid + "&fetchType=RealTime"
        currData = requests.get(apiRealT).json()
        print(currData)
        timee -= 1
        # time.sleep(2)


SensorStream(1000)
