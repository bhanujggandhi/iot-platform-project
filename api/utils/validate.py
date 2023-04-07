from .model import UserLoginSchema


def check_user(data: UserLoginSchema, users: [UserLoginSchema]):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False
