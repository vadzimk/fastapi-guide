from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette import status

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

security_app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')  # tokenUrl is expecting username and password to send the token


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_hash_password(password: str):
    return 'fakehashed' + password


def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user


def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'},  # prart of spec, along with 401
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(
            status_code=400,
            detail='inactive user'
        )


@security_app.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)): # dependency that declares form body with username, password, scope, grant_type, client_id, client_secret
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=400,
            detail='invalid username or password'
        )
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(
            status_code=400,
            detail='invalid username or password'
        )
    return { # by the spec this is the required shape of the response
        'access_token': user.username,  # jwt token usually
        'token_type': 'bearer'
    }


@security_app.get('/users/me')
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@security_app.get('/items/')
async def read_items(token: str = Depends(
    oauth2_scheme)):  # will check for Authorization header for a Bearer token and respond with 401 Unauthorized if not found
    return {'token': token}
