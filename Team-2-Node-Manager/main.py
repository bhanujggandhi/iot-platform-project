from typing import Union
from fastapi import FastAPI

import os
import json


app = FastAPI()

ports = [8001, 8002, 8003, 8004, 8005, 8006, 8007]


def generate_docker_image(service):
    s = (
        """FROM python:3.8.16

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./"""
        + str(service)
        + """.py ./

CMD ["python3", "./"""
        + str(service)
        + """.py"]"""
    )
    # CMD ["uvicorn", " """ +str(service)+""".main:app", "--host", "0.0.0.0", "--port", ' """ +str(ports[3])+ """' ]"""

    f = open("./" + str(service) + "/Dockerfile", "w")
    f.write(s)


@app.get("/init")
def initialize():
    with open("module.json", "r") as f:
        module_data = json.load(f)
    # print(module_data["modules"])
    upservices = []
    module = module_data["modules"]
    for service in module:
        cmd = f"sudo docker stop $(sudo docker ps -aqf 'name={service}') && sudo docker remove $(sudo docker ps -aqf 'name={service}')"
        os.system(cmd)
        generate_docker_image(service)
        cmd = "sudo docker build -t " + str(service) + " ./" + str(service)
        os.system(cmd)
        cmd = f"sudo docker run --name {service} {service}"
        os.system(cmd)
        upservices.append(service)

    return {"services": upservices}


@app.post("/create_node/{service}")
def create_node(service: str):
    generate_docker_image(service)
    # os.system("sudo docker ps -aq | xargs docker stop | xargs docker rm")
    cmd = "sudo docker build -t " + str(service) + " ./" + str(service)
    os.system(cmd)
    cmd = f"sudo docker run --name {service} {service}"
    os.system(cmd)
    return {"service": service}


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
