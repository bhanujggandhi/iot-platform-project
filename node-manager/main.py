import json
import os
import socket
import zipfile
from typing import Union

import uvicorn
from bson import ObjectId
from confluent_kafka import Consumer, Producer
from decouple import config
from fastapi import FastAPI
from Messenger import Produce
from pymongo import MongoClient
from storage import downloadFile

KAFKA_CONFIG_FILE = "kafka_setup_config.json"
TOPIC = "topic_node_manager"
mongokey = config("mongoKey")
client = MongoClient(mongokey)
db = client["platform"]
producer = Produce()


def generate_docker_image(service):
    s = """FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]"""

    f = open("./" + str(service) + "/Dockerfile", "w")
    f.write(s)


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    addr = s.getsockname()
    s.close()
    return addr[1]


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    currip = s.getsockname()[0]
    s.close()
    return currip


ip = get_ip()


class Consume:
    def __init__(self, topic):
        self.topic = topic
        self.data = json.load(open(KAFKA_CONFIG_FILE))
        self.kafka_consumer_config = self.data["kafka_consumer_config"]
        self.kafka_consumer_config["group.id"] = f"group_{self.topic}"
        self.consumer = Consumer(self.kafka_consumer_config)
        self.consumer.subscribe([self.topic])

    def pull(self):
        # Checking for message till the message is not found.
        while True:
            msg = self.consumer.poll(1.0)
            if msg is not None:
                break

        if msg.error():
            return {"status": False, "key": None, "value": msg.error()}

        else:
            # Extract the (optional) key and value, and print.
            key = msg.key().decode("utf-8")
            value = msg.value().decode("utf-8")
            if msg.headers():
                for header in msg.headers():
                    print("Header key: {}, Header value: {}".format(header[0], header[1]))
            return {"status": True, "key": key, "value": value}


# =============================================
# App Utils
# =============================================


def deploy_app(appid: str, userid: str):
    collection = db.App
    collection.create_index("name", unique=True)

    ip = get_ip()

    status = downloadFile("apps", f"{appid}.zip", ".")

    with zipfile.ZipFile(f"{appid}.zip", "r") as zip_ref:
        zip_ref.extractall(".")

    cmd = f"docker stop {appid} && docker rm {appid}"
    os.system(cmd)
    cmd = f"docker rmi {appid}"
    os.system(cmd)
    generate_docker_image(appid)
    cmd = f"docker build -t {appid} {appid}"
    os.system(cmd)
    assign_port = get_free_port()
    cmd = f"docker run --name {appid} -d -p {assign_port}:80 {appid}"
    os.system(cmd)

    data = {"name": appid, "port": assign_port, "ip": ip, "active": True, "user": ObjectId(userid)}

    collection.find_one_and_delete({"name": appid})
    collection.insert_one(data)

    message = {
        "receiver_email": "gandhibhanuj@gmail.com",
        "subject": f"{appid} Deployed",
        "body": f"Hello Developer,\nWe have successfully deployed your app at http://{ip}:{assign_port}",
    }

    produce.push("topic_notification", "node-manager-deploy", json.dumps(message))
    os.system(f"rm -rf {appid}.zip")
    os.system(f"rm -rf {appid}")

    return {"success": "deployed", "port": f"{assign_port}", "ip": ip}


def stop_app(appid: str, userid: str):
    collection = db.App
    active = collection.find_one({"name": appid})
    if not active:
        return {"status": "False", "msg": "App is not deployed!"}
    cmd = f"docker stop {appid}"
    os.system(cmd)
    data = {"active": False}
    collection.find_one_and_update({"name": service}, {"$set": data})
    return data


def start_app(appid: str, userid: str):
    collection = db.App
    active = collection.find_one({"name": appid})
    if not active:
        return {"status": "False", "msg": "App is not deployed!"}
    cmd = f"docker stop {appid}"
    os.system(cmd)
    cmd = f"docker rmi {appid}"
    os.system(cmd)
    generate_docker_image(appid)
    cmd = f"docker build -t {appid} {appid}"
    os.system(cmd)
    assign_port = get_free_port()
    cmd = f"docker run --name {appid} -d --rm -p {assign_port}:80 {appid}"
    os.system(cmd)
    data = {"name": service, "port": assign_port, "ip": ip, "active": True}
    collection.find_one_and_update({"name": service}, {"$set": data})
    return data


def remove_app(appid: str, userid: str):
    collection = db.App
    active = collection.find_one({"name": appid})
    if not active:
        return {"status": "False", "msg": "App is not deployed!"}
    cmd = f"docker stop {appid} && docker rm {appid}"
    os.system(cmd)
    cmd = f"docker rmi {appid}"
    os.system(cmd)
    collection.find_one_and_delete({"name": appid})
    return {"status": "True", "msg": "App removed"}


