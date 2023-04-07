# importing the required modules
from json import loads
from kafka import KafkaConsumer
from decouple import config

KAFKA_ADDRESS = config("kafka_address")

# generating the Kafka Consumer
# my_consumer = KafkaConsumer(
#         'test',
#         bootstrap_servers = ['localhost : 9092'],
#         auto_offset_reset = 'earliest',
#         enable_auto_commit = True,
#         group_id = 'my-group',
#         value_deserializer = lambda x : loads(x.decode('utf-8'))
#         )

my_consumer = KafkaConsumer(
    "test", bootstrap_servers=[KAFKA_ADDRESS], value_deserializer=lambda x: loads(x.decode("utf-8"))
)

for message in my_consumer:
    message = message.value
    print(message)
