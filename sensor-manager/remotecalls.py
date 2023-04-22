import requests
from decouple import config
from pymongo import MongoClient
import datetime
import json

parametertoSensorIDAPI = "https://iudx-rs-onem2m.iiit.ac.in/resource/nodes/"


dataFetchAPI = "https://iudx-rs-onem2m.iiit.ac.in/channels/"
# example https://iudx-rs-onem2m.iiit.ac.in/channels/WM- WF-PH03-00/feeds?start=2023-01-06T20:20:01Z where 2023-01-06T20:20:01Z is the start time and WM-WF-PH03-00 is the sensorID
descriptorAPI = "https://iudx-rs-onem2m.iiit.ac.in/resource/descriptor/"
mongokey = config("mongoKey")
client = MongoClient(mongokey)


def fetchdatahelper(sensorIDs, startTime):
    data = {}
    # print("Fetching data for ", sensorIDs, " from ", startTime)
    for i in sensorIDs:
        res = requests.get(dataFetchAPI + i + "/feeds?start=" + startTime)
        if res.status_code == 200:
            res = res.json()
            # feild names
            descriptor = requests.get(descriptorAPI + i)
            fields = []
            if descriptor.status_code == 200:
                descriptor = descriptor.json()
                descriptor = descriptor["Data String Parameters"]
                for j in descriptor:
                    fields.append(j)
                # print(descriptor)
            if len(fields) > 0:
                # data[i] = res["feeds"]
                data[i] = {"fields": fields, "data": res["feeds"]}
            else:
                data[i] = {"fields": "Could not fetch fields", "data": res["feeds"]}

        else:
            data[i] = {}
    return data


def validateSensorIDs(sensorIDs):
    for i in sensorIDs:
        try:
            res = requests.get(descriptorAPI + i, timeout=2)
            if res.status_code != 200:
                return False
        except:
            return False
    return True


def validateReadingType(readingType):
    response = requests.get(parametertoSensorIDAPI)
    if response.status_code == 200:
        response = response.json()
        results = response["results"]
        if readingType in results:
            return True
        else:
            return False
    else:
        return False


def validateStartTime(startTime):
    if startTime[-1] != "Z":
        startTime = startTime + "Z"
    startTime = startTime.replace("Z", "")
    startTime = startTime.replace("T", " ")
    try:
        datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False


def get_sensor_data(readingType="", startTime="", numofSensor=1, latitude="", longitude=""):
    sensorIDs = []
    if "lat" != "" and "long" != "":
        db = client["SensorDB"]
        collection = db["LatLongtoSensorID"]
        res = collection.find_one({"location": latitude + "," + longitude})
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
    if data_flag:
        data = fetchdatahelper(sensorIDs, startTime)
        return data
    else:
        return sensorIDs


def main():
    data = get_sensor_data("Flowrate", "2023-04-1T20:26:20Z", 2, "17.445402", "78.349875")
    print(data)


if __name__ == "__main__":
    main()
