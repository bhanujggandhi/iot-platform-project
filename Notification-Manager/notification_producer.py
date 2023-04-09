import json
from Messenger import Produce

TOPIC = "topic_notification"

# Sample Driver Code
if __name__ == "__main__":
    produce = Produce()

    key = "mg"
    message = {"receiver_email": "mayankgupta12321@gmail.com", "subject": "Test 2", "body": "By changing producer"}

    produce.push(TOPIC, key, json.dumps(message))
