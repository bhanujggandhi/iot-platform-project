import asyncio
import json
import shutil
import sys

import uvicorn
from decouple import config
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from utils.jwt_bearer import JWTBearer
from utils.storage import uploadFile
from utils.verify_zip import verify_zip

sys.path.append("../")

router = APIRouter()

CONTAINER_NAME = config("deploy_app_container_name")


async def my_task(time: int, file: UploadFile = File(...)):
    await asyncio.sleep(time)
    # Logic or api call will come here to deploy
    try:
        ans = await upload_zip_file(file)
        print(ans)
    except:
        print("invalid")
    print("Task Deployed")


@router.post("/", dependencies=[Depends(JWTBearer())])
async def upload_zip_file(file: UploadFile = File(...)):
    """
    Api to server upload zip file requets in order for developer to deploy
    """

    # Check filetype
    if file.content_type != "application/zip":
        raise HTTPException(400, detail="Only Zip file with proper directory structure is allowed")

    # Copy file to local disk
    with open(f"{file.filename}", "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Verify file structure
    if verify_zip(f"{file.filename}"):
        # Upload to the cloud
        status = await uploadFile(CONTAINER_NAME, file.filename, file.filename)
        return status
    else:
        os.remove(file.filename)
        raise HTTPException(400, detail="Zip file does not follow the directory structure. Please refer the doc")


@router.post("/schedule", dependencies=[Depends(JWTBearer())])
async def schedule_task(background_tasks: BackgroundTasks, time: int = 0, file: UploadFile = File(...)):
    status = await upload_zip_file(file)
    background_tasks.add_task(my_task, time, file)
    return {"message": "Task scheduled", "status": json.dumps(status)}
