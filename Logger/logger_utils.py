import time
from pymongo import MongoClient
from decouple import config

MONGO_KEY = config("mongoKey")


class Logger:
    def __init__(self):
        self.client = MongoClient(MONGO_KEY)
        self.db = self.client.LoggerDB
        self.collection = self.db.loggingCollection

    def log(self, service_name, level, msg, app_name=None, user_id=None):
        # """Store the message onto MongoDB Collection"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        try:
            log_data = {
                "timestamp": time.time(),
                "service_name": service_name,
                "level": levels[level],
                "msg": msg,
                "app_name": app_name,
                "user_id": user_id,
            }

            # send json object to mongoDB collection
            res = self.collection.insert_one(log_data)
            # print(res)

        except Exception as e:
            print("Error: ", e)


# Sample Driver Code
if __name__ == "__main__":
    # levels = {0-DEBUG, 1-INFO, 2-WARNING, 3-ERROR, 4-CRITICAL]
    logger = Logger()
    logger.log(service_name="Notification", level=1, msg="Email sent.")
    # logger.log(service_name = 'Notification', level = 1, msg = 'App Crashed.', app_name = 'myapp1', user_id = 'ias2022')
