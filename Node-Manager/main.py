import json
import os
import socket
import zipfile
from typing import Union

import uvicorn
from decouple import config
from fastapi import FastAPI
from Messenger import Produce
from pymongo import MongoClient
from storage import downloadFile

app = FastAPI()
produce = Produce()

mongokey = config("mongoKey")
client = MongoClient(mongokey)


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


@app.get("/init")
def initialize():
    upservices = {}
    db = client["services"]
    collection = db.services
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
        cmd = f"docker run --name {service} -d --rm -p {assign_port}:80 {service}"
        os.system(cmd)
        upservices[service] = {"port": assign_port, "ip": ip}
        data = {"name": service, "port": assign_port, "ip": ip, "active": True}
        collection.insert_one(data)

    return {"services": upservices}


@app.post("/deploy/{appid}")
def serve_deploy(appid: str):
    db = client["apps"]
    collection = db.app
    exists = collection.find_one({"name": appid})
    ip = get_ip()

    if exists:
        if exists["active"] == False:
            assign_port = get_free_port()
            cmd = f"docker run --name {appid} -d --rm -p {assign_port}:80 {appid}"
            os.system(cmd)
            exists["port"] = assign_port
            exists["ip"] = ip

            res = collection.update_one({"name": appid}, exists)
            return res
        else:
            return exists

    status = downloadFile("apps", f"{appid}.zip", ".")

    with zipfile.ZipFile(f"{appid}.zip", "r") as zip_ref:
        zip_ref.extractall(".")

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

    data = {"name": appid, "port": assign_port, "ip": ip, "active": True}

    collection.insert_one(data)

    message = {
        "receiver_email": "gandhibhanuj@gmail.com",
        "subject": f"{appid} Deployed",
        "body": f"Hello Developer,\nWe have successfully deployed your app at http://{ip}:{assign_port}",
    }

    produce.push("topic_notification", "node-manager-deploy", json.dumps(message))
    deployed_apps.append(appid)
    # os.remove(f"{appid}.zip")

    return {"success": "deployed", "port": assign_port, "ip": ip}


@app.post("/app/stop/{appid}")
def serve_deploy(appid: str):
    if not appid in deployed_apps:
        return {"err": "app not deployed"}

    cmd = f"docker stop {appid}"
    os.system(cmd)


@app.post("/app/start/{appid}")
def serve_deploy(appid: str):
    if not appid in deployed_apps:
        return {"err": "app not deployed"}

    assign_port = get_free_port()
    cmd = f"docker run --name {appid} -d --rm -p {assign_port}:80 {appid}"
    os.system(cmd)

    return {"success": "deployed", "port": assign_port, "ip": "0.0.0.0"}


@app.post("/app/remove/{appid}")
def serve_deploy(appid: str):
    if not appid in deployed_apps:
        return {"err": "app not deployed"}
    cmd = f"docker rmi {appid}"
    os.system(cmd)
    deployed_apps.remove(appid)


@app.post("/create_node/{service}")
def create_node(service: str):
    generate_docker_image(service)
    # os.system("sudo docker ps -aq | xargs docker stop | xargs docker rm")
    cmd = "docker build -t " + str(service) + " ./" + str(service)
    os.system(cmd)
    cmd = f"docker run --name {service} {service}"
    os.system(cmd)
    port = 0
    for i in range(len(ports)):
        if not taken[i]:
            port = ports[i]
            taken[i] = True
            break
    return {"service_status": "NODE CREATED!!", "IP": ip, "PORT": port}


@app.get("/start_node/{service}")
def start_node(service: str):
    cmd = f"docker start {service}"
    os.system(cmd)
    return {"service started": service}


@app.get("/stop_node/{service}")
def stop_node(service: str):
    cmd = f"docker stop {service}"
    os.system(cmd)
    return {"node stopped": service}


@app.get("/restart_node/{service}")
def restart_node(service: str):
    cmd = f"docker stop {service}"
    os.system(cmd)
    cmd = f"docker start {service}"
    os.system(cmd)
    return {"node restarted": service}


@app.get("/configure_node/{service}")
def configure_node(service: str):
    return {"node configured": service}


if __name__ == "__main__":
    db = client["services"]
    collection = db.services
    res = collection.find_one({"name": "node-manager"})
    if not res:
        collection.insert_one({"name": "node-manager", "ip": ip, "port": 8000})
    uvicorn.run("main:app", host="0.0.0.0", log_level="trace", port=8000, workers=4)
