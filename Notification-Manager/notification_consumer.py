
import json
from confluent_kafka import Consumer, OFFSET_BEGINNING
from notification_utils import sendEmail


TOPIC = 'topic_notification'
KAFKA_CONFIG_FILE = 'kafka_setup_config.json'


def create_consumer() :
    data = json.load(open(KAFKA_CONFIG_FILE))
    kafka_consumer_config = data['kafka_consumer_config']
    consumer = Consumer(kafka_consumer_config)
    return consumer


# Set up a callback to handle the '--reset' flag.
def reset_offset(consumer, partitions):
#     for p in partitions:
#         p.offset = OFFSET_BEGINNING
#     consumer.assign(partitions)
    pass


# utilising message as per need
def utilise_message(topic, key, value) :
    value = json.loads(value)
    receiver_email, subject, body = value['receiver_email'], value['subject'], value['body']
    sendEmail(receiver_email, subject, body)

    # print(topic, key, receiver_email, subject, body)


# Driver Code
if __name__ == '__main__' :
    consumer = create_consumer()

    # Subscribe to topic
    consumer.subscribe([TOPIC], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = consumer.poll(-1)
            if msg is None:
                print("Waiting...")
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                # Extract the (optional) key and value, and print.
                topic=msg.topic()
                key=msg.key().decode('utf-8')
                value=msg.value().decode('utf-8')
                utilise_message(topic, key, value)
                
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()

    