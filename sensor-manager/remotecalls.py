
import requests
parametertoSensorIDAPI = "https://iudx-rs-onem2m.iiit.ac.in/resource/nodes/"

dataFetchAPI = "https://iudx-rs-onem2m.iiit.ac.in/channels/"
# example https://iudx-rs-onem2m.iiit.ac.in/channels/WM- WF-PH03-00/feeds?start=2023-01-06T20:20:01Z where 2023-01-06T20:20:01Z is the start time and WM-WF-PH03-00 is the sensorID


def fetchdata(parms):
    readingType = parms["readingtype"]
    startTime = parms["starttime"]
    numofSensor = parms["numofsensors"]
    # get request parameters to sensorID API
    response = requests.get(parametertoSensorIDAPI)
    if response.status_code == 200:
        response = response.json()
        results = response["results"]
        # check if readingtype is present in the results
        if readingType in results:
            sensorIDs = results[readingType]
            # get the data from the sensorID
            if len(sensorIDs) > numofSensor:
                sensorIDs = sensorIDs[:numofSensor]
            print(sensorIDs)
            data = {}
            for i in sensorIDs:
                # print(i)
                res = requests.get(dataFetchAPI+i+"/feeds?start="+startTime)
                # print(dataFetchAPI+i+"/feeds?start="+startTime)
                # print(res.status_code)
                if res.status_code == 200:
                    res = res.json()
                    data[i] = res["feeds"]
                else:
                    print("Error: ", res.status_code)
            return data
        else:
            return {"Error": "Reading type not found"}
    else:
        return {"Error": "Error while querying the reading type"}


def main():
    parms = {
        "readingtype": "Flowrate",
        "starttime": "2023-01-14T08:26:20Z",
        "numofsensors": 1
    }
    data = fetchdata(parms)
    print(data)


if __name__ == "__main__":
    main()
