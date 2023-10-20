"""
This file is responsible for

- check wheather the request is authorized or not (middleware)
"""

from utils.jwt_handler import decodeJWT
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(403, detail="Invalid or Expired Token")
            return credentials.credentials
        else:
            raise HTTPException(403, detail="Invalid or Expired Token")

    def verify_jwt(self, jwttoken: str):
        isTokenValid: bool = False
        payload = decodeJWT(jwttoken)
        if payload:
            isTokenValid = True

        return isTokenValid
