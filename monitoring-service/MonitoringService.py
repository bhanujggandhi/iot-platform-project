"""
MONITORING SERVICE:
    * Gets initalized with a config file describing:
        - The rules for determining threshold

    * Will monitor the levels of CPU and memory usage for each instance of the 
    node in the node manager. It will use the rules in the config file to inform
    the node manager in case there is need of upscaling and downscaling.

    * Get the health status of all platform modules by hitting their healthcheck
    API.

    * Get the metrics of all services from the response time logs created by API Manager

    Assumes:
    * Node Manager is always up
    * API Manager is up when traffic data is asked
"""
import requests
import json

import time
import sys
import threading
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer, OFFSET_BEGINNING
from confluent_kafka import Producer


def getServiceInfo(filePath: str) -> dict:
    """get the list of topics of the various submodules from the Bootstrap Module"""
    # For now, we will get the topic info from dummy topic info file
    with open(filePath, "r") as f:
        response = json.load(f)

    return response


def getTrafficLogs(service_info) -> dict:
    """Get the traffic logs from the API Manager module"""

    # get the IP and PORT of APIManager
    try:
        socket_address = service_info["APIManager"]
        IP = socket_address["IP"]
        PORT = socket_address["PORT"]
    except Exception as e:
        print(f"{e} is not in list of services")
        return dict()

    api_url = f"http://{IP}:{PORT}/traffic_logs"
    # get the response from the module at IP:PORT
    try:
        response = requests.get(api_url)
        return response

    except Exception as e:
        print(e)
        return dict()


def extractQoSValues(traffic_logs: dict) -> None:
    for microservice_name, logs in traffic_logs.items():
        requests = logs["requests"]
        responses = logs["responses"]

        total = min(len(requests), len(responses))

        response_times = []

        for query in range(total):
            response_times.append(responses[query] - requests[query])

        print(f"Reponse Time for {microservice_name}: ")
        print(response_times)

        # TODO: Store the Qos Values in the database


# def getQoSValues() -> dict:
#     """Send QoS values"""
#     report = {
#         "serviceName": microservice_A,
#         "QoS": 2.0341,
#     }
#     headers = {"Content-Type": "application/json"}
#
#     # get the IP and PORT of NodeManager
#     socket_address = service_info["APIManager"]
#     IP = socket_address["IP"]
#     PORT = socket_address["PORT"]
#
#     api_url = f"http://{IP}:{PORT}/sendQoSVals"
#     response = requests.post(api_url, json=report)
#     print(response.json())


def healthCheck(config, frequency) -> None:
    # Create Producer instance
    producer = Producer(config)

    # Optional per-message delivery callback (triggered by poll() or flush())
    # when a message has been successfully delivered or permanently
    # failed delivery (after retries).
    def delivery_callback(err, msg):
        if err:
            print(f"ERROR: Message failed delivery: {err}")
        else:
            print(f"Healthcheck sent to {msg.topic()}")
            # print(
            #     "Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
            #         topic=msg.topic(),
            #         key=msg.key().decode("utf-8"),
            #         value=msg.value().decode("utf-8"),
            #     )
            # )

    services = getServiceInfo("./topic_info.json")

    while True:
        time.sleep(frequency)
        for service_name, service_data in services.items():
            producer.produce(
                service_data["topic_name"],
                "",
                "healthcheck",
                on_delivery=delivery_callback,
            )

        print("Healthcheck done")

        # Block until the messages are sent.
        producer.poll(10)
        producer.flush()


def getHealthStatus(config) -> None:
    # Set up a callback to handle the '--reset' flag.
    def reset_offset(consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            consumer.assign(partitions)

    # Create Consumer instance
    consumer = Consumer(config)

    # Subscribe to topic
    topic = "topic_monitoring"
    consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages for the Monitoring topic
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            # Initial message consumption may take up to
            # `session.timeout.ms` for the consumer group to
            # rebalance and start consuming
            print("Waiting...")
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            # Extract the (optional) key and value, and print.
            print(msg)
            print(f"{msg.topic()}: [UP]")
            # print("Consumed event from topic {topic}: key = {key:12} value = {value:12}".format(
            #     topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))


if __name__ == "__main__":
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument("config_file", type=FileType("r"))
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    # Parse the configuration.
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser["default"])
    config.update(config_parser["consumer"])

    # healthCheck(config)
    # getHealthStatus(config)
    frequency = 5

    # Create a producer to send healthcheck request at regular intervals
    # and update the timeout queue
    producer_thread = threading.Thread(target=healthCheck, args=(config, frequency))

    # Create a consumer to consume the message and update the timeout queue
    consumer_thread = threading.Thread(target=getHealthStatus, args=(config,))

    # TODO: Create a timeout tracker to keep track of the values in the timeout queue

    # start the two threads
    producer_thread.start()
    consumer_thread.start()
