from fastapi import FastAPI
from bson import ObjectId
from db_util import DataBase
import bcrypt
import re

app = FastAPI()
database = DataBase()
database.connect()
database.create_db("test_app_to_dev")


def user_schema(username, email, password):
    data = {
        "_id": ObjectId(),
        "username": username,
        "email": email,
        "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
    }
    return data


def dev_schema(dev_id, dev_email):
    data = {"_id": ObjectId(), "dev_id": dev_id, "dev_email": dev_email}
    return data


def app_schema(app_id, dev_id, app_name):
    data = {"_id": ObjectId(), "app_id": app_id, "dev_id": dev_id, "app_name": app_name}
    return data


@app.get("/")
def index():
    return {"message": "Welcome To FastAPI World"}


@app.post("/add_user/users/")
def add(username: str, email: str, password: str):
    database.use_collection("users")

    email_isvaild = re.search(r"[\w.]+\@[\w.]+", email)
    if not email_isvaild:
        return {"message": "Invalid Email"}

    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat = re.compile(reg)
    mat = re.search(pat, password)

    if not mat:
        return {"message": "Invalid Password"}

    database.model(user_schema(username, email, password))
    return database.add()


@app.post("/add_dev/dev/")
def add(dev_id: int, dev_email: str):
    database.use_collection("dev")
    database.model(dev_schema(dev_id, dev_email))
    return database.add()


@app.post("/add_app/app/")
def add(app_id: int, dev_id: int, app_name: str):
    database.use_collection("app")
    database.model(app_schema(app_id, dev_id, app_name))
    return database.add()


@app.post("/update/")
def update(collection: str, field: str, old_value: str, new_value: str):
    database.use_collection(collection)
    return database.update(field, old_value, new_value)


@app.post("/delete/")
def delete(collection: str, field: str, value: str):
    database.use_collection(collection)
    return database.delete(field, value)


@app.post("/read/")
def read(collection: str):
    database.use_collection(collection)
    return database.read()


@app.post("/join/")
def join(collection: str, fromCollection, localField, foreignField):
    database.use_collection(collection)
    return database.join(fromCollection, localField, foreignField)
