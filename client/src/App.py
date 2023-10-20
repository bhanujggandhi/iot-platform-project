from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
import jwt

# from decouple import config
from pymongo import MongoClient


# from pymongo import MongoClient
# from decoupler import config

app = Flask(__name__)
CORS(app)

# Define database connection and cursor
conn = sqlite3.connect("db.db")
cur = conn.cursor()

# Create users table if it doesn't exist
cur.execute(
    """CREATE TABLE IF NOT EXISTS users
               (id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL)"""
)
conn.commit()

# Create apps table if it doesn't exist
cur.execute(
    """CREATE TABLE IF NOT EXISTS apps
               (app_id TEXT PRIMARY KEY,
                app_name TEXT NOT NULL,
                modules TEXT,
                sensors TEXT)"""
)
conn.commit()

# Create user_apps table if it doesn't exist
cur.execute(
    """CREATE TABLE IF NOT EXISTS user_apps
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                app_id TEXT NOT NULL UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (app_id) REFERENCES apps(app_id))"""
)
conn.commit()

cur.close()
conn.close()


def get_db():
    db = sqlite3.connect("db.db")
    db.row_factory = sqlite3.Row
    return db.cursor(), db


# Route to handle user registration
@app.route("/register", methods=["POST"])
def register():
    email = request.json.get("email")
    password = request.json.get("password")
    # mongokey = config['mongoKey']
    # client = MongoClient(mongokey)
    # db = client('userDB')
    # collection = db.userCollection
    # collection.insert_one({})

    # Get a new cursor and connection for this request
    cur, conn = get_db()

    # Check if email is already registered
    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    if cur.fetchone() is not None:
        return jsonify({"message": "Email is already registered"}), 400

    # Add new user to database
    cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    conn.commit()

    # Close the cursor and connection
    cur.close()
    conn.close()

    return jsonify({"message": "User registered successfully"}), 200


# Route to handle user login
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    # print(email, password)

    # Get a new cursor and connection for this request
    cur, conn = get_db()

    # Retrieve the user with the given email
    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cur.fetchone()

    # Check if the user exists and the password matches
    if user is None or user["password"] != password:
        return jsonify({"message": "Invalid email or password"}), 401

    # Close the cursor and connection
    cur.close()
    conn.close()

    return jsonify({"message": "Login successful"}), 200


app_num = 0


# API route to add an app for a user
@app.route("/addapp", methods=["POST"])
def add_app():
    global app_num
    try:
        # Get input data from request body
        app_name = request.json["app_name"]
        user_id = request.json["user_id"]
        
        payload = {
            "user_id": user_id,
            "app_name": app_name,
           
        }

        secret_key = "iasbrew"
        app_token = jwt.encode(payload, secret_key, algorithm="HS256")

        # Connect to the database and execute the query
        cur, conn = get_db()

        # Insert app into apps table if it doesn't exist
        cur.execute(
            """SELECT * FROM user_apps
            INNER JOIN apps ON user_apps.app_id = apps.app_id
            WHERE user_apps.user_id = ? AND apps.app_name = ?""",
            (user_id, app_name),
        )
        if cur.fetchone() is None:
            app_id = user_id + app_name
            cur.execute(
                "INSERT INTO apps (app_id, app_name) VALUES (?, ?)",
                (app_id, app_name),
            )
            conn.commit()

            # Insert user_app entry into user_apps table
            cur.execute(
                "INSERT INTO user_apps (user_id, app_id) VALUES (?, ?)",
                (user_id, app_id),
            )
            conn.commit()

            # Close the database connection and return success message
            cur.close()
            conn.close()
            return (
                jsonify(
                    {
                        "message": "App added successfully",
                        "app_id": app_id,
                        "token": app_token,
                    }
                ),
                200,
            )

        return jsonify({"message": "App name is already registered"}), 400

    except sqlite3.Error as e:
        # Handle SQLite errors
        print("Error:", e)
        return jsonify({"message": "Database error occurred"}), 500

    except Exception as e:
        # Handle other exceptions
        print("Error:", e)
        return jsonify({"message": "Internal server error"}), 500


@app.route("/fetchapps")
def fetch_apps():
    # Get user ID from request parameters
    if "user_id" in request.args.keys():
        user_id = request.args.get("user_id")

        # Connect to the database and execute the query
        cur, conn = get_db()
        cur.execute(
            "SELECT apps.app_id, apps.app_name, apps.modules, apps.sensors FROM user_apps JOIN apps ON user_apps.app_id = apps.app_id WHERE user_apps.user_id = ?",
            (user_id,),
        )
        rows = cur.fetchall()

        # Build list of JSON objects from query results
        apps = []
        for row in rows:
            app = {
                "app_id": row[0],
                "app_name": row[1],
                "modules": row[2],
                "sensors": row[3],
            }
            apps.append(app)

        # Close the database connection and return JSON response
        cur.close()
        conn.close()
        return jsonify(apps)

    elif "app_id" in request.args.keys():
        user_id = request.args.get("app_id")

        # Connect to the database and execute the query
        cur, conn = get_db()
        cur.execute(
            "SELECT apps.app_id, apps.app_name, apps.modules, apps.sensors FROM apps WHERE apps.app_id = ?",
            (user_id,),
        )
        row = cur.fetchone()
        app = {}
        if row is not None:
            app = {
                "app_id": row[0],
                "app_name": row[1],
                "modules": row[2],
                "sensors": row[3],
            }
        cur.close()
        conn.close()
        return jsonify(app)

    return jsonify({"message": "Internal server error"}), 500


@app.route("/fetchsensors")
def fetch_sensors():
    MONGOKEY = "mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(MONGOKEY)
    db = client["SensorDB"]
    collection = db.SensorMetadata
    cursor = collection.find({}, {"_id": 0})
    documents = list(cursor)
    client.close()
    return jsonify(documents)


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
