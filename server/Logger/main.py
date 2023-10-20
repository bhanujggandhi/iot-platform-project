import time
from pymongo import MongoClient
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# from decouple import config

app = FastAPI()

# MONGO_KEY = config("mongoKey")
MONGO_KEY = "mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority"

# Get the list of logging entries in MongoDB collection
client = MongoClient(MONGO_KEY)
db = client.LoggerDB
collection = db.loggingCollection


@app.get("/logs/", response_class=HTMLResponse)
async def getLogs(
    service_name: str = None,
    level: str = None,
    app_name: str = None,
    user_id: str = None,
):
    output = ""

    if app_name is None and service_name is None:
        output += "MODE 1 <br>"
        # find all data in DB
        cursor = collection.find(sort=[("timestamp", 1)])
    elif app_name is None:
        output += "MODE 2 <br>"
        # find all data in DB
        cursor = collection.find(
            {"service_name": service_name}, sort=[("timestamp", 1)]
        )
    else:
        output += "MODE 3 <br>"
        # find all data in DB
        cursor = collection.find({"app_name": app_name}, sort=[("timestamp", 1)])

    latest_timetimestamp = 0

    # Sort the documents on the basis of their created time and display onto stdout
    for document in cursor:
        print(document)
        # if document["timestamp"] > latest_timetimestamp:
        #     latest_timetimestamp = document["timestamp"]

        if app_name is None and service_name is None:
            if "service_name" in document:
                string = f'<br>{document["timestamp"]} | {document["level"]} <b>({document["service_name"]})</b>: {document["msg"]}'
            else:
                string = f'<br>{document["timestamp"]} | {document["level"]} <b>({document["app_name"]}, {document["user_id"]})</b>: {document["msg"]}'
        elif app_name is None:
            string = f'<br>{document["timestamp"]} | {document["level"]} <b>({document["service_name"]})</b>: &nbsp; {document["msg"]}'
        else:
            string = f'<br>{document["timestamp"]} | {document["level"]} <b>({document["app_name"]}, {document["user_id"]})</b>: {document["msg"]}'

        output += string
        # print(string)

    # while True:
    #     try:
    #         # get the latest data entry in collection
    #         document = collection.find_one(sort=[("timestamp", -1)])
    #         if document["timestamp"] > latest_timetimestamp:
    #             latest_timetimestamp = document["timestamp"]
    #             string = f'{document["timestamp"]} | {document["level"]} ({document["module"]}): {document["msg"]}'
    #             print(string)
    #     except KeyboardInterrupt:
    #         break

    HTML_output = (
        """        
    <html>
    <head>
        LOGS
    </head>
    <body>
    """
        + output
        + """
    </body>
    </html>
    """
    )

    return HTMLResponse(content=HTML_output, status_code=200)
