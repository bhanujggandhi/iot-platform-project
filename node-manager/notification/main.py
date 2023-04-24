import json
import sys
import threading
import time

from heartbeat_service import HeartbeatService
from logger_utils import Logger
from Messenger import Consume, Produce
from notification_utils import Notification

TOPIC_NOTIFICATION = "topic_notification"
SERVICE_NAME = "notification-service"

# Creating object of class Notification, Logger
notification = Notification()
logger = Logger()
# Create a new instance of the HeartbeatService class
heartbeat_service = HeartbeatService("topic_notification_health", SERVICE_NAME)


# utilising message as per need
def utilise_message(produce, value):
    value = json.loads(value)
    print(value)

    # If the message consumend is for sending notification.
    if (
        "receiver_email" in value.keys()
        and "subject" in value.keys()
        and "body" in value.keys()
    ):
        receiver_email, subject, body = (
            value["receiver_email"],
            value["subject"],
            value["body"],
        )
        notification.notify(receiver_email, subject, body)

    else:
        msg = f"Invalid Arguments found while consuming from Kafka Topic : {TOPIC_NOTIFICATION}."
        print(msg)
        logger.log(service_name=SERVICE_NAME, level=2, msg=msg)


# Driver Code
if __name__ == "__main__":
    consume = Consume(TOPIC_NOTIFICATION)
    produce = Produce()
    thread = threading.Thread(target=heartbeat_service.start)
    thread.start()
    while True:
        resp = consume.pull()
        if resp["status"] == False:
            print(resp["value"])
        else:
            # print(resp["key"], resp["value"])
            utilise_message(produce, resp["value"])
