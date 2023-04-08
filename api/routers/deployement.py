import asyncio
import os
import shutil
import sys

import uvicorn
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from utils.jwt_bearer import JWTBearer
from utils.verify_zip import verify_zip

sys.path.append("..")

router = APIRouter()


async def my_task():
    await asyncio.sleep(10)
    print("Task Deployed")


@router.post("/upload", dependencies=[Depends(JWTBearer())])
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
        return {"detail": "uploaded"}
    else:
        os.remove(file.filename)
        raise HTTPException(400, detail="Zip file does not follow the directory structure. Please refer the doc")


@router.post("/schedule-task")
async def schedule_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(my_task)
    return {"message": "Task scheduled"}
