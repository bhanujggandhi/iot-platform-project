import json

from Messenger import Produce

produce = Produce()

message = {
    "service": "platform",
    "app": "",
    "operation": "init",
    "src": "topic_bootstrap",
    "appid": "",
    "userid": "",
}

produce.push("topic_node_manager", "", json.dumps(message))
print("Signal sent to node manager to start all the modules")
