import os
import shutil
from typing import Union
import uvicorn

from auth.jwt_bearer import JWTBearer
from auth.jwt_handler import decodeJWT, signJWT
from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile, status
from utils.verify_zip import verify_zip

app = FastAPI()


@app.get("/", tags=["test"])
async def read_root():
    return {"Hello": "World"}


@app.post("/deploy/upload", dependencies=[Depends(JWTBearer())], tags=["deployement"])
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


@app.get("/apitoken/generate/{userid}", tags=["deployement"])
async def generate_token(userid: str):
    return signJWT(userid)


@app.get("/apitoken/verify/{token}", tags=["deployement"])
async def generate_token(token: str):
    return decodeJWT(token)
