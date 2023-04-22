"""
MONITORING SERVICE:
    Assumes:
    * Node Manager is always up
    * API Manager is up when traffic data is asked

    INFORMATION
    Module Names : Sensor Manager, Node Manager, Monitoring Service.

    * MESSAGE format to sent  : {"to": "<your_topic_name>", "src":"topic_monitoring","data": {"operation": "health", "module": "<my_module>"}}
    * MESSAGE format to receive : {"to": "topic_monitoring", "src":"<your_topic_name>","data": {"timestamp": time.time() ,"module": "<my_module>"} }
    * MESSAGE format for API(module w/o kafka) health check : /ping/{module_name} : {"name": "<module name>", "data": {"timestamp": time.time()}}
    * MESSAGE format for APP health check : {"name": "<app_name>", "data": {"timestamp": time.time()}}

    levels = {0-DEBUG, 1-INFO, 2-WARNING, 3-ERROR, 4-CRITICAL]
    logger.log(service_name = SERVICE_NAME, level = 1, msg = ' < msg > ')
    logger.log(service_name = SERVICE_NAME, level = 1, msg = ' < msg > ', app_name = <app_name>, user_id = <developer_id>)
    
"""
import json
import threading
import time

import requests
from decouple import config
from pymongo import MongoClient
from logger_utils import Logger
from bson import ObjectId
from Messenger import Consume, Produce

PRODUCER_SLEEP_TIME = 3
CONSUMER_SLEEP_TIME = 2
API_SLEEP_TIME = 5
MAIN_SLEEP_TIME = 1
TRACKING_INTERVAL = 10
TIMEOUT_THRESHOLD = 30
IP = "127.0.0.1"
PORT = "8000"

# kafka topics and other related info.
MY_TOPIC = "topic_monitoring"
TOPIC_NOTIFICATION = "topic_notification"
SERVICE_NAME = "monitoring-service"
produce = Produce()  # Instantiate Kafka producer
logger = Logger()  # Instantiate logger

# module information
MODULE_LIST = []  # modules which uses kafka
API_MODULE_LIST = []  # modules which are not using kafka
CONFIG_FILE_PATH = "./topic_info.json"
SERVICES = []

# Establish connection to MongoDB
mongokey = config("mongoKey")
client = MongoClient(mongokey)
db = client["platform"]
collection = db["Module_Status"]
app_collection = db["App"]
app_status_collection = db["App_Status"]
user_collection = db["User"]


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
        print(f"Failed to decode configuration file: {config_file}. Error: {e}")
        return {}, []


# **********************************|    Dealing with Mongo    |***********************************


# Function to store module health status in MongoDB
def store_health_status(module_name, timestamp, status):
    try:
        # Create a document with the module name and timestamp
        filter = {"module_name": module_name}
        # Define the update values
        update = {"$set": {"status": status, "last_updated": timestamp}}
        collection.update_one(filter, update, upsert=True)
    except Exception as e:
        print(f"Error: {e}. Failed to store health status for module '{module_name}'")


# Function to store app health status in MongoDB
def store_app_health_status(app_name, timestamp, status):
    try:
        # Create a document with the module name and timestamp
        filter = {"name": app_name}
        # Define the update values
        update = {"$set": {"status": status, "last_updated": timestamp}}
        app_status_collection.update_one(filter, update, upsert=True)
    except Exception as e:
        print(f"Error: {e}. Failed to store health status for app '{app_name}'")


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
            f"Error: {e}. Failed to get last update timestamp for module '{module_name}'"
        )
        return None


# Function to get last update timestamp of a specific app from MongoDB


def get_app_last_update_timestamp(app_name):
    try:
        # Query MongoDB to get the latest document of the specific module based on module_name field
        document = app_status_collection.find_one({"name": app_name})
        # Extract and return the timestamp from the document
        if document:
            return document["last_updated"]
        else:
            return None
    except Exception as e:
        print(f"Error: {e}. Failed to get last update timestamp for app '{app_name}'")
        return None


# get list of all the active apps.
def getAppData():
    return list(app_collection.find({"active": True}))


# return the mail id of developer associated with the app.
def get_developer_mailid(app_name):
    try:
        # Update status of app to inactive in App collection.
        filter = {"name": app_name}
        update = {"$set": {"active": False}}
        app_collection.update_one(filter, update, upsert=True)
    except Exception as e:
        print(
            f"Error: {e}. Failed to store health status for app '{app_name}' in App collection."
        )
        return None

    try:
        # Get developer id from App collection associated with this app.
        document = app_collection.find_one({"name": app_name})
        if document:
            developer_id = str(document["developer"])
        else:
            print(f"No app found with name '{app_name}' in App collection.")
            return None
    except Exception as e:
        print(f"Error: {e}. Failed to get developer id for '{app_name}' app.")
        return None

    try:
        # Get developer mail id from User collection.
        document = user_collection.find_one({"_id": ObjectId(developer_id)})
        if document:
            developer_mailid = str(document["email"])
            developer_name = str(document["name"])
        else:
            print(f"No user found with id '{developer_id}' in User collection.")
            return None
    except Exception as e:
        print(f"Error: {e}. Failed to get developer mail id for '{app_name}' app.")
        return None

    return developer_mailid, developer_name


