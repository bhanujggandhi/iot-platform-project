"""
MONITORING SERVICE:
    Assumes:
    * Node Manager is always up
    * API Manager is up when traffic data is asked

    INFORMATION
    Module Names : Sensor Manager, Node Manager, Monitoring Service.

    * MESSAGE format to sent : {"to": "your_topic_name, "src":"topic_monitoring","data": {"operation": "health", "module": "my_module"}}
    * MESSAGE format to receive : {"to": "topic_monitoring", "src":"your_topic_name","data": {"timestamp": time.time() ,"module": "my_module"} }
    * API format for modules which doen't use Kafka : /ping/{module_name}
"""
import json
import threading
import time

import requests
from decouple import config
from Messenger import Consume, Produce
from pymongo import MongoClient

PRODUCER_SLEEP_TIME = 3
CONSUMER_SLEEP_TIME = 1
API_SLEEP_TIME = 5
MAIN_SLEEP_TIME = 1
TRACKING_INTERVAL = 10
TIMEOUT_THRESHOLD = 30
IP = "127.0.0.1"
PORT = "8000"
MY_TOPIC = "topic_monitoring"
MODULE_LIST = []
API_MODULE_LIST = []
CONFIG_FILE_PATH = "./topic_info.json"

# Establish connection to MongoDB
mongokey = config("mongoKey")
client = MongoClient(mongokey)
db = client["platform"]
collection = db["Module_status"]
# app_collection = db["AppCollection"]


# Load topic info from configuration file
def get_service_info(config_file):
    """get the list of topics of the various submodules from the Bootstrap Module"""
    try:
        with open(config_file, "r") as f:
            response = json.load(f)
            # Extract the keys and store them in a list
            Module_list = list(response.keys())
            return response, Module_list
    except FileNotFoundError as e:
        print(f"Configuration file not found: {config_file}")
        return {}, []
    except json.JSONDecodeError as e:
        print(
            f"Failed to decode configuration file: {config_file}. Error: {e}")
        return {}, []


# **********************************|    Dealing with Mongo    |***********************************


# Function to store module health status in MongoDB
def store_health_status(module_name, timestamp):
    try:
        # Create a document with the module name and timestamp
        filter = {"module_name": module_name}
        # Define the update values
        update = {"$set": {"status": "active", "last_updated": timestamp}}
        collection.update_one(filter, update, upsert=True)
    except Exception as e:
        print(
            f"Error: {e}. Failed to store health status for module '{module_name}'")


# Function to get last update timestamp of a specific module from MongoDB
def get_last_update_timestamp(module_name):
    try:
        # Query MongoDB to get the latest document of the specific module based on module_name field
        document = collection.find_one({"module_name": module_name})
        # Extract and return the timestamp from the document
        if document:
            return document["last_updated"]
        else:
            return None
    except Exception as e:
        print(
            f"Error: {e}. Failed to get last update timestamp for module '{module_name}'")
        return None


# Function to update module status in MongoDB
def updateStatus(module_name):
    try:
        # Create a document with the module name and timestamp
        filter = {"module_name": module_name}
        # Define the update values
        update = {"$set": {"status": "inactive"}}
        # app_collection.update_one(filter, update, upsert=True)
    except Exception as e:
        print(
            f"Error: {e}. Failed to update status for module '{module_name}'")


# **********************************| Communication with Modules |***********************************


def apiHealthCheck():
    """
    Health check of modules which does not use Kafka, through API
    """
    while True:
        for module_name in API_MODULE_LIST:
            """need to change this api_url according to api provided by the module for health check"""
            api_url = f"http://{IP}:{PORT}/ping/{module_name}"

            try:
                response_dict = requests.get(api_url).json()
                timestamp = response_dict["time_stamp"]
                # Store module health status in MongoDB
                store_health_status(module_name, float(timestamp))
                return response_dict

            except Exception as e:
                print(e)
                return dict()

        time.sleep(API_SLEEP_TIME)


