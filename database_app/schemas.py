# contains pydantic models for validation and shape of requests and responses
from typing import Optional, List

from pydantic import BaseModel


# contain common attributes
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


# before creating an item we don't know what will be the id assigned to it
class ItemCreate(ItemBase):
    pass


# when reading item from db the id will be assigned to it
class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True # tells Pydantic model to read the data even if it is not a dict, but ORM model. this way it becomes compatible with orm and can be declared as response_model of a path operation. Pydantic will also try to access the data from orm attributes making lazy loading store it in the object


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str

# reading user from db does not have password in the model
class User(UserBase):
    id: int
    is_active: bool
    items: List[Item] = []

    class Config:
        orm_mode = True
