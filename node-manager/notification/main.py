import json
import sys
import time

from notification_utils import Notification
from logger_utils import Logger
from Messenger import Consume, Produce

TOPIC_NOTIFICATION = "topic_notification"
SERVICE_NAME = "notification-service"

# Creating object of class Notification, Logger
notification = Notification()
logger = Logger()


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

    # If the message consumend is for health checkup.
    elif "to" in value.keys() and "src" in value.keys() and "data" in value.keys():
        if value["src"] == "topic_monitoring":
            try:
                data = {"timestamp": time.time(), "module": value["data"]["module"]}
                key = ""
                message = {"to": value["src"], "src": value["to"], "data": data}
                produce.push(value["src"], key, json.dumps(message))

                msg = f"Replied to Monitoring Service for Health Checkup Request with timestamp : {data['timestamp']}."
                logger.log(service_name=SERVICE_NAME, level=0, msg=msg)
            except:
                msg = f"Invalid Arguments found while consuming from Kafka Topic : {TOPIC_NOTIFICATION}."
                print(msg)
                logger.log(service_name=SERVICE_NAME, level=2, msg=msg)

        else:
            msg = f"Invalid Arguments found while consuming from Kafka Topic : {TOPIC_NOTIFICATION}."
            print(msg)
            logger.log(service_name=SERVICE_NAME, level=2, msg=msg)

    else:
        msg = f"Invalid Arguments found while consuming from Kafka Topic : {TOPIC_NOTIFICATION}."
        print(msg)
        logger.log(service_name=SERVICE_NAME, level=2, msg=msg)


# Driver Code
if __name__ == "__main__":
    consume = Consume(TOPIC_NOTIFICATION)
    produce = Produce()
    while True:
        resp = consume.pull()
        if resp["status"] == False:
            print(resp["value"])
        else:
            # print(resp["key"], resp["value"])
            utilise_message(produce, resp["value"])
