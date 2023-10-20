import pymongo
import sys

client = pymongo.MongoClient(
    "mongodb+srv://spraddyumn:630fZAc39GsDKSTy@cluster0.iaoachz.mongodb.net/?retryWrites=true&w=majority"
)

print(client.list_database_names())
mydatabase = client["NodeInfo"]

print(mydatabase.list_collection_names())
mycollection = mydatabase["node_info"]

# FOR TESTING
# mydict = {
#     "ip": "194.56.2.3",
#     "port": 200,
#     "serverStatus": 1,
#     "cpuUsage": 0.95,
#     "memUsage": 0.45,
#     "runningResourceCount": 4,
# }

# mycollection.insert_one(mydict)

myquery = {"serverStatus": 1}
mydoc = mycollection.find(myquery)


import json


def get_ip_port():
    ip, port = None, None
    minLoad = None

    with open("loadLimits.json", "r") as file:
        temp = json.load(file)
        minLoad = temp["maxCPUusage"]

    """ iterating through the active node instances 
        and picking the instance with least active workload"""

    for x in mydoc:
        if x["cpuUsage"] < minLoad:
            minLoad = x["cpuUsage"]
            ip, port = x["ip"], x["port"]
        print(x)

    if ip is None and port is None:
        print("request for new node instance creation from the node manager")

    return ip, port


ip, port = get_ip_port()
print(ip, port)
