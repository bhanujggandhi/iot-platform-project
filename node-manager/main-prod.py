import json

from Messenger import Produce

produce = Produce()

message = {
    "service": "internal-api",
    "app": "",
    "operation": "remove",
    "id": "a12",
    "src": "topic_bootstrap",
}

produce.push("topic_node_manager", "", json.dumps(message))

# message = {
#     "sensorId": "ifbouefvb",
#     "duration": 10,
#     "fetchType": "RT",
#     "startTime": 1,
#     "endTime": 10,
#     "src": "topic_internal_api"
# }

# produce.push("topic_sensor_manager", "", json.dumps(message))
