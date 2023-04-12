import json

from Messenger import Produce

produce = Produce()

message = {"service": "", "app": "myapp1", "operation": "remove", "id": "a12", "src": "topic_internal_api"}

produce.push("topic_node_manager", "", json.dumps(message))
