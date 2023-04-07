from time import sleep
from json import dumps
from kafka import KafkaProducer
from decouple import config

KAFKA_ADDRESS = config("kafka_address")

# initializing the Kafka producer
my_producer = KafkaProducer(bootstrap_servers=[KAFKA_ADDRESS], value_serializer=lambda x: dumps(x).encode("utf-8"))

# generating the numbers ranging from 1 to 500
for n in range(500):
    my_data = {"num": n}
    my_producer.send("test", value=my_data)
    sleep(1)
