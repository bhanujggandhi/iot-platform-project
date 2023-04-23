import os
import time
import math
import random
import threading
import requests
from IPython.display import clear_output
import requests
import json


data_frequency = 0.5
no_of_params = 3


url = "http://127.0.0.1:5089/~/in-cse/in-name/AE-DEV/DEVICE-4/Data"
headers = {"X-M2M-Origin": "admin:admin", "Content-Type": "application/json;ty=23"}
payload = {"m2m:sub": {"rn": "Sub-DW", "nct": 2, "nu": "http://localhost:5089/"}}

response = requests.request("POST", url, headers=headers, json=payload)
response.text


def post_random_data():
    cnt = url
    headers = {"X-M2M-Origin": "admin:admin", "Content-Type": "application/json;ty=4"}
    lbls = ["tds", "water_level", "water_density", "lux", "uv", "color"]
    for lbl in lbls:
        _data_cin = [int(time.time()), random.randint(0, 1)]

        for count in range(no_of_params - 2):
            _data_cin.append(random.randint(1, 400))

        payload = {
            "m2m:cin": {"con": "{}".format(_data_cin), "lbl": lbl, "cnf": "text"}
        }
        response = requests.request("POST", cnt, headers=headers, json=payload)
        # print(response.text)
        # time.sleep(1)

    return response.status_code


def run():
    publish_count = 0
    while True:
        status_code = post_random_data()
        if status_code == 201:
            publish_count += 1
            print("Data publishing at " + str(data_frequency) + "-second frequency")
            print("Publish Successful")
            print("Number of data point published = " + str(publish_count))
        else:
            print(
                "Unable to publish data, process failed with a status code: "
                + str(status_code)
            )
        time.sleep(data_frequency)
        clear_output(wait=True)


run()