def postHealthCheck():
    """
    post health messages to all the module's
    """
    print("Post health check messages started... ")
    services, MODULE_LIST = get_service_info(CONFIG_FILE_PATH)
    # topic_names = [value["topic_name"] for value in services.values()]

    if not MODULE_LIST:
        print("Failed to get MODULE_LIST from configuration file. Aborting...")
        return

    produce = Produce()  # Instantiate Kafka producer
    while True:
        try:
            for Module in MODULE_LIST:
                key = ""
                topic_name = services[Module]["topic_name"]

                # needs to decide what message format will be..
                message = {"to": topic_name, "src": "topic_monitoring",
                           "data": {"operation": "health", "module": Module}}
                produce.push(topic_name, key, json.dumps(message))
        except KeyError as e:
            print(f"KeyError: {e}. Failed to post health check message.")
        except Exception as e:
            print(f"Error: {e}. Failed to post health check message.")
        # time interval for next health message to send.
        finally:
            time.sleep(PRODUCER_SLEEP_TIME)


def getHealthStatus():
    """
    Get health status from Kafka topic
    """
    print("Get health status started... ")
    consume = Consume(MY_TOPIC)

    while True:
        try:
            # Get messages from Kafka topic
            resp = consume.pull()
            if resp["status"] == False:
                print(resp["value"])
            else:
                # print(resp["key"], resp["value"])
                value = json.loads(resp["value"])
                # Extract module name and timestamp from the message
                module_name = value['data']['module']
                timestamp = value['data']['timestamp']

                # Check if module_name and timestamp are present in the message
                if module_name is not None and timestamp is not None:
                    # Store module health status in MongoDB
                    store_health_status(module_name, float(timestamp))
                else:
                    print(
                        "Error: Required fields are missing in the health status message.")
        except KeyError as e:
            print(f"Error: {e}. Failed to get health status.")
        except Exception as e:
            print(f"Error: {e}. Failed to get health status.")
        finally:
            time.sleep(CONSUMER_SLEEP_TIME)


# **********************************| Monitoring of Modules |***********************************


def timeOutTracker():
    """
    Method that keep track of all the modules to be monitored
    """
    print("Tracker to monitor modules started....")
    while True:
        try:
            # Check if any module has not responded for a long time
            current_timestamp = time.time()

            # Iterate through the list of modules
            for module_name in MODULE_LIST:
                try:
                    last_update_timestamp = get_last_update_timestamp(
                        module_name)

                    if last_update_timestamp and (current_timestamp - last_update_timestamp) > TIMEOUT_THRESHOLD:
                        # Take action and send notification to admin
                        print(
                            f"Module '{module_name}' has not responded for a long time! Notification sent to admin..")
                        updateStatus(module_name)
                        """
                        TO DO : some more action when required
                        """
                except Exception as e:
                    print(
                        f"Error: {e}. Failed to monitor module '{module_name}' for timeout.")
                    # Continue to the next module in case of any error
                    continue

            # Sleep for a specific interval
            time.sleep(TRACKING_INTERVAL)

        except Exception as e:
            print(f"Error: {e}. Failed to monitor modules to track .")
            continue


if __name__ == "__main__":
    print("Monitoring System Started....")
    # Create a producer to send healthcheck request at regular intervals and update the timeout queue
    producer_thread = threading.Thread(target=postHealthCheck, args=())

    # Create a consumer to consume the message and update the timeout queue
    consumer_thread = threading.Thread(target=getHealthStatus, args=())

    # Create a timeout tracker to keep track of the values in the timeout queue
    tracker_thread = threading.Thread(target=timeOutTracker, args=())

    # start the all the  threads.
    producer_thread.start()
    consumer_thread.start()
    tracker_thread.start()

    try:
        # Keep the main thread running
        while True:
            time.sleep(MAIN_SLEEP_TIME)
    except KeyboardInterrupt:
        # Gracefully terminate threads on keyboard interrupt
        producer_thread.join()
        consumer_thread.join()
        tracker_thread.join()
