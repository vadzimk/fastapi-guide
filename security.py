from typing import Optional

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

security_app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')  # tokenUrl is expecting username and password to send the token


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

def fake_decode_token(token):
    return User(
        username=token+'fakedecoded', email='foo@example.com', full_name='Foo Bar'
    )

def get_current_user(token: str=Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    return user

@security_app.get('/users/me')
async def read_users_me(current_user: User=Depends(get_current_user)):
    return current_user

@security_app.get('/items/')
async def read_items(token: str = Depends(
    oauth2_scheme)):  # will check for Authorization header for a Bearer token and respond with 401 Unauthorized if not found
    return {'token': token}
