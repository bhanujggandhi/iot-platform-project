import json
import os
import socket
import threading
import time
import zipfile
from typing import Union

import uvicorn
from bson import ObjectId
from confluent_kafka import Consumer, Producer
from decouple import config
from fastapi import FastAPI
from heartbeat_service import HeartbeatService
from logger_utils import Logger
from Messenger import Produce
from pymongo import MongoClient
from storage import downloadFile

KAFKA_CONFIG_FILE = "kafka_setup_config.json"
TOPIC = "topic_node_manager"
SERVICE_NAME = "node_manager"
mongokey = config("mongoKey")
client = MongoClient(mongokey)
db = client["platform"]
producer = Produce()
logger = Logger()

# Create a new instance of the HeartbeatService class
heartbeat_service = HeartbeatService("topic_node_manager_health", SERVICE_NAME)


def generate_docker_image(service):
    s = """FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends --no-install-suggests build-essential && pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

EXPOSE 80

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
                    print(
                        "Header key: {}, Header value: {}".format(header[0], header[1])
                    )
            return {"status": True, "key": key, "value": value}


# =============================================
# App Utils
# =============================================


def deploy_app(appname: str, appid: str, userid: str):
    logger.log(SERVICE_NAME, 1, "Deploying App.....")

    collection = db.App
    collection.create_index("name", unique=True)
    user_collection = db.User
    app_collection = db.App
    curr_app = app_collection.find_one(
        {"_id": ObjectId(appid), "user": ObjectId(userid)}
    )
    curr_user = user_collection.find_one({"_id": ObjectId(userid)})

    if not curr_app:
        # message = {"src": TOPIC, "status": 404, "msg": "Could not find the app"}
        # produce.push("topic-internal-api", "", json.dumps(message))
        logger.log(SERVICE_NAME, 3, f"{appname} does not exist in our records")

        return {"success": 404, "err": "App does not found"}

    ip = get_ip()

    logger.log(SERVICE_NAME, 1, f"Starting the ZIP File download.....")
    res = downloadFile("apps", f"{appname}.zip", ".")
    if res["status"] == False:
        logger.log(SERVICE_NAME, 3, res["message"])
        return {"success": 500, "err": "Could not download the file, please check logs"}

    logger.log(SERVICE_NAME, 1, f"{appname}.zip downloaded successfully")

    with zipfile.ZipFile(f"{appname}.zip", "r") as zip_ref:
        zip_ref.extractall(".")

    logger.log(SERVICE_NAME, 1, "Allocating resouces....")

    cmd = f"docker stop {appname} && docker rm {appname}"
    os.system(cmd)
    cmd = f"docker rmi {appname}"
    os.system(cmd)
    generate_docker_image(appname)
    cmd = f"docker build -t {appname} {appname}"
    res = os.system(cmd)
    if res != 0:
        logger.log(
            SERVICE_NAME,
            4,
            f"{res} error code occurs from the VM Machine, please check",
        )
        return {"success": False, "message": "Internal Server Error"}
    assign_port = get_free_port()
    cmd = f"docker run --name {appname} -d -p {assign_port}:80 {appname}"
    res = os.system(cmd)
    if res != 0:
        logger.log(
            SERVICE_NAME,
            4,
            f"{res} error code occurs from the VM Machine, please check",
        )
        return {"success": False, "message": "Internal Server Error"}

    data = {"active": True, "port": assign_port, "ip": ip}

    logger.log(
        SERVICE_NAME, 1, "App deployed successfully", app_name=appname, user_id=userid
    )
    logger.log(SERVICE_NAME, 1, json.dumps(data), app_name=appname, user_id=userid)

    collection.find_one_and_update({"name": appname}, {"$set": data})

    message = {
        "receiver_email": curr_user["email"],
        "subject": f"{appname} Deployed",
        "body": f"Hello Developer,\nWe have successfully deployed your app at http://bhanujggandhi.me/apps/app/{appname}",
    }

    produce.push("topic_notification", "node-manager-deploy", json.dumps(message))
    os.system(f"rm -rf {appname}.zip")
    os.system(f"rm -rf {appname}")

    return {"success": "deployed", "port": f"{assign_port}", "ip": ip}


def stop_app(appname: str, appid: str, userid: str):
    collection = db.App
    active = collection.find_one({"_id": ObjectId(appid), "user": ObjectId(userid)})

    if not active:
        logger.log(
            SERVICE_NAME, 3, "App does not exist", app_name=appname, user_id=userid
        )
        return {"status": 404, "msg": "Could not find the app"}
    cmd = f"docker stop {appname}"
    res = os.system(cmd)
    if res != 0:
        logger.log(
            SERVICE_NAME,
            4,
            f"{res} error code occurs from the VM Machine, please check",
        )
        return {"success": False, "message": "Internal Server Error"}
    data = {"active": False}
    collection.find_one_and_update(
        {"_id": ObjectId(appid), "user": ObjectId(userid)}, {"$set": data}
    )

    logger.log(SERVICE_NAME, 1, f"{appname} is stopped successfully")
    logger.log(
        SERVICE_NAME,
        1,
        f"{appname} is stopped successfully",
        app_name=appname,
        user_id=userid,
    )
    return data


def start_app(appname: str, appid: str, userid: str):
    collection = db.App
    active = collection.find_one({"_id": ObjectId(appid), "user": ObjectId(userid)})

    if not active:
        logger.log(
            SERVICE_NAME, 3, "App does not exist", app_name=appname, user_id=userid
        )
        return {"status": 404, "msg": "Could not find the app"}

    cmd = f"docker start {appname}"
    res = os.system(cmd)
    if res != 0:
        logger.log(
            SERVICE_NAME,
            4,
            f"{res} error code occurs from the VM Machine, please check",
        )
        return {"success": False, "message": "Internal Server Error"}
    data = {"active": True}
    collection.find_one_and_update(
        {"_id": ObjectId(appid), "user": ObjectId(userid)}, {"$set": data}
    )

    logger.log(SERVICE_NAME, 1, f"{appname} is stopped successfully")
    logger.log(
        SERVICE_NAME,
        1,
        f"{appname} is stopped successfully",
        app_name=appname,
        user_id=userid,
    )
    return data


def remove_app(appname: str, appid: str, userid: str):
    collection = db.App
    active = collection.find_one({"_id": ObjectId(appid), "user": ObjectId(userid)})

    if not active:
        return {"status": 404, "msg": "Could not find the app"}

    cmd = f"docker stop {appname} && docker rm {appname}"
    os.system(cmd)
    cmd = f"docker rmi {appname}"
    os.system(cmd)
    collection.find_one_and_delete({"name": appname})
    return {"status": "True", "msg": "App removed"}


# =============================================
# Service Utils
# =============================================


def initialize():
    upservices = {}
    collection = db.Service
    with open("module.json", "r") as f:
        module_data = json.load(f)
    module = module_data["modules"]

    for i, service in enumerate(module):
        # collection.delete_many({"name": service})
        # cmd = f"docker stop {service} && docker rm {service}"
        # os.system(cmd)
        # cmd = f"docker rmi {service}"
        # os.system(cmd)
        # generate_docker_image(service)
        # cmd = f"docker build -t {service} {service}"
        # os.system(cmd)
        # assign_port = get_free_port()
        # cmd = f"docker run --name {service} -d -p {assign_port}:80 {service}"
        # os.system(cmd)
        # upservices[service] = {"port": assign_port, "ip": ip}
        # data = {"name": service, "port": assign_port, "ip": ip, "active": True}
        # collection.insert_one(data)
        logger.log(SERVICE_NAME, 1, f"{service}: STARTING....")
        cmd = f"kubectl apply -f ./{service}/manifests"
        res = os.system(cmd)
        if res != 0:
            logger.log(
                SERVICE_NAME,
                4,
                f"{res} error code occurs from the VM Machine, please check",
            )

    logger.log(SERVICE_NAME, 1, "All the services have initialised")
    return {"services": upservices}


def destroy():
    upservices = {}
    collection = db.Service
    with open("module.json", "r") as f:
        module_data = json.load(f)
    module = module_data["modules"]

    for i, service in enumerate(module):
        # collection.delete_many({"name": service})
        # cmd = f"docker stop {service} && docker rm {service}"
        # os.system(cmd)
        # cmd = f"docker rmi {service}"
        # os.system(cmd)
        # generate_docker_image(service)
        # cmd = f"docker build -t {service} {service}"
        # os.system(cmd)
        # assign_port = get_free_port()
        # cmd = f"docker run --name {service} -d -p {assign_port}:80 {service}"
        # os.system(cmd)
        # upservices[service] = {"port": assign_port, "ip": ip}
        # data = {"name": service, "port": assign_port, "ip": ip, "active": True}
        # collection.insert_one(data)
        logger.log(SERVICE_NAME, 1, f"{service}: STOPPING....")
        cmd = f"kubectl delete -f ./{service}/manifests"
        res = os.system(cmd)
        if res != 0:
            logger.log(
                SERVICE_NAME,
                4,
                f"{res} error code occurs from the VM Machine, please check",
            )

    logger.log(SERVICE_NAME, 1, "All the services have been stopped")

    return {"services": upservices}


def create_node(service: str):
    collection = db.Service
    collection.delete_many({"name": service})
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
    collection = db.Service
    active = collection.find_one({"name": service})
    if not active:
        return {
            "status": "False",
            "msg": "Node is not in our database, please create one",
        }
    cmd = f"docker stop {service}"
    os.system(cmd)
    cmd = f"docker rmi {service}"
    os.system(cmd)
    generate_docker_image(service)
    cmd = f"docker build -t {service} {service}"
    os.system(cmd)
    assign_port = get_free_port()
    cmd = f"docker run --name {service} -d -p {assign_port}:80 {service}"
    os.system(cmd)
    data = {"name": service, "port": assign_port, "ip": ip, "active": True}
    collection.find_one_and_update({"name": service}, {"$set": data})
    return data


def remove_node(service: str):
    collection = db.Service
    active = collection.find_one({"name": service})
    if not active:
        return {
            "status": "False",
            "msg": "Node is not in our database, please create one",
        }
    cmd = f"docker stop {service} && docker rm {service}"
    os.system(cmd)
    cmd = f"docker rmi {service}"
    os.system(cmd)
    collection.find_one_and_delete({"name": service})
    return {"status": "True", "msg": "Service removed"}


def stop_node(service: str):
    collection = db.Service
    active = collection.find_one({"name": service})
    if not active:
        return {
            "status": "False",
            "msg": "Node is not in our database, please create one",
        }
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
    "destroy": destroy,
}

app_func = {
    "deploy": deploy_app,
    "start": start_app,
    "stop": stop_app,
    "remove": remove_app,
}

produce = Produce()


def utilise_message(value):
    value = json.loads(value)
    print(value)
    if "to" in value.keys() and "src" in value.keys() and "data" in value.keys():
        if value["src"] == "topic_monitoring":
            try:
                data = {"timestamp": time.time(), "module": value["data"]["module"]}
                key = ""
                message = {"to": value["src"], "src": value["to"], "data": data}
                produce.push(value["src"], key, json.dumps(message))

                msg = f"Replied to Monitoring Service for Health Checkup Request with timestamp : {data['timestamp']}."
                print(msg)
                return
            except Exception as e:
                print(e)
                msg = f"Invalid Arguments found while consuming from Kafka Topic : {TOPIC}."
                print(msg)
                return
        else:
            msg = f"Invalid Arguments found while consuming from Kafka Topic : {TOPIC}."
            print(msg)
            return
    try:
        src = value["src"]
        service = value["service"]
        appname = value["app"]
        operation = value["operation"]
        appid = value["appid"]
        userid = value["userid"]
    except:
        message = {
            "src": TOPIC,
            "status": "False",
            "msg": "Message format is not correct",
        }
        produce.push(src, "", json.dumps(message))
        return

    if service == "" and appname == "":
        message = {
            "src": TOPIC,
            "status": "False",
            "msg": "No valid service or app provided",
        }
        produce.push(src, "", json.dumps(message))
    if service != "":
        if operation not in service_func.keys():
            message = {
                "src": TOPIC,
                "status": "False",
                "msg": f"No valid operation provided for the {service}",
            }
            produce.push(src, "", json.dumps(message))
        else:
            if operation == "init" or operation == "destroy":
                res = service_func[operation]()
            else:
                res = service_func[operation](service)
                print(res)
            message = {"src": TOPIC, "status": "True", "msg": res}
            produce.push(src, "", json.dumps(message))
    if appname != "":
        if operation not in app_func.keys():
            message = {
                "src": TOPIC,
                "status": "False",
                "msg": f"No valid operation provided for the {appname}",
            }
            produce.push(src, "", json.dumps(message))
            print(message)
        else:
            print(value)
            res = app_func[operation](appname, appid, userid)
            try:
                message = json.dumps({"status": "True", "msg": res})
            except:
                message = {"src": TOPIC, "status": "True", "msg": "deployed"}
            produce.push(src, "", json.dumps(message))


"""
Expected json from producer of topic topic_node_manager

{
    "service": "",
    "app": "",
    "operation": "",
    "appid":"",
    "userid":"",
    "src":""
}

"""


if __name__ == "__main__":
    print("Node Manager Started")
    consume = Consume(TOPIC)
    thread = threading.Thread(target=heartbeat_service.start)
    thread.daemon = True
    thread.start()
    while True:
        resp = consume.pull()
        if resp["status"] == False:
            print(resp["value"])
        else:
            utilise_message(resp["value"])
            # print(resp)
