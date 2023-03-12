import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


class Report(BaseModel):
    serviceName: str


app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {"status": True}


@app.post("/contact/")
async def createNode(item: Report):
    return {"status": "Node Manager contacted"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=9000, log_level="info")
