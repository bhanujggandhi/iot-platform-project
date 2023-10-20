"""
HEARTBEAT SERVICE FROM MONITORING :

Use this module to implement a heartbeat service that responds to health check requests from a monitoring service. 

INSTRUCTIONS:

0. Copy and paste logger_utils, Messenger and this file into your directory where main.py is runnning

1. Import the following:
    ```
    import threading
    from heartbeat_service import HeartbeatService
    import atexit
    ```

2. Initialize the HeartbeatService object with your Kafka topic name and your service name:
    ```
    TOPIC = "<your-topic-name>" # Replace with your topic name
    SERVICE_NAME = "<your-service-name>" # Replace with your service name

    # Create a new instance of the HeartbeatService class
    heartbeat_service = HeartbeatService(TOPIC, SERVICE_NAME)
    ```

3. Start the heartbeat service as a thread:
    ```
    # Create a new thread and start the HeartbeatService instance
    thread = threading.Thread(target=heartbeat_service.start)
    thread.daemon = True
    thread.start()
    ```
"""
import json
import time
from logger_utils import Logger
from Messenger import Consume, Produce


class HeartbeatService:
    def __init__(self, topic, service_name):
        self.topic = topic
        self.service_name = service_name
        self.logger = Logger()
        self.consume = Consume(self.topic)
        self.produce = Produce()
        self.running = False

    def utilise_message(self, value):
        value = json.loads(value)
        # If the message consumed is for health checkup.
        if "to" in value.keys() and "src" in value.keys() and "data" in value.keys():
            if value["src"] == "topic_monitoring":
                try:
                    data = {"timestamp": time.time(
                    ), "module": value["data"]["module"]}
                    key = ""
                    message = {"to": value["src"],
                               "src": value["to"], "data": data}
                    self.produce.push(value["src"], key, json.dumps(message))

                    msg = f"Replied to Monitoring Service for Health Checkup Request with timestamp : {data['timestamp']}."
                    self.logger.log(
                        service_name=self.service_name, level=0, msg=msg)
                except Exception as e:
                    msg = f"Invalid Arguments found while consuming from Kafka Topic : {self.topic}. Error: {str(e)}"
                    print(msg)
                    self.logger.log(
                        service_name=self.service_name, level=2, msg=msg)

            else:
                msg = f"Invalid Arguments found while consuming from Kafka Topic : {self.topic}."
                print(msg)
                self.logger.log(service_name=self.service_name,
                                level=2, msg=msg)

        else:
            msg = f"Invalid Arguments found while consuming from Kafka Topic : {self.topic}."
            print(msg)
            self.logger.log(service_name=self.service_name, level=2, msg=msg)

    def heartbeat_service(self):
        print("Heartbeat service started... ")
        while self.running:
            resp = self.consume.pull()
            if resp["status"] == False:
                msg = f"Error while consuming from Kafka Topic : {self.topic}. Error: {resp['value']}"
                print(msg)
                self.logger.log(service_name=self.service_name,
                                level=2, msg=msg)
            else:
                self.utilise_message(resp["value"])
        print("Heartbeat service stopped... ")

    def start(self):
        try:
            self.running = True
            self.heartbeat_service()
        except Exception as e:
            msg = f"Error while running Heartbeat Service. Error: {str(e)}"
            print(msg)
            self.logger.log(service_name=self.service_name, level=2, msg=msg)

    def stop(self):
        self.running = False
