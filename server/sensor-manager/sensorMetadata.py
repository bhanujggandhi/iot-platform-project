import requests
from decouple import config
from pymongo import MongoClient

parametertoSensorIDAPI = "https://iudx-rs-onem2m.iiit.ac.in/resource/nodes/"


dataFetchAPI = "https://iudx-rs-onem2m.iiit.ac.in/channels/"
# example https://iudx-rs-onem2m.iiit.ac.in/channels/WM- WF-PH03-00/feeds?start=2023-01-06T20:20:01Z where 2023-01-06T20:20:01Z is the start time and WM-WF-PH03-00 is the sensorID
descriptorAPI = "https://iudx-rs-onem2m.iiit.ac.in/resource/descriptor/"
mongokey = config("mongoKey")
client = MongoClient(mongokey)


def populateMetadata():
    db = client["SensorDB"]
    collection = db["LatLongtoSensorID"]
    response = requests.get(parametertoSensorIDAPI)

    if response.status_code == 200:
        response = response.json()
        results = response["results"]
        sensorIDs = []
        for i in results:
            for j in results[i]:
                sensorIDs.append(j)
        LattoSensorIDmap = {}
        for i in sensorIDs:
            print("Fetching descriptor for ", i)
            res = requests.get(descriptorAPI + i)
            if res.status_code == 200:
                print("Success")
                res = res.json()
                res = res["Node Location"]
                Lat = res["Latitude"]
                long = res["Longitude"]
                lotlong = str(Lat) + "," + str(long)
                if lotlong in LattoSensorIDmap:
                    if i not in LattoSensorIDmap[lotlong]:
                        print(lotlong, i, "Existing latlong new sensor ")
                        LattoSensorIDmap[lotlong].append(i)
                    else:
                        print(lotlong, i, "Existing latlong existing sensor ")
                else:
                    print(lotlong, i, "not present")
                    LattoSensorIDmap[lotlong] = [i]
        for i in LattoSensorIDmap:
            print(i, LattoSensorIDmap[i])
            collection.insert_one({"location": i, "sensorIDs": LattoSensorIDmap[i]})
    else:
        print("Error while querying the sensorIDs")


populateMetadata()
