from enum import Enum
from typing import Optional

from fastapi import FastAPI, status
from pydantic import BaseModel, EmailStr

multi_model_app = FastAPI()


# will contain shared attributes
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserIn(UserBase):
    password: str


class UserOut(BaseModel):
    pass


class UserInDB(BaseModel):
    hashed_password: str


def fake_pass_hasher(raw_password: str):
    return 'supersecret' + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_pass_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(),
                          hashed_password=hashed_password)  # create a new pydantic model from the contents of another
    print('user saved')
    return user_in_db


class Tags(Enum):
    items = 'items'
    users = 'users'


@multi_model_app.post('/user',
                      response_model=UserOut,
                      # possible values:
                      # response_model=Union[MoreSpecificType, LessSpecificType]
                      # response_model=Dict[str,float]
                      status_code=status.HTTP_201_CREATED,  # or 201 number or import from starlette.status
                      tags=[Tags.users],  # you can add tags to OpenApi schema/documentation as a string or Enum
                      summary='Create a user',
                      description='Create a user with username, email, full_name',
                      # escription can be declared in the path operation as docstring and FastApi will read it from there
                      response_description='the created item', # is actually required
                      deprecated=True, # path operation can be marked as depricated in the documentation
                      )
async def create_user(user_in: UserIn):
    """
    Create a user with username, email, full_name
    can contain markdown
    """
    user_saved = fake_save_user(user_in)
    return user_saved
