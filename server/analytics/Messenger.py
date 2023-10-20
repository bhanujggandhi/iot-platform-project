import json
from confluent_kafka import Producer, Consumer

KAFKA_CONFIG_FILE = "kafka_setup_config.json"


class Produce:
    def __init__(self):
        self.data = json.load(open(KAFKA_CONFIG_FILE))
        self.kafka_producer_config = self.data["kafka_producer_config"]
        self.producer = Producer(self.kafka_producer_config)

    def delivery_callback(self, err, msg):
        if err:
            print("ERROR: Message failed delivery: {}".format(err))
        else:
            pass
            # print(
            #     "Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
            #         topic=msg.topic(),
            #         key=msg.key().decode("utf-8"),
            #         value=msg.value().decode("utf-8"),
            #     )
            # )

    def push(self, topic, key, value):
        self.producer.produce(topic, value, key, on_delivery=self.delivery_callback)

        # Block until the messages are sent.
        self.producer.poll(10)
        self.producer.flush()



class Consume:
    def __init__(self, topic):
        self.topic = topic
        self.data = json.load(open(KAFKA_CONFIG_FILE))
        self.kafka_consumer_config = self.data["kafka_consumer_config"]
        self.kafka_consumer_config["group.id"] = f"group_{self.topic}"
        self.consumer = Consumer(self.kafka_consumer_config)
        self.consumer.subscribe([self.topic])

    def pull(self):
        # Checking for message till the message is not found.
        while True:
            msg = self.consumer.poll(1.0)
            if msg is not None:
                break

        if msg.error():
            return {"status": False, "key": None, "value": format(msg.error())}

        else:
            # Extract the (optional) key and value, and print.
            # topic=msg.topic()
            key = msg.key().decode("utf-8")
            value = msg.value().decode("utf-8")
            return {"status": True, "key": key, "value": value}
