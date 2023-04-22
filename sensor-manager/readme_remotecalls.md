Input for fetchdata function:

```py
 params = {
        "readingtype": "Flowrate",
        "starttime": "2023-01-14T08:26:20Z",
        "numofsensors": 2,
        "lat": 17.445402,
        "long": 78.349875,
        "sensorIDs": ["WM-WF-PH03-00"],
        "data_flag": True
    }

```

<!-- return Format -->

Example Output from fetchdata function:

```json
{
  "WM-WF-PH03-00": {
    "fields": [
      "Timestamp",
      "Flowrate",
      "Total Flow",
      "Pressure",
      "Pressure Voltage",
      "VersionInfo"
    ],
    "data": [
      {
        "created_at": "2023-01-24T02:55:52+05:30",
        "field1": 0.0,
        "field2": 9041.69,
        "field3": 0.0,
        "field4": 0.7823,
        "field5": "V6.0.0"
      },
      {
        "created_at": "2023-01-24T02:54:13+05:30",
        "field1": 0.0,
        "field2": 9041.69,
        "field3": 0.0,
        "field4": 0.769409,
        "field5": "V6.0.0"
      }
    ]
  }
}
```

### Recommended SensorIDS for testing:

| SensorID      | Description                  |
| ------------- | ---------------------------- |
| WM-WF-PH03-00 | Water Quality                |
| SL-VN03-00    | Solar Monitoring             |
| SR-EM-KH04-00 | Smart Room Energy Monitoring |

- All the Fields are optional, if not passed then default values are used.

- Here based on keys readingtype,lat,long Sensors are selected and starttime is used to get the data from that time to current time/till 8days (whichever is minimum). NumofSensors denotes required instance of the sensors, If upon searching the sensors based on readingtype,lat,long we get more sensors than required instance then top n sensors are selected randomly , where n denotes numofsensors.

- if data_flag is set to True then data is fetched else the function returns the sensorIDs of the sensors which are selected.

- if SensorsIDs are passed then data is fetched for those sensors only , regardless of readingtype,lat,long.

Default values for parms are:

```py
    readingtype = ""
    starttime = ""
    numofsensors = 1
    lat = 0
    long = 0
    sensorIDs = []
    data_flag = True

```

Expected Datatype of fields in parms:

```py
    readingtype = string
    starttime = string
    numofsensors = int
    lat = float
    long = float
    sensorIDs = list of strings
    data_flag = bool

```