# =============================================
# Service Utils
# =============================================


def initialize():
    upservices = {}
    collection = db.Services
    with open("module.json", "r") as f:
        module_data = json.load(f)
    module = module_data["modules"]

    for i, service in enumerate(module):
        cmd = f"docker stop {service} && docker rm {service}"
        os.system(cmd)
        cmd = f"docker rmi {service}"
        os.system(cmd)
        generate_docker_image(service)
        cmd = f"docker build -t {service} {service}"
        os.system(cmd)
        assign_port = get_free_port()
        cmd = f"docker run --name {service} -d -p {assign_port}:80 {service}"
        os.system(cmd)
        upservices[service] = {"port": assign_port, "ip": ip}
        data = {"name": service, "port": assign_port, "ip": ip, "active": True}
        collection.insert_one(data)

    return {"services": upservices}


def create_node(service: str):
    collection = db.Services
    cmd = f"docker stop {service} && docker rm {service}"
    os.system(cmd)
    cmd = f"docker rmi {service}"
    os.system(cmd)
    generate_docker_image(service)
    cmd = f"docker build -t {service} {service}"
    os.system(cmd)
    assign_port = get_free_port()
    cmd = f"docker run --name {service} -d --rm -p {assign_port}:80 {service}"
    os.system(cmd)
    data = {"name": service, "port": assign_port, "ip": ip, "active": True}
    collection.insert_one(data)
    return data


def start_node(service: str):
    collection = db.Services
    active = collection.find_one({"name": service})
    if not active:
        return {"status": "False", "msg": "Node is not in our database, please create one"}
    cmd = f"docker stop {service}"
    os.system(cmd)
    cmd = f"docker rmi {service}"
    os.system(cmd)
    generate_docker_image(service)
    cmd = f"docker build -t {service} {service}"
    os.system(cmd)
    assign_port = get_free_port()
    cmd = f"docker run --name {service} -d --rm -p {assign_port}:80 {service}"
    os.system(cmd)
    data = {"name": service, "port": assign_port, "ip": ip, "active": True}
    collection.find_one_and_update({"name": service}, {"$set": data})
    return data


def remove_node(service: str):
    collection = db.Services
    active = collection.find_one({"name": service})
    if not active:
        return {"status": "False", "msg": "Node is not in our database, please create one"}
    cmd = f"docker stop {service} && docker rm {service}"
    os.system(cmd)
    cmd = f"docker rmi {service}"
    os.system(cmd)
    collection.find_one_and_delete({"name": service})
    return {"status": "True", "msg": "Service removed"}


def stop_node(service: str):
    collection = db.Services
    active = collection.find_one({"name": service})
    if not active:
        return {"status": "False", "msg": "Node is not in our database, please create one"}
    cmd = f"docker stop {service} && docker rm {service}"
    os.system(cmd)
    data = {"active": False}
    collection.find_one_and_update({"name": service}, {"$set": data})
    return {"status": "True", "msg": "service stopped successfully"}


service_func = {
    "create": create_node,
    "start": start_node,
    "stop": stop_node,
    "init": initialize,
    "remove": remove_node,
}

app_func = {"deploy": deploy_app, "start": start_app, "stop": stop_app, "remove": remove_app}

produce = Produce()


def utilise_message(value):
    value = json.loads(value)
    src = value["src"]
    if value["service"] == "" and value["app"] == "":
        message = {"status": "False", "msg": "No valid service or app provided"}
        produce.push(src, TOPIC, json.dumps(message))
    if value["service"] != "":
        if value["operation"] not in service_func.keys():
            message = {"status": "False", "msg": f"No valid operation provided for the {value['service']}"}
            produce.push(src, TOPIC, json.dumps(message))
        else:
            if value["operation"] == "init":
                res = service_func[value["operation"]]()
            else:
                res = service_func[value["operation"]](value["service"])
            message = {"status": "True", "msg": res}
            produce.push(src, TOPIC, json.dumps(message))
    if value["app"] != "":
        if value["operation"] not in app_func.keys():
            message = {"status": "False", "msg": f"No valid operation provided for the {value['app']}"}
            produce.push(src, TOPIC, json.dumps(message))
            print(message)
        else:
            print(value)
            res = app_func[value["operation"]](value["app"], value["id"])
            try:
                message = json.dumps({"status": "True", "msg": res})
            except:
                message = {"status": "True", "msg": "deployed"}
            produce.push(src, TOPIC, json.dumps(message))


"""
Expected json from producer of topic topic_node_manager

{
    "service": "",
    "app": "",
    "operation": "",
    "id":"",
    "src":""
}

"""


if __name__ == "__main__":
    consume = Consume("topic_internal_api")
    while True:
        resp = consume.pull()
        if resp["status"] == False:
            print(resp["value"])
        else:
            # utilise_message(resp["value"])
            print(resp)
