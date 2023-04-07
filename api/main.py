import os
import shutil
from typing import Union

from fastapi import FastAPI, File, HTTPException, Response, UploadFile, status
from utils import verify_zip

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/deploy/upload")
async def get_zip_file(file: UploadFile = File(...)):
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
