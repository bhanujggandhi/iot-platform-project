
import requests
from decouple import config
from pymongo import MongoClient

parametertoSensorIDAPI = "https://iudx-rs-onem2m.iiit.ac.in/resource/nodes/"


dataFetchAPI = "https://iudx-rs-onem2m.iiit.ac.in/channels/"
# example https://iudx-rs-onem2m.iiit.ac.in/channels/WM- WF-PH03-00/feeds?start=2023-01-06T20:20:01Z where 2023-01-06T20:20:01Z is the start time and WM-WF-PH03-00 is the sensorID
descriptorAPI = "https://iudx-rs-onem2m.iiit.ac.in/resource/descriptor/"
mongokey = config("mongoKey")
client = MongoClient(mongokey)


def fetchdatahelper(sensorIDs, startTime):
    data = {}
    print("Fetching data for ", sensorIDs, " from ", startTime)
    for i in sensorIDs:
        res = requests.get(dataFetchAPI+i+"/feeds?start="+startTime)
        if res.status_code == 200:
            res = res.json()
            data[i] = res["feeds"]
        else:
            data[i] = []
    return data


def fetchdata(parms):
    readingType = parms["readingtype"]
    startTime = parms["starttime"]
    numofSensor = parms["numofsensors"]
    sensorIDs = []
    if "lat" in parms and "long" in parms:
        lat = parms["lat"]
        long = parms["long"]
        db = client["SensorDB"]
        collection = db["LatLongtoSensorID"]
        res = collection.find_one({"location": lat+","+long})
        if res:
            sensorIDs = res["sensorIDs"]

    # check if reading type some value
    if readingType != "":
        response = requests.get(parametertoSensorIDAPI)
        if response.status_code == 200:
            response = response.json()
            results = response["results"]
            if readingType in results:
                res_SIDS = results[readingType]
                sensorIDs.extend(res_SIDS)
            else:
                return {"Error": "No sensor with this reading type"}
        else:
            return {"Error": "Error while querying the sensorIDs"}

    if len(sensorIDs) == 0:
        return {"Error": "No sensor for given parameters"}
    if len(sensorIDs) > numofSensor:
        sensorIDs = sensorIDs[:numofSensor]
    data = fetchdatahelper(sensorIDs, startTime)
    return data


def main():
    parms = {
        "readingtype": "Flowrate",
        "starttime": "2023-01-14T08:26:20Z",
        "numofsensors": 10,
        "lat": "17.445402",
        "long": "78.349875"
    }
    data = fetchdata(parms)
    print(data)


if __name__ == "__main__":
    main()
