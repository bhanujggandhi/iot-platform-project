import requests
from decouple import config
from pymongo import MongoClient
import datetime
import json
from logger_utils import Logger


SERVICE_NAME = "sensor-manager"
logger = Logger()

parametertoSensorIDAPI = "https://iudx-rs-onem2m.iiit.ac.in/resource/nodes/"
dataFetchAPI = "https://iudx-rs-onem2m.iiit.ac.in/channels/"
descriptorAPI = "https://iudx-rs-onem2m.iiit.ac.in/resource/descriptor/"
mongokey = config("mongoKey")
client = MongoClient(mongokey)


def fetchdatahelper(sensorIDs, startTime):
    data = {}
    for i in sensorIDs:
        res = requests.get(dataFetchAPI + i + "/feeds?start=" + startTime)
        if res.status_code == 200:
            res = res.json()
            # feild names
            descriptor = requests.get(descriptorAPI+i)
            fields = []
            if descriptor.status_code == 200:
                descriptor = descriptor.json()
                descriptor = descriptor["Data String Parameters"]
                for j in descriptor:
                    fields.append(j)
            if (len(fields) > 0):
                data[i] = {
                    "fields": fields,
                    "data": res["feeds"]
                }
            else:
                data[i] = {
                    "fields": "Could not fetch fields",
                    "data": res["feeds"]
                }

        else:
            data[i] = {}

    return data


def validateSensorIDs(sensorIDs):
    for i in sensorIDs:
        try:
            res = requests.get(descriptorAPI+i, timeout=2)
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
        datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False


def fetchdata(parms):
    readingType = ""
    latitute = ""
    longitude = ""
    SensorIDsbyUser = []
    startTime = ""
    numofSensor = 1
    data_flag = True

    if "sensorIDs" in parms and len(parms["sensorIDs"]) > 0:
        SensorIDsbyUser = parms["sensorIDs"]

    if "readingtype" in parms and parms["readingtype"] != "":
        readingType = str(parms["readingtype"])
        if validateReadingType(readingType):
            pass
        else:
            msg = f"requestType : 'Fetchdata', request : {parms}, response : 'Invalid reading type'"
            logger.log(service_name=SERVICE_NAME, level=3, msg=msg)
            return {'status' : 400, 'data' : 'Invalid reading type'}

    if ("lat" in parms and parms['lat'] != '') and ("long" in parms and parms['long'] != ''):
        if type(parms["lat"]) == float and type(parms["long"]) == float:
            latitute = str(parms["lat"])
            longitude = str(parms["long"])
        else:
            msg = f"requestType : 'Fetchdata', request : {parms}, response : 'Invalid lat long'"
            logger.log(service_name=SERVICE_NAME, level=3, msg=msg)
            return {'status' : 400, 'data' : 'Invalid lat long'}

    if "starttime" in parms and parms["starttime"] != "":
        startTime = parms["starttime"]
        if startTime[-1] != "Z":
            startTime = startTime + "Z"
        if validateStartTime(startTime):
            startTime = startTime
        else:
            msg = f"requestType : 'Fetchdata', request : {parms}, response : 'Invalid start time'"
            logger.log(service_name=SERVICE_NAME, level=3, msg=msg)
            return {'status' : 400, 'data' : 'Invalid start time'}

    if "numofsensors" in parms:
        if type(parms["numofsensors"]) == int:
            if parms["numofsensors"] > 0:
                numofSensor = parms["numofsensors"]
            else:
                msg = f"requestType : 'Fetchdata', request : {parms}, response : 'Invalid number of sensors'"
                logger.log(service_name=SERVICE_NAME, level=3, msg=msg)
                return {'status' : 400, 'data' : 'Invalid number of sensors'}
        else:
            msg = f"requestType : 'Fetchdata', request : {parms}, response : 'Invalid datatype for number of sensors'"
            logger.log(service_name=SERVICE_NAME, level=3, msg=msg)
            return {'status' : 400, 'data' : 'Invalid datatype for number of sensors'}

    if "data_flag" in parms:
        if type(parms["data_flag"]) == bool:
            data_flag = parms["data_flag"]
        else:
            msg = f"requestType : 'Fetchdata', request : {parms}, response : 'Invalid data flag'"
            logger.log(service_name=SERVICE_NAME, level=3, msg=msg)
            return {'status' : 400, 'data' : 'Invalid data flag'}

    if len(SensorIDsbyUser) > 0:
        sensorIDs = SensorIDsbyUser
        if validateSensorIDs(sensorIDs):
            # print("Valid sensorIDs")
            if data_flag:
                data = fetchdatahelper(sensorIDs, startTime)
                msg = f"requestType : 'Fetchdata', request : {parms}, response : 'Data sent successfully, size : {len(data)}'"
                logger.log(service_name=SERVICE_NAME, level=1, msg=msg)
                return {'status' : 200, 'data' : data}
            else:
                msg = f"requestType : 'Fetchdata', request : {parms}, response : 'SensorIds sent successfully, size : {len(sensorIDs)}'"
                logger.log(service_name=SERVICE_NAME, level=1, msg=msg)
                return {'status' : 200, 'data' : sensorIDs}
        else:
            msg = f"requestType : 'Fetchdata', request : {parms}, response : 'Invalid sensorIDs'"
            logger.log(service_name=SERVICE_NAME, level=3, msg=msg)
            return {'status' : 400, 'data' : 'Invalid sensorIDs'}

    sensorIDs = []
    if latitute != "" and longitude != "":
        db = client["SensorDB"]
        collection = db["LatLongtoSensorID"]
        if collection.count_documents({"location": latitute+","+longitude}) == 0:
            # return {"Error": "No sensorIDs for given lat long"}
            pass
        else:
            res = collection.find_one({"location": latitute+","+longitude})
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
                msg = f"requestType : 'Fetchdata', request : {parms}, response : 'No sensor with this reading type'"
                logger.log(service_name=SERVICE_NAME, level=3, msg=msg)
                return {'status' : 400, 'data' : 'No sensor with this reading type'}
        else:
            msg = f"requestType : 'Fetchdata', request : {parms}, response : 'Error while querying the sensorIDs'"
            logger.log(service_name=SERVICE_NAME, level=3, msg=msg)
            return {'status' : 400, 'data' : 'Error while querying the sensorIDs'}

    if len(sensorIDs) == 0:
        msg = f"requestType : 'Fetchdata', request : {parms}, response : 'No sensor for given parameters'"
        logger.log(service_name=SERVICE_NAME, level=3, msg=msg)
        return {'status' : 400, 'data' : 'No sensor for given parameters'}
    if len(sensorIDs) > numofSensor:
        sensorIDs = sensorIDs[:numofSensor]
    if data_flag:
        data = fetchdatahelper(sensorIDs, startTime)
        msg = f"requestType : 'Fetchdata', request : {parms}, response : 'Data sent successfully, size : {len(data)}'"
        logger.log(service_name=SERVICE_NAME, level=1, msg=msg)
        return {'status' : 200, 'data' : data}
    else:
        msg = f"requestType : 'Fetchdata', request : {parms}, response : 'SensorIds sent successfully, size : {len(sensorIDs)}'"
        logger.log(service_name=SERVICE_NAME, level=1, msg=msg)
        return {'status' : 200, 'data' : sensorIDs}


def main():
    parms = {
        'readingtype': 'Voltage1', 'numofsensors': 1, 'data_flag': False
    }
    data = fetchdata(parms)
    print(data)


if __name__ == "__main__":
    main()
