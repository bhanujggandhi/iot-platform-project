import json

from Messenger import Produce

produce = Produce()

message = {
    "service": "sensor-manager",
    "app": "",
    "operation": "remove",
    "id": "a12",
    "src": "topic_internal_api",
}

produce.push("topic_node_manager", "", json.dumps(message))
