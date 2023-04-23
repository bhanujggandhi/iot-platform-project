import requests

url = "http://127.0.0.1:8000"

# "uid": "qwert1234",
#   "aid": "abc123",

payload = {
    "api_name": "fetch",
    "sensorID": "fsdvfsd-8e46-db42f4671f4e",
    "fetchType": "RealTime",
    "duration": 10,
    "startTime": 10,
    "endTime": 20,
}
response = requests.post(url, json=payload).json()

# payload={"api_name":"register","sensorName":"delete","sensorType":"RealTime","sensorLocation":"delete","sensorDescription":"delete"}
# response=requests.post(url,json=payload).json()
# id=response['sensorID']
# print(response)

# payload={"api_name":"bind","sensorName":"lux"}
# response=requests.post(url,json=payload).json()

# payload={"api_name":"deregister","sensorID":id}
# response=requests.post(url,json=payload).json()

print(response)
