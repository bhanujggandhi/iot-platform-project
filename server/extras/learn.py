# import xml.etree.ElementTree as ET

# tree = ET.parse("metadata.xml")
# root = tree.getroot()
# print(root)


# name = root.find("name").text
# version = root.find("version").text

# author = {}
# for auth in root.find("author"):
#     author[auth.get("name")] = auth.get("value")


# config = {}
# # for setting in root.find("config"):
# #     config[setting.get("name")] = setting.get("value")

# print(name, version, author, config)


import json

import jsonschema
import yaml

# Load the YAML file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# print(config)

with open("out.txt", "w") as f:
    json.dump(config, f)

appname = "myapp1"

deployment = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {"name": appname, "labels": {"app": appname}},
    "spec": {
        "replicas": 2,
        "selector": {"matchLabels": {"app": appname}},
        "strategy": {"type": "RollingUpdate", "rollingUpdate": {"maxSurge": 3}},
        "template": {
            "metadata": {"labels": {"app": appname}},
            "spec": {
                "containers": [
                    {
                        "name": appname,
                        "image": f"bhanujggandhi/{appname}:latest",
                        "ports": [{"containerPort": 5000}],
                        "envFrom": [
                            {"configMapRef": {"name": f"{appname}-configmap"}},
                            {"secretRef": {"name": f"{appname}-secret"}},
                        ],
                    }
                ]
            },
        },
    },
}

with open("out.yaml", "r") as f:
    sched_yaml = yaml.safe_load(f)

print(sched_yaml)
print(schema)
# print(validate(sched_yaml, schema))
print(jsonschema.validate(json.dumps(sched_yaml), json.dumps(schema)))
