Sensor Manager module : 
1. sensormanager.py : contains all the api endpoints accessible by the app developer through api gateway. List of available endpoints are as follows : 
    - get(“/fetchSensors”) :  parameters : {} :: {"data" : [list of all sensors]}
      fetch all the sensors that are available for that particular app developer

    - get(“/fetchTimeSeries”) : parameters : {sensorID: str, startTime: int = None, endTime: int = None} :: {"data": [[timestamp, output, datapoint]]}

    - get(“/fetchInstant”) : parameters : {sensorID: str} :: {"data": [[timestamp, output, datapoint]]}

    - get(“/fetchRealTime”) : parameters : {sensorID: str, duration: int = 1} :: {"data": [[timestamp, output, datapoint]]}

    - get(“/register”) : parameters : {sensorName: str, sensorType: str, sensorLocation: str, sensorDescription: str}
    - get(“/deregister”) : parameters : {sensorID: str}
    - get(“/bind”) : parameters : {}

2. sensordata_to_db.py : Pushes sensor data of all sensors to the DB at a particular predefined frequency.
3. kafka_comm.py : Analytics module can fetch data from the sensormanager module through kafka

Developer token : eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjY0M2M2MGExOThiZjY4ZWQ3NTMzYjc2YSIsInJvbGUiOiJkZXZlbG9wZXIiLCJlbWFpbCI6ImJpc3dhc3NhbnRhbnUyMkBnbWFpbC5jb20iLCJleHBpcnkiOjE4MDUxNjQwMDguMDQ1MzIxfQ.weJmiCkL_D8ytMJhvdpSS7u4wlE4tjxMNaPztkgNAGg

Platform token : eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjY0MzZiYWQzYjhmZTM1NjVhMjkzNTc0NCIsInJvbGUiOiJwbGF0Zm9ybSIsImVtYWlsIjoiZ2FuZGhpYmhhbnVqQGdtYWlsLmNvbSIsImV4cGlyeSI6MTgwNTE2NDAxMC4yNzM5Mzk0fQ.2XBFeN7EpoH8eIwtBKSNKRoIO8foEPYendi431d-dMY

App token : 
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjY0M2Q3MWIxYWE1Njc3ZjNhYTJiOGM4YyIsImV4cGlyeSI6MTgwNTIwNjk2Mi45NzQ5MjQ4fQ.9qK3RtHGiSDrM7GfIYQ3AyR0K4Te3clXGTqYRKjDfDE