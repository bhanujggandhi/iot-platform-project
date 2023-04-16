import json
import sys

from notification_utils import Notification
from Messenger import Consume

TOPIC = "topic_notification"

# Creating object of class Notification
notification = Notification()

# utilising message as per need
def utilise_message(value):
    value = json.loads(value)
    receiver_email, subject, body = value["receiver_email"], value["subject"], value["body"]
    # print(receiver_email, subject, body)
    notification.notify(receiver_email, subject, body)


# Driver Code
if __name__ == "__main__":
    consume = Consume(TOPIC)
    while True:
        resp = consume.pull()
        if resp["status"] == False:
            print(resp["value"])
        else:
            # print(resp["key"], resp["value"])
            utilise_message(resp["value"])
