# importing the required modules  
from json import loads  
from kafka import KafkaConsumer   

# generating the Kafka Consumer  
# my_consumer = KafkaConsumer(  
#         'test',  
#         bootstrap_servers = ['localhost : 9092'],  
#         auto_offset_reset = 'earliest',  
#         enable_auto_commit = True,  
#         group_id = 'my-group',  
#         value_deserializer = lambda x : loads(x.decode('utf-8'))  
#         )  

my_consumer = KafkaConsumer('test', bootstrap_servers = ['192.168.137.185 : 9092']
                            , value_deserializer = lambda x : loads(x.decode('utf-8'))
                            )

for message in my_consumer:  
    message = message.value
    print(message)