
import json
from confluent_kafka import Producer

TOPIC = 'topic_notification'
KAFKA_CONFIG_FILE = 'kafka_setup_config.json'

# To create instancer of Producer
def create_producer() :
    data = json.load(open(KAFKA_CONFIG_FILE))
    kafka_producer_config = data['kafka_producer_config']
    producer = Producer(kafka_producer_config)
    return producer

# Optional per-message delivery callback (triggered by poll() or flush())
# when a message has been successfully delivered or permanently
# failed delivery (after retries).
def delivery_callback(err, msg):
    if err:
        print("ERROR: Message failed delivery: {}".format(err))
    else:
        print(
            "Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(),
                key=msg.key().decode("utf-8"),
                value=msg.value().decode("utf-8"),
            )
        )

# To produce message
def produce_message(producer, topic, key, value) :
    producer.produce(topic, value, key, on_delivery=delivery_callback)
    
    # Block until the messages are sent.
    producer.poll(10)
    producer.flush()


# Sample Driver Code
if __name__ == '__main__' :
    producer = create_producer()

    while True :    
        print('-------------------------------')
        receiver_email = input('Enter Email : ')
        subject = input('Enter Subject : ')
        body = input('Enter Body : ')

        key = 'mg'
        message = {
            'receiver_email' : receiver_email,
            'subject' : subject,
            'body' : body
        }

        produce_message(producer, TOPIC, key, json.dumps(message))



