
import json
from notification_utils import sendEmail
import sys
from Messenger import Consume

TOPIC = 'topic_notification'

# utilising message as per need
def utilise_message(key, value) :
    value = json.loads(value)
    receiver_email, subject, body = value['receiver_email'], value['subject'], value['body']
    sendEmail(receiver_email, subject, body)

# Driver Code
if __name__ == '__main__' :
    consume = Consume(TOPIC)
    while True :
        resp = consume.pull()
        if resp['status'] == False :
            print(resp['value'])
        else :
            utilise_message(resp['key'], resp['value'])

