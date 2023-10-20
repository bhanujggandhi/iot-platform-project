"""
MONITORING SERVICE:
    Assumes:
    * Node Manager is always up

    INFORMATION

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
from bson import ObjectId
from decouple import config
from pymongo import MongoClient

from Messenger import Consume, Produce
from logger_utils import Logger

ADMIN_NAME = "Bhanuj Gandhi"
ADMIN_MAILID = "gandhibhanuj@gmail.com"

# Load configuration from config_intervals.json file
with open("config_intervals.json", "r") as f:
    config_int = json.load(f)

# Get configuration values
PRODUCER_SLEEP_TIME = config_int["PRODUCER_SLEEP_TIME"]
CONSUMER_SLEEP_TIME = config_int["CONSUMER_SLEEP_TIME"]
API_SLEEP_TIME = config_int["API_SLEEP_TIME"]
MAIN_SLEEP_TIME = config_int["MAIN_SLEEP_TIME"]
TRACKING_INTERVAL = config_int["TRACKING_INTERVAL"]
TIMEOUT_THRESHOLD = config_int["TIMEOUT_THRESHOLD"]
IP = config_int["IP"]
PORT = config_int["PORT"]
MY_TOPIC = config_int["MY_TOPIC"]
TOPIC_NOTIFICATION = config_int["TOPIC_NOTIFICATION"]
SERVICE_NAME = config_int["SERVICE_NAME"]

produce = Produce()  # Instantiate Kafka producer
logger = Logger()  # Instantiate logger

# module information
MODULE_LIST = []  # modules which uses kafka
API_MODULE_LIST = ["internal-api"]  # modules which are not using kafka
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
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Configuration file not found: {config_file}",
        )
        return {}, []
    except json.JSONDecodeError as e:
        print(f"Failed to decode configuration file: {config_file}. Error: {e}")
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Failed to decode configuration file: {config_file}. Error: {e}",
        )
        return {}, []


# ***************************************|    Dealing with Mongo    |**********************************


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
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Error: {e}. Failed to store health status for module '{module_name}'",
        )


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
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Error: {e}. Failed to store health status for app '{app_name}'",
            app_name=app_name,
            user_id=get_developer_mailid(app_name)[0],
        )


# Function to get last update timestamp of a specific module from MongoDB
def get_last_update_timestamp(module_name):
    try:
        # Query MongoDB to get the latest document of the specific module based on module_name field
        document = collection.find_one({"module_name": module_name, "status": "active"})
        # Extract and return the timestamp from the document
        if document:
            return document["last_updated"]
        else:
            return None
    except Exception as e:
        print(
            f"Error: {e}. Failed to get last update timestamp for module '{module_name}'"
        )
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Error: {e}. Failed to get last update timestamp for module '{module_name}'",
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
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Error: {e}. Failed to get last update timestamp for app '{app_name}'",
            app_name=app_name,
            user_id=get_developer_mailid(app_name)[0],
        )
        return None


# get list of all the active apps.
def getAppData():
    return list(collection.find({"active": True}))


# init Module_Status and App_Status collection in MongoDb
def init_ModuleStatus_AppStatus():
    for module in MODULE_LIST:
        store_health_status(module, time.time(), "active")

    for module in API_MODULE_LIST:
        store_health_status(module, time.time(), "active")

    app_list = getAppData()
    for app in app_list:
        store_app_health_status(app["name"], time.time(), "active")


# Refresh app status from APP Collection in a time interval dynamically.


def refresh_app_status():
    app_list = getAppData()
    for app_name in app_list:
        try:
            # Create a document with the module name and timestamp
            filter = {"name": app_name}
            # Define the update values
            update = {"$set": {"status": "active", "last_updated": time.time()}}
            app_status_collection.update_one(filter, update, upsert=True)
        except Exception as e:
            print(f"Error: {e}. Failed to refresh health status for app '{app_name}'")
            logger.log(
                service_name=SERVICE_NAME,
                level=3,
                msg=f"Error: {e}. Failed to refresh health status for app '{app_name}'",
                app_name=app_name,
                user_id=get_developer_mailid(app_name)[0],
            )


# return the mail id of developer associated with the app.


def get_developer_mailid(app_name):
    try:
        # Get developer id from App collection associated with this app.
        document = app_collection.find_one({"name": app_name})
        if document:
            developer_id = document["user"]
        else:
            print(f"No app found with name '{app_name}' in App collection.")
            logger.log(
                service_name=SERVICE_NAME,
                level=2,
                msg=f"No app found with name '{app_name}' in App collection.",
                app_name=app_name,
                user_id=developer_id,
            )
            return None
    except Exception as e:
        print(f"Error: {e}. Failed to get developer id for '{app_name}' app.")
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Error: {e}. Failed to get developer id for '{app_name}' app.",
            app_name=app_name,
            user_id=developer_id,
        )
        return None
    try:
        # Get developer mail id from User collection.
        document = user_collection.find_one({"_id": ObjectId(developer_id)})
        if document:
            developer_mailid = str(document["email"])
            developer_name = str(document["name"])
        else:
            print(f"No user found with id '{developer_id}' in User collection.")
            logger.log(
                service_name=SERVICE_NAME,
                level=2,
                msg=f"No user found with id '{developer_id}' in User collection.",
            )
            return None
    except Exception as e:
        print(f"Error: {e}. Failed to get developer mail id for '{app_name}' app.")
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Error: {e}. Failed to get developer mail id for '{app_name}' app.",
            app_name=app_name,
            user_id=developer_id,
        )
        return None

    return developer_mailid, developer_name


# check module is active or not.
def is_active(module_name):
    active_modules = app_collection.count_documents(
        {"module_name": module_name, "status": "active"}
    )
    return active_modules > 0


# ***************************************| Notification services |**********************************


# send notification to developer if app crashed.
def notify_to_developer(app_name):
    try:
        # Update status of app to inactive in App collection.
        filter = {"name": app_name}
        update = {"$set": {"active": False}}
        update_status = {"$set": {"status": "inactive"}}
        app_status_collection.update_one(filter, update_status, upsert=True)
        app_collection.update_one(filter, update, upsert=True)
    except Exception as e:
        print(
            f"Error: {e}. Failed to store health status for app '{app_name}' in App and app_status collections."
        )
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Error: {e}. Failed to store health status for app '{app_name}' in App and app_status collections.",
            app_name=app_name,
        )

    try:
        developer_mailid, developer_name = get_developer_mailid(app_name)
        if not developer_mailid:
            print(
                f"Could not retrieve developer email for app '{app_name}'. Notification not sent."
            )
            logger.log(
                service_name=SERVICE_NAME,
                level=3,
                msg=f"Could not retrieve developer email for app '{app_name}'. Notification not sent.",
                app_name=app_name,
            )
            return False
    except Exception as e:
        print(
            f"Error: {e}. Could not retrieve developer email for app '{app_name}'. Notification not sent."
        )
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Could not retrieve developer email for app '{app_name}'. Notification not sent.",
            app_name=app_name,
        )
        return False

    subject = f"URGENT Your app '{app_name}' has crashed!"
    body = f"Dear {developer_name}, \nWe regret to inform you that your app, '{app_name}' has crashed."

    key = ""
    message = {"receiver_email": developer_mailid, "subject": subject, "body": body}

    try:
        produce.push(TOPIC_NOTIFICATION, key, json.dumps(message))
        print(
            f"Notification sent to developer '{developer_mailid}' for app '{app_name}'."
        )
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg=f"Notification sent to developer '{developer_mailid}' for app '{app_name}'.",
            app_name=app_name,
            user_id=developer_mailid,
        )
        return True
    except Exception as e:
        print(
            f"Error: {e}. Failed to send notification to developer '{developer_mailid}' for app '{app_name}'."
        )
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Error: {e}. Failed to send notification to developer '{developer_mailid}' for app '{app_name}'.",
            app_name=app_name,
            user_id=developer_mailid,
        )
        return False


def notify_to_admin(module_name):
    admin_name = ADMIN_NAME
    admin_mailid = ADMIN_MAILID
    subject = f"URGENT, In your platform '{module_name}' has crashed!"
    body = f"Dear {admin_name}, \nWe regret to inform you that In your platform, module '{module_name}' has crashed please try to restart."
    key = ""
    message = {"receiver_email": admin_mailid, "subject": subject, "body": body}

    try:
        produce.push(TOPIC_NOTIFICATION, key, json.dumps(message))
        print(
            f"Notification sent to Admin '{admin_mailid}' for module '{module_name}'."
        )
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg=f"Notification sent to admin '{admin_mailid}' for module '{module_name}'.",
        )
        return True
    except Exception as e:
        print(
            f"Error: {e}. Failed to send notification to admin '{admin_mailid}' for module '{module_name}'."
        )
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Error: {e}. Failed to send notification to admin '{admin_mailid}' for module '{module_name}'.",
        )
        return False


# ***************************************| Communication with Modules |**********************************


def appHealthCheck():
    """
    Health check of Applications deployed on the platform which are currently active.
    """
    print("App health check started... ")

    flag = 1
    while True:
        if flag == 0:
            refresh_app_status()
            print("Refresh cycle: Application status has been refreshed.")
        else:
            flag = (flag + 1) % 4

        app_list = getAppData()
        for app in app_list:
            app_api_url = f"http://{app['ip']}:{app['port']}/ping"
            try:
                response_dict = requests.get(app_api_url).json()
                timestamp = response_dict["data"]["time_stamp"]

                # store app health status in App_Status Collection
                store_app_health_status(app["name"], timestamp, "active")

            except Exception as e:
                print(f"Error {e} in appHealthCheck().")
                logger.log(
                    service_name=SERVICE_NAME,
                    level=3,
                    msg=f"Error {e} in appHealthCheck().",
                    app_name=app["name"],
                    user_id=get_developer_mailid(app["name"])[0],
                )

        time.sleep(API_SLEEP_TIME)


def apiHealthCheck():
    """
    Health check of modules which does not use Kafka, through API
    """
    print("Api health Check started... ")
    while True:
        for module_name in API_MODULE_LIST:
            if is_active(module_name):
                """need to change this api_url according to api provided by the module for health check"""
                api_url = f"http://{module_name}:5000/ping/{module_name}"

                try:
                    response_dict = requests.get(api_url).json()
                    timestamp = response_dict["time_stamp"]
                    # Store module health status in MongoDB
                    store_health_status(module_name, float(timestamp), "active")

                except Exception as e:
                    print(
                        f"Error: '{module_name}' is not responding in apiHealthCheck()."
                    )
                    logger.log(
                        service_name=SERVICE_NAME,
                        level=3,
                        msg=f"Error {e} in apiHealthCheck().",
                    )

        time.sleep(API_SLEEP_TIME)


def postHealthCheck():
    """
    post health messages to all the module's
    """
    print("Post health check started... ")
    # topic_names = [value["topic_name"] for value in SERVICES.values()]

    if not MODULE_LIST:
        print("Failed to get MODULE_LIST from configuration file. Aborting...")
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg="Failed to get MODULE_LIST from configuration file. Aborting...",
        )
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
            logger.log(
                service_name=SERVICE_NAME,
                level=3,
                msg=f"KeyError: {e}. Failed to post health check message.",
            )
        except Exception as e:
            print(f"Error: {e}. Failed to post health check message.")
            logger.log(
                service_name=SERVICE_NAME,
                level=3,
                msg=f"Error: {e}. Failed to post health check message.",
            )
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
                    logger.log(
                        service_name=SERVICE_NAME,
                        level=3,
                        msg="Error: Required fields are missing in the health status message.",
                    )
        except Exception as e:
            print(f"Error: {e}. Failed to get health status.")
            logger.log(
                service_name=SERVICE_NAME,
                level=3,
                msg=f"Error: {e}. Failed to get health status.",
            )
        finally:
            time.sleep(CONSUMER_SLEEP_TIME)


# *********************************| Monitoring of Modules |************************************


def timeOutTracker():
    """
    Method that keep track of all the modules to be monitored
    """
    time.sleep(TRACKING_INTERVAL)
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
                        logger.log(
                            service_name=SERVICE_NAME,
                            level=2,
                            msg=f"Module '{module_name}' has not responded for a long time! Notification sent to admin..",
                        )
                        store_health_status(
                            module_name, last_update_timestamp, "inactive"
                        )
                        notify_to_admin(module_name)
                except Exception as e:
                    print(
                        f"Error: {e}. Failed to monitor module '{module_name}' for timeout."
                    )
                    logger.log(
                        service_name=SERVICE_NAME,
                        level=3,
                        msg=f"Error: {e}. Failed to monitor module '{module_name}' for timeout.",
                    )
                    # Continue to the next module in case of any error
                    continue

            # Iterate through the list of apps
            app_list = getAppData()
            for app in app_list:
                app_name = app["name"]
                try:
                    last_update_timestamp = get_app_last_update_timestamp(app_name)

                    if (
                        last_update_timestamp
                        and (current_timestamp - last_update_timestamp)
                        > TIMEOUT_THRESHOLD
                    ):
                        # Take action and send notification to admin/dev
                        print(
                            f"App '{app_name}' has not responded for a long time! Notification sent to developer.."
                        )
                        logger.log(
                            service_name=SERVICE_NAME,
                            level=2,
                            msg=f"App '{app_name}' has not responded for a long time! Notification sent to developer..",
                            app_name=app_name,
                            user_id=get_developer_mailid(app_name)[0],
                        )
                        store_app_health_status(
                            app_name, last_update_timestamp, "inactive"
                        )
                        notify_to_developer(app_name)
                except Exception as e:
                    print(
                        f"Error: {e}. Failed to monitor app '{app_name}' for timeout."
                    )
                    logger.log(
                        service_name=SERVICE_NAME,
                        level=3,
                        msg=f"Error: {e}. Failed to monitor app '{app_name}' for timeout.",
                        app_name=app_name,
                        user_id=get_developer_mailid(app_name)[0],
                    )
                    # Continue to the next app in case of any error
                    continue

            # Sleep for a specific interval
            time.sleep(TRACKING_INTERVAL)

        except Exception as e:
            print(f"Error: {e}. Failed to monitor modules to track .")
            logger.log(
                service_name=SERVICE_NAME,
                level=3,
                msg=f"Error: {e}. Failed to monitor modules to track .",
            )
            continue


if __name__ == "__main__":
    print("Monitoring System Started....")
    SERVICES, MODULE_LIST = get_service_info(CONFIG_FILE_PATH)
    init_ModuleStatus_AppStatus()
    # Create a producer to send healthcheck request at regular intervals and update the timeout queue
    producer_thread = threading.Thread(target=postHealthCheck, args=())

    # Create a consumer to consume the message and update the timeout queue
    consumer_thread = threading.Thread(target=getHealthStatus, args=())

    # Create a thread for app healthcheck  at regular intervals and update the timeout queue
    appHealth_thread = threading.Thread(target=appHealthCheck, args=())

    # Create a thread for Api healthcheck  at regular intervals and update the timeout queue
    apiHealth_thread = threading.Thread(target=apiHealthCheck, args=())

    # Create a timeout tracker to keep track of the values in the timeout queue
    tracker_thread = threading.Thread(target=timeOutTracker, args=())

    # start the all the  threads.
    producer_thread.start()
    appHealth_thread.start()
    consumer_thread.start()
    apiHealth_thread.start()
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
        apiHealth_thread.join()
        tracker_thread.join()
