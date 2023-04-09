import json
import sys

from notification_utils import sendEmail
from Messenger import Consume


TOPIC = "topic_notification"


# utilising message as per need
def utilise_message(key, value):
    value = json.loads(value)
    receiver_email, subject, body = value["receiver_email"], value["subject"], value["body"]
    sendEmail(receiver_email, subject, body)


# Driver Code
if __name__ == "__main__":
    consume = Consume(TOPIC)
    while True:
        resp = consume.pull()
        if resp["status"] == False:
            print(resp["value"])
        else:
            try:
                utilise_message(resp["key"], resp["value"])
            except:
                print("some value")
