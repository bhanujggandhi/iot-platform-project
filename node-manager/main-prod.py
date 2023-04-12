import json

from Messenger import Produce

produce = Produce()

message = {
    "service": "internal-api",
    "app": "",
    "operation": "start",
    "id": "a12",
    "src": "topic_bootstrap",
}

produce.push("topic_node_manager", "", json.dumps(message))
