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

# message = {
#     "sensorId": "ifbouefvb",
#     "duration": 10,
#     "fetchType": "RT",
#     "startTime": 1,
#     "endTime": 10,
#     "src": "topic_internal_api"
# }

# produce.push("topic_sensor_manager", "", json.dumps(message))
