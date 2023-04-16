import logging
import json
import time
from pymongo import MongoClient
from logging import handlers


class Logger:
    def __init__(self, mongoKey=None):
        if mongoKey is None:
            # self.key = config("mongoKey")
            self.key = "mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority"
        else:
            self.key = mongoKey

        self.client = MongoClient(self.key)
        self.db = self.client.LoggerDB
        self.collection = self.db.loggingCollection

    def log(self, msg, level, module="None", timestamp=time.time()):
        """Store the message onto MongoDB Collection"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        try:
            log_data = {
                "timestamp": timestamp,
                "level": levels[level],
                "module": module,
                "msg": msg,
            }

            # send json object to mongoDB collection
            res = self.collection.insert_one(log_data)
            # print(res)
            # print(log_data)
            # log_json = json.dumps(log_data)
            # print(log_json)

        except Exception as e:
            print("Error: ", e)

        # # create an HTTP handler
        # http_handler = handlers.HTTPHandler(
        #     HOST,
        #     url,
        #     method="POST",
        # )
        #
        # self.logger.addHandler(http_handler)


logger_object = Logger()
logger_object.log("this is a new message", 3)

# if __name__ == "main":
# logging.basicConfig(format="%(asctime)s| %(levelname)s : %(message)s")
# logging.debug("This is a debug message")
# logging.info("This is an info message")
# logging.warning("This is a warning message")
# logging.error("This is an error message")
# logging.critical("This is a critical message")

# logger_object = Logger()
# logger_object.log()

# record = logging.makeLogRecord({"msg": "This is a message"})
# print(record)
# print(record.getMessage())
# time.asctime(localtime(timestamp)),
# time.localtime(timestamp),
# time.ctime(timestamp),
# time.time_ns(),
