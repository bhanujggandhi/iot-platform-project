from typing import List

from bson import ObjectId


# Define App model
class App:
    def __init__(self, name: str, ip: str, port: int, users: List[ObjectId]):
        self.name = name
        self.ip = ip
        self.port = port
        self.users = users

    def to_dict(self):
        return {
            "name": self.name,
            "ip": self.ip,
            "port": self.port,
            "users": self.users,
        }
