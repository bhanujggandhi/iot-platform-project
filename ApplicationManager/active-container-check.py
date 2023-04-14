"""
Traverse the MonogoDB active container list to find list of
inactive or dead services and remove their entries
"""

import time
from pymongo import MongoClient

# mongoKey = config("mongoKey")
mongoKey = "mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority"

# Get the list of containers node entries in MongoDB collection
client = MongoClient(mongoKey)
db = client.ActiveNodeDB
collection = db.activeNodeCollection
# find all data in DB
cursor = collection.find()

# Traverse the list and get the difference of current time to the
# last updated timestamp entry in the list
inactive_containers = {}

for document in cursor:
    if "lastUpdated" in document:
        diff = time.time() - document["lastUpdated"]
        if diff > 30:
            # it has been more than 30 seconds since the container gave response
            # by contacting the MongoDB collection and updating its entry
            try:
                inactive_containers[document["ContainerName"]] = (
                    document["IP"],
                    document["Port"],
                )
            except:
                raise RuntimeWarning(
                    "Document is misssing ContainerName, PORT or IP field"
                )

    else:
        raise RuntimeWarning("Document does not have lastUpdated field")

# Get the list of inactive containers and their corresponding VMs in
# which they are running. Then SSH into those VMs and prune those containers
for container_name, address in inactive_containers.items():
    IP, PORT = address
    ssh_key = keymap[f"IP:PORT"]
    command = f"docker container prune {container_name}"

# Requirements:
# - Mapping of container names to the IP:PORT of the VM (to SSH and remove the required containers)
