import asyncio
import json
import os
import shutil
import sys
from typing import Annotated

import requests
import uvicorn
from decouple import config
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from pymongo import MongoClient
from utils.jwt_bearer import JWTBearer
from utils.jwt_handler import decodeJWT
from utils.Messenger import Produce
from utils.storage import deleteFile, downloadFile, listFiles, uploadFile
from utils.verify_zip import verify_zip

sys.path.append("..")

router = APIRouter()
produce = Produce()


CONTAINER_NAME = config("deploy_app_container_name")
mongokey = config("mongoKey")
client = MongoClient(mongokey)
db = client["platform"]


async def schedule_deployement_task(time: int, file: UploadFile = File(...), userid=""):
    await asyncio.sleep(time)
    # Logic or api call will come here to deploy
    try:
        fname = file.filename
        fname = fname.split(".")[0]
        message = {
            "service": "",
            "app": fname,
            "operation": "deploy",
            "id": userid,
            "src": "topic_internal_api",
        }
        produce.push("topic_node_manager", "", json.dumps(message))
        os.system(f"rm -rf {file.filename}")
        print(status)
    except:
        print("invalid")
    print("Task Deployed")


@router.post("/", dependencies=[Depends(JWTBearer())])
async def upload_zip_file(token: Annotated[str, Depends(JWTBearer())], file: UploadFile = File(...)):
    """
    Api to server upload zip file requets in order for developer to deploy
    """
    curr_user = decodeJWT(token)

    # Check filetype
    if file.content_type != "application/zip":
        raise HTTPException(400, detail="Only Zip file with proper directory structure is allowed")

    # Copy file to local disk
    with open(f"{file.filename}", "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Verify file structure
    verified = verify_zip(f"{file.filename}")
    if not verified is False:
        uploaded_files = listFiles(CONTAINER_NAME)

        if file.filename in uploaded_files["file_list"]:
            status = downloadFile(CONTAINER_NAME, file.filename, "./verify/")
            print(status)
            if verify_zip(f"./verify/{file.filename}") == verified:
                os.system(f"rm -rf ./verify/{file.filename}")
                os.system(f"rm -rf ./{file.filename}")
            else:
                status = deleteFile(CONTAINER_NAME, file.filename)
                print(status)
                status = uploadFile(CONTAINER_NAME, ".", file.filename)
                print(status)
                os.system(f"rm -rf ./verify/{file.filename}")
                os.system(f"rm -rf ./{file.filename}")
        else:
            # Upload to the cloud
            status = uploadFile(CONTAINER_NAME, ".", file.filename)

        fname = file.filename
        fname = fname.split(".")[0]
        message = {
            "service": "",
            "app": fname,
            "operation": "deploy",
            "id": curr_user["id"],
            "src": "topic_internal_api",
        }
        produce.push("topic_node_manager", "", json.dumps(message))
        return {"status": "True", "msg": "File is deploying safely. Please check back after 5 minutes"}
    else:
        os.remove(file.filename)
        raise HTTPException(400, detail="Zip file does not follow the directory structure. Please refer the doc")


@router.post("/schedule", dependencies=[Depends(JWTBearer())])
async def schedule_task(
    background_tasks: BackgroundTasks,
    token: Annotated[str, Depends(JWTBearer())],
    time: int = 0,
    file: UploadFile = File(...),
):
    curr_user = decodeJWT(token)
    # Check filetype
    if file.content_type != "application/zip":
        raise HTTPException(400, detail="Only Zip file with proper directory structure is allowed")

    # Copy file to local disk
    with open(f"{file.filename}", "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Verify file structure
    verified = verify_zip(f"{file.filename}")
    if not verified is False:
        uploaded_files = listFiles(CONTAINER_NAME)

        if file.filename in uploaded_files["file_list"]:
            status = downloadFile(CONTAINER_NAME, file.filename, "./verify/")
            print(status)
            if verify_zip(f"./verify/{file.filename}") == verified:
                os.system(f"rm -rf ./verify/{file.filename}")
                os.system(f"rm -rf ./{file.filename}")
            else:
                status = deleteFile(CONTAINER_NAME, file.filename)
                print(status)
                status = uploadFile(CONTAINER_NAME, ".", file.filename)
                print(status)
                os.system(f"rm -rf ./verify/{file.filename}")
                os.system(f"rm -rf ./{file.filename}")
        else:
            # Upload to the cloud
            status = uploadFile(CONTAINER_NAME, ".", file.filename)

        background_tasks.add_task(schedule_deployement_task, time, file, curr_user["id"])
        return {"message": "Task scheduled", "status": json.dumps(status)}
    else:
        os.remove(file.filename)
        raise HTTPException(400, detail="Zip file does not follow the directory structure. Please refer the doc")
