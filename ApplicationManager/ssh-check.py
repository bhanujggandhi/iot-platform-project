"""
Use SSH command to get the docker stats from remote machine
"""
import subprocess
import json
import time
from pymongo import MongoClient

# mongoKey = config("mongoKey")
mongoKey = "mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority"
path = "./Kafka-VM_key.pem"

# Get the list of public keys of various remote machines
# keymap = {"q13asdlkj44tq343908": ("ardhendu", "192.168.204.238")}
keymap = {"q13asdlkj44tq343908": ("azureuser", "74.235.240.222")}

while True:
    # time.sleep(10)

    # TODO: Get the SSH key to IP mappings

    # SSH into each machine and run the docker ps command to get the stats
    for key, value in keymap.items():
        user, address = value
        # IP, PORT = address.split(":")
        # command = f"ssh {user}@{address} 'docker ps'"
        try:
            command = f"ssh -i {path} {user}@{address} 'sudo docker ps'"

        except err:
            print("Unable to SSH into the VM. ERROR: ", err)

        response = subprocess.check_output(command, shell=True).decode("utf-8")
        print(response)

        # TODO: Modify the output to proper JSON format

    break
    # Send the stats of each container seperatly by using the ID and container name
    # as key to edit the specific row in the MongoDB collection
    # client = MongoClient(mongoKey)
    # db = client.ActiveNodeDB
    # collection = db.activeNodeCollection
    # try:
    #     collection.insert_one(response)
    # except:
    #     raise RuntimeWarning("Unable to insert entry into activeNodeCollection")
