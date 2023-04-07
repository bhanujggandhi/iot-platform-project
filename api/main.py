import shutil
from typing import Union

from fastapi import FastAPI, File, HTTPException, Response, UploadFile, status
from utils import verify_zip

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/deploy/upload")
async def get_zip_file(res: Response, file: UploadFile = File(...)):
    if file.content_type != "application/zip":
        raise HTTPException(400, detail="Only Zip file with proper directory structure is allowed")
    with open(f"{file.filename}", "wb") as f:
        shutil.copyfileobj(file.file, f)

    if not verify_zip(f"{file.filename}"):
        res.status_code = status.HTTP_200_OK
        return {"res": "uploaded"}
    else:
        raise HTTPException(400, detail="Zip file does not follow the directory structure. Please refer the doc")
