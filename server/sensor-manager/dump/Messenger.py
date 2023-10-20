from kafka import KafkaProducer, KafkaConsumer
from json import dumps, loads

KAFKA_IP_PORT = "20.244.37.218:9092"


class Produce:
    def __init__(self):
        self.my_producer = KafkaProducer(
            bootstrap_servers=[KAFKA_IP_PORT],
            value_serializer=lambda x: dumps(x).encode("utf-8"),
        )

    def push(self, topic, key, message):
        try:
            self.my_producer.send(topic, value=message)
            self.my_producer.flush(timeout=10)
        except:
            print("pass")
            pass


class Consume:
    def __init__(self, topic):
        self.my_consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[KAFKA_IP_PORT],
            group_id=f"group_{topic}",
            value_deserializer=lambda x: loads(x.decode("utf-8")),
        )

    def pull(self):
        flag = 1
        x = None
        while flag:
            x = self.my_consumer.poll(timeout_ms=1000, max_records=1)
            if len(x) == 0:
                flag = 1
            else:
                flag = 0
        for key in x:
            data = x[key][0].value
            return {"status": True, "key": "", "value": data}
