import json

from Messenger import Produce

produce = Produce()

message = {
    "service": "",
    "app": "myapp4",
    "operation": "remove",
}

produce.push("topic_node_manager", "topic_internal_api", json.dumps(message))
