import json
import os
import zipfile
from typing import Union

from fastapi import FastAPI
from storage import downloadFile

app = FastAPI()

ports = [8001, 8002, 8003, 8004, 8005, 8006, 8007]
ip = "127.0.0.1"
taken = [False] * 7
upservices = []
deployed_apps = []


def generate_docker_image(service):
    s = """FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]"""
    # CMD ["uvicorn", " """ +str(service)+""".main:app", "--host", "0.0.0.0", "--port", ' """ +str(ports[3])+ """' ]"""

    f = open("./" + str(service) + "/Dockerfile", "w")
    f.write(s)


@app.get("/init")
def initialize():
    with open("module.json", "r") as f:
        module_data = json.load(f)
    # print(module_data["modules"])
    module = module_data["modules"]
    for service in module:
        cmd = f"sudo docker stop {service} && docker rm {service}"
        os.system(cmd)
        generate_docker_image(service)
        cmd = f"sudo docker build -t {service} {service}"
        os.system(cmd)
        cmd = f"sudo docker run --name {service} {service}"
        os.system(cmd)
        upservices.append(service)

    return {"services": upservices}


@app.post("/deploy/{appid}")
def serve_deploy(appid: str):
    if appid in deployed_apps:
        return {"err": "app already deployed"}

    status = downloadFile("apps", f"{appid}.zip", ".")

    with zipfile.ZipFile(f"{appid}.zip", "r") as zip_ref:
        zip_ref.extractall(".")

    cmd = f"sudo docker stop {appid} && docker remove{appid}"
    os.system(cmd)
    generate_docker_image(appid)
    cmd = f"sudo docker build -t {appid} {appid}"
    os.system(cmd)
    cmd = f"sudo docker run --name {appid} -d -p 8080:80 {appid}"
    os.system(cmd)
    deployed_apps.append(appid)
    # os.remove(appid)

    return {"success": "deployed", "port": "8080", "ip": "0.0.0.0"}


@app.post("/app/stop/{appid}")
def serve_deploy(appid: str):
    if not appid in deployed_apps:
        return {"err": "app not deployed"}

    cmd = f"sudo docker stop {appid}"
    os.system(cmd)


@app.post("/app/start/{appid}")
def serve_deploy(appid: str):
    if not appid in deployed_apps:
        return {"err": "app not deployed"}

    cmd = f"sudo docker start {appid}"
    os.system(cmd)


@app.post("/app/remove/{appid}")
def serve_deploy(appid: str):
    if not appid in deployed_apps:
        return {"err": "app not deployed"}

    cmd = f"sudo docker stop {appid} && docker rm {appid}"
    os.system(cmd)
    cmd = f"sudo docker rmi {appid}"
    os.system(cmd)
    deployed_apps.remove(appid)


@app.post("/create_node/{service}")
def create_node(service: str):
    generate_docker_image(service)
    # os.system("sudo docker ps -aq | xargs docker stop | xargs docker rm")
    cmd = "sudo docker build -t " + str(service) + " ./" + str(service)
    os.system(cmd)
    cmd = f"sudo docker run --name {service} {service}"
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
    cmd = f"sudo docker start $(sudo docker ps -aqf 'name={service}')"
    os.system(cmd)
    return {"service started": service}


@app.get("/stop_node/{service}")
def stop_node(service: str):
    cmd = f"sudo docker stop $(sudo docker ps -aqf 'name={service}')"
    os.system(cmd)
    return {"node stopped": service}


@app.get("/restart_node/{service}")
def restart_node(service: str):
    cmd = f"sudo docker stop $(sudo docker ps -aqf 'name={service}')"
    os.system(cmd)
    cmd = f"sudo docker start $(sudo docker ps -aqf 'name={service}')"
    os.system(cmd)
    return {"node restarted": service}


@app.get("/configure_node/{service}")
def configure_node(service: str):
    return {"node configured": service}
