from .model import UserLoginSchema


def check_user(data, user):
    if user["email"] == data["email"] and user["password"] == data["password"]:
        return True
    return False
