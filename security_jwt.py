# about jwt
# https://jwt.io/introduction
# jwt is a readable base64url encoded string
# header.payload.signature
# signatrure is created as algorithm(base64urlencode(header) + "." + base64urlencode(payload), secret)

# to get a sting run
# openssl rand -hex 32
from datetime import timedelta, datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel
from passlib.context import CryptContext
from starlette import status

SECRET_KEY = 'f9739e470ee4d039995f7b5fd7789816fdbbb3d93b1b3bbe3c7cac11c3df1f55'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


# pydontic model used in the token endpoint for response
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDb(User):
    hashed_password: str


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

security_jwt_app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDb(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# utility function to generate a new access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    """ decode token verify it and return current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='inactive user'
        )
    return current_user


### Send POST request with body as parameters
# POST http://127.0.0.1:8000/token
# Content-Type: application/x-www-form-urlencoded
#
# username=johndoe&password=secret
@security_jwt_app.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username},
        # sub is subject of the token to put users id or of any other resource like a car or blog post
        # example of payload:
        # {
        #   "sub": "1234567890",
        #   "name": "John Doe",
        #   "admin": true
        # }
        # to avoid id collisions you can prefix it, e.g: username:1234567890
        expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}

# ###
# GET http://127.0.0.1:8000/users/me/items
# Content-Type: application/json
# Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNjQzODgxMTI3fQ.491DIWEc7EvbHv_XWViHoU23o-TePU3nvZVnEOWunR4
@security_jwt_app.get('/users/me/items')
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{'item_id': 'Foo', 'owner': current_user.username}]
