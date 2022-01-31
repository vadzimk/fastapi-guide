from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer

security_app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token') # tokenUrl is expecting username and password to send the token

@security_app.get('/items/')
async def read_items(token: str=Depends(oauth2_scheme)):  # will check for Authorization header for a Bearer token and respond with 401 Unauthorized if not found
    return {'token': token}

