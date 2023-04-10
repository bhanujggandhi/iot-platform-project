import json
import os
import zipfile
from typing import Union

from fastapi import FastAPI
from Messenger import Produce
from storage import downloadFile

app = FastAPI()
produce = Produce()

ports = [8081, 8082, 8083, 8084, 8085, 8086, 8087]
ip = "127.0.0.1"
taken = [False] * 7
upservices = {}
deployed_apps = []


def generate_docker_image(service):
    s = """FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]"""

    f = open("./" + str(service) + "/Dockerfile", "w")
    f.write(s)


@app.get("/init")
def initialize():
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
        cmd = f"docker run --name {service} -d -p {ports[i]}:80 {service}"
        os.system(cmd)
        upservices[service] = ports[i]

    return {"services": upservices}


@app.post("/deploy/{appid}")
def serve_deploy(appid: str):
    if appid in deployed_apps:
        return {"err": "app already deployed"}

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
    cmd = f"docker run --name {appid} -d --rm -p {ports[-1]}:80 {appid}"
    # cmd = f"docker run -d --add-host host.docker.internal:host-gateway --name {appid} -p {ports[2]}:80 {appid}"

    os.system(cmd)
    message = {
        "receiver_email": "gandhibhanuj@gmail.com",
        "subject": f"{appid} Deployed",
        "body": f"Hello Developer,\nWe have successfully deployed your app at http://localhost:8080",
    }

    produce.push("topic_notification", "node-manager-deploy", json.dumps(message))
    deployed_apps.append(appid)
    # os.remove(appid)

    return {"success": "deployed", "port": ports[-1], "ip": "0.0.0.0"}


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

    cmd = f"docker run --name {appid} -d --rm -p {ports[4]}:80 {appid}"
    os.system(cmd)


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
