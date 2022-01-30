from typing import Optional, List

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

body_updates_app = FastAPI()


class Item(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: float = 10.5
    tags: List[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}

@body_updates_app.get('/items/{item_id}', response_model=Item)
async def read_item(item_id: str):
    return items[item_id]


# PUT is used to receive data that should replace existing data
# if if the key is not in the new data, it will be substituted by the default value in the pydantic model
@body_updates_app.put('/items/{item_id}', response_model=Item)
async def update_item(item_id: str, item: Item):
    update_item_encoded = jsonable_encoder(item) # returns a dict with json compatible data
    items[item_id] = update_item_encoded
    return update_item_encoded


# partial updates with PATCH (the operation type is just a convention)
# you can send only the data that you want to update, leaving the rest intact
# if you want to receive partial updates, use parameter exclude_unset in pydantic's mode's .dict()
@body_updates_app.patch('/items/{item_id}', response_model=Item)
async def update_item(item_id: str, item: Item): # you can make a separate update model with optional fields instead of required for creation
    stored_item_data = items[item_id] # retrieve the stored data
    stored_item_model = Item(**stored_item_data) # put stored data in model
    update_data = item.dict(exclude_unset=True) # generate dict without unset default values
    updated_item = stored_item_model.copy(update=update_data) # creates a copy of stored model and updates model
    items[item_id] = jsonable_encoder(updated_item) # converts model into dict compatible with json stores dict in the db which is a dict in the example
    return updated_item # returns updated model

