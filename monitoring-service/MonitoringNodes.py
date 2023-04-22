"""Assumption is that the healthStatus has same name across all the subsystems."""

import pymongo
import requests
from time import sleep

MAX_LOAD = 0.8
MIN_LOAD = 0.7
TIME_INTERVAL = 10
NODEINFO_DATABASE_URL = "mongodb+srv://spraddyumn:630fZAc39GsDKSTy@cluster0.iaoachz.mongodb.net/?retryWrites=true&w=majority"

NODE_MANAGER_API = "http://127.0.0.1:8000/"


def scale_nodes(NodeInfoCollection, MIN_LOAD, MAX_LOAD, TIME_INTERVAL):
    pipeline_for_avg_usage = [
        {"$match": {"serverStatus": 1}},
        {
            "$group": {
                "_id": None,
                "avg_cpu_usage": {"$avg": "$cpuUsage"},
                "avg_mem_usage": {"$avg": "$memUsage"},
            }
        },
    ]

    pipeline_for_min_usage = [
        {"$match": {"serverStatus": 1}},
        {"$group": {"_id": None, "min_cpu_usage": {"$min": "$cpuUsage"}}},
    ]

    while True:
        result = NodeInfoCollection.aggregate(pipeline_for_avg_usage).next()
        avg_cpu_usage, avg_mem_usage = result["avg_cpu_usage"], result["avg_mem_usage"]
        print(f"avg cpu usage : {avg_cpu_usage}, avg memory usage : {avg_mem_usage}")

        if avg_cpu_usage > MAX_LOAD or avg_mem_usage > MAX_LOAD:
            url = NODE_MANAGER_API + "upscale"
            req = {"serviceName": "upscale"}
            res = requests.post(url, json=req).json()
            print(res)

        elif avg_cpu_usage < MIN_LOAD and avg_mem_usage < MIN_LOAD:
            url = NODE_MANAGER_API + "downscale"

            result = NodeInfoCollection.aggregate(pipeline_for_min_usage).next()
            min_cpu_usage = result["min_cpu_usage"]
            node_with_min_cpu_usage = NodeInfoCollection.find_one(
                {"cpuUsage": min_cpu_usage}
            )
            ip, port = node_with_min_cpu_usage["ip"], node_with_min_cpu_usage["port"]
            address = f"{ip}:{port}"

            updated_result = NodeInfoCollection.find_one_and_update(
                {"ip": ip, "port": port}, {"$set": {"serverStatus": 0}}
            )

            print(
                f'Node with ip : {updated_result["ip"]}, port : {updated_result["port"]} has been marked for downscaling(serverStatus : 0)'
            )

            req = {"serviceName": address}
            res = requests.post(url, json=req).json()
            print(res)

        else:
            print("Everything Fine")

        sleep(1)  # As of now running script every second


if __name__ == "__main__":
    client = pymongo.MongoClient(NODEINFO_DATABASE_URL)
    NodeInfoDB = client["NodeInfo"]
    NodeInfoCollection = NodeInfoDB["node_info"]
    scale_nodes(NodeInfoCollection, MIN_LOAD, MAX_LOAD, TIME_INTERVAL)
