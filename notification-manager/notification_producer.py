import json
from Messenger import Produce

TOPIC = "topic_notification"

# Sample Driver Code
if __name__ == "__main__":
    produce = Produce()

    for i in range(5):
        key = ""
        message = {
            "receiver_email": "ias2023.g1@gmail.com",
            "subject": f"Test{i}",
            "body": f"Test Body{i}.",
        }
        produce.push(TOPIC, key, json.dumps(message))
