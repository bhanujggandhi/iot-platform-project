"""
This file is responsible for

- Signing of JWTs
- Encoding of JWTs
- Decoding of JWTs
- Returing of JWTs
"""


import time

import jwt
from decouple import config

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def token_response(token: str):
    return {"access_token": token}


def signJWT(payload: dict):
    payload["expiry"] = time.time() + 123456789
    # payload = {"id": userID, "role": role, "email": email, "expiry": time.time() + 123456789}

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decode_token if decode_token["expiry"] >= time.time() else None
    except:
        return {}