# send notification to developer if app crashed.
def notify_to_developer(app_name):
    try:
        developer_mailid, developer_name = get_developer_mailid(app_name)
        if not developer_mailid:
            print(
                f"Could not retrieve developer email for app '{app_name}'. Notification not sent."
            )
            return False
    except Exception as e:
        print(
            f"Error: {e}. Could not retrieve developer email for app '{app_name}'. Notification not sent."
        )
        return False

    subject = f"URGENT Your app '{app_name}' has crashed!"
    body = f"Dear '{developer_name}',We regret to inform you that your app, '{app_name}' has crashed."

    key = ""
    message = {"receiver_email": developer_mailid, "subject": subject, "body": body}

    try:
        produce.push(TOPIC_NOTIFICATION, key, json.dumps(message))
        print(
            f"Notification sent to developer '{developer_mailid}' for app '{app_name}'."
        )
        return True
    except Exception as e:
        print(
            f"Error: {e}. Failed to send notification to developer '{developer_mailid}' for app '{app_name}'."
        )
        return False


# **********************************| Communication with Modules |***********************************


def appHealthCheck():
    """
    Health check of Applications deployed on the platform which are currently active.
    """
    print("App health check started... ")
    while True:
        app_list = getAppData()

        for app in app_list:
            app_api_url = f"http://{app['ip']}:{app['port']}/ping"
            try:
                response_dict = requests.get(app_api_url).json()
                timestamp = response_dict["data"]["time_stamp"]

                # Store app health status in MongoDB
                store_app_health_status(app["name"], timestamp, "active")

                return response_dict

            except Exception as e:
                print(e)
                return dict()

        time.sleep(API_SLEEP_TIME)


def apiHealthCheck():
    """
    Health check of modules which does not use Kafka, through API
    """
    print("Api health Check started... ")
    while True:
        for module_name in API_MODULE_LIST:
            """need to change this api_url according to api provided by the module for health check"""
            api_url = f"http://{IP}:{PORT}/ping/{module_name}"

            try:
                response_dict = requests.get(api_url).json()
                timestamp = response_dict["time_stamp"]
                # Store module health status in MongoDB
                store_health_status(module_name, float(timestamp), "active")
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
    # topic_names = [value["topic_name"] for value in SERVICES.values()]

    if not MODULE_LIST:
        print("Failed to get MODULE_LIST from configuration file. Aborting...")
        return

    while True:
        try:
            for Module in MODULE_LIST:
                key = ""
                topic_name = SERVICES[Module]["topic_name"]

                # needs to decide what message format will be..
                message = {
                    "to": topic_name,
                    "src": "topic_monitoring",
                    "data": {"operation": "health", "module": Module},
                }
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
                module_name = value["data"]["module"]
                timestamp = value["data"]["timestamp"]

                # Check if module_name and timestamp are present in the message
                if module_name is not None and timestamp is not None:
                    # Store module health status in MongoDB
                    store_health_status(module_name, float(timestamp), "active")
                else:
                    print(
                        "Error: Required fields are missing in the health status message."
                    )
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
                    last_update_timestamp = get_last_update_timestamp(module_name)

                    if (
                        last_update_timestamp
                        and (current_timestamp - last_update_timestamp)
                        > TIMEOUT_THRESHOLD
                    ):
                        # Take action and send notification to admin
                        print(
                            f"Module '{module_name}' has not responded for a long time! Notification sent to admin.."
                        )
                        store_health_status(
                            module_name, last_update_timestamp, "inactive"
                        )
                        """
                        TO DO : some more action when required
                        """
                except Exception as e:
                    print(
                        f"Error: {e}. Failed to monitor module '{module_name}' for timeout."
                    )
                    # Continue to the next module in case of any error
                    continue

            # Iterate through the list of apps
            for app_name in getAppData():
                try:
                    last_update_timestamp = get_app_last_update_timestamp(app_name)

                    if (
                        last_update_timestamp
                        and (current_timestamp - last_update_timestamp)
                        > TIMEOUT_THRESHOLD
                    ):
                        # Take action and send notification to admin/dev
                        print(
                            f"App '{app_name}' has not responded for a long time! Notification sent to admin/dev.."
                        )
                        store_app_health_status(
                            app_name, last_update_timestamp, "inactive"
                        )
                        notify_to_developer(app_name)
                except Exception as e:
                    print(
                        f"Error: {e}. Failed to monitor app '{app_name}' for timeout."
                    )
                    # Continue to the next app in case of any error
                    continue

            # Sleep for a specific interval
            time.sleep(TRACKING_INTERVAL)

        except Exception as e:
            print(f"Error: {e}. Failed to monitor modules to track .")
            continue


if __name__ == "__main__":
    print("Monitoring System Started....")
    SERVICES, MODULE_LIST = get_service_info(CONFIG_FILE_PATH)
    # Create a producer to send healthcheck request at regular intervals and update the timeout queue
    producer_thread = threading.Thread(target=postHealthCheck, args=())

    # Create a consumer to consume the message and update the timeout queue
    consumer_thread = threading.Thread(target=getHealthStatus, args=())

    # Create a thread for app healthcheck  at regular intervals and update the timeout queue
    appHealth_thread = threading.Thread(target=appHealthCheck, args=())

    time.sleep(TRACKING_INTERVAL)
    # Create a timeout tracker to keep track of the values in the timeout queue
    tracker_thread = threading.Thread(target=timeOutTracker, args=())

    # start the all the  threads.
    producer_thread.start()
    appHealth_thread.start()
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
        appHealth_thread.join()
        tracker_thread.join()
