from typing import Optional

from fastapi import FastAPI
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


@multi_model_app.post('/user',
                      response_model=UserOut,
                      # possible values:
                      # response_model=Union[MoreSpecificType, LessSpecificType]
                      # response_model=Dict[str,float]
                      )
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved
