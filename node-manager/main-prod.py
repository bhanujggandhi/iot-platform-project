import json

from Messenger import Produce

produce = Produce()

message = {
    "service": "init",
    "app": "",
    "operation": "init",
    "id": "a12",
    "src": "topic_bootstrap",
}

produce.push("topic_node_manager", "", json.dumps(message))

# message = {
#     "receiver_email": "gandhibhanuj@gmail.com",
#     "subject": f"app1 Deployed",
#     "body": f"Hello Developer,\nWe have successfully deployed your app at http://0.0.0.0:8000",
# }

# produce.push("topic_notification", "node-manager-deploy", json.dumps(message))
