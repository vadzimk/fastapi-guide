# start the app
# uvicorn main:app --reload
# main is file main.py
# app object of FastAPI class
# --reload is hot reload only for development

# documentation
# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/openapi.json
# http://127.0.0.1:8000/redoc

# FastAPI is a subclass of https://www.starlette.io/
# based on async lib https://anyio.readthedocs.io/

# data validation by https://pydantic-docs.helpmanual.io/
from enum import Enum, unique  # https://docs.python.org/3/library/enum.html
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get('/')  # operation(endpoint)
async def root():
    return {'message': 'hello world'}  # auto converted to json


@app.get('/items/{item_id}')  # path parameter is passed to decorated function
async def read_item(item_id: int):  # auto converted to the specified type int - auto request parsing
    return {'item_id': item_id}


# path operations are performed in order
@app.get('/users/me')
async def read_user_me():
    return {'user_id': 'the current user'}


@app.get('/users/{user_id}')  # will catch the second item as a parameter
async def read_user(user_id: str):
    return {'user_id': user_id}


# Predefined values inherit from Enum class and possibly str
@unique
class ModelName(str, Enum):
    alexnet = 'alexnet'
    resnet = 'resnet'
    lenet = 'lenet'


@app.get('/models/{model_name}')
async def get_model(model_name: ModelName):
    # compare enum and enum
    if model_name == ModelName.alexnet:
        return {'model_name': model_name, "message": 'Deep learning'}

    # compare enum values
    if model_name.value == 'lenet':
        return {'model_name': model_name, 'message': 'LeCNN all the images'}

    # when retuning enum members they are auto converted to enum values
    return {'model_name': model_name, 'message': 'have some residuals'}


# path parameter can be /home/myfile.txt
# the url will look as /files//home/myfile.txt
@app.get('/files/{file_path:path}')  # declare parameter of type path
async def read_file(file_path: str):
    return {'file_path': file_path}


#  when you declare other function parameters that are not part of path parameters, they are interpreted as query parameters
fake_items_db = [{'item_name': 'foo'}, {'item_name': 'bar'}, {'item_name': 'baz'}]


# query is a set of key=value
# http://127.0.0.1:8000/items/?skip=0&limit=10
@app.get('/items/')
async def read_item(skip: int = 0, limit: int = 10):  # skip, limit are query parameters
    return fake_items_db[skip:(skip + limit)]


@app.get('/items/{item_id}')
async def read_item(item_id: str, q: Optional[
    str] = None):  # query parameter q is optional, when default is not specified it becomes required
    if q:
        return {"item_id": item_id, 'q': q}
    return {'item_id': item_id}


## to send data in request.body use operations POST, DELETE, PATCH
# to declare a request.body use Pydantic models

class Item(BaseModel):
    name: str # required
    description: Optional[str] = None # optional identified if there is default value but not the Optional type
    price: float
    tax: Optional[float] = None


@app.post('/items')
async def create_item(item: Item): # request.body variable
    item_dict = item.dict()
    if item.tax:
        price_w_tax = item.price+item.tax
        item_dict.update({'pirce_with_tax': price_w_tax})
    return item_dict

## request.body and path parameters
@app.put('/items/{item_id}')
async def update_item(item_id: int, item: Item, q:Optional[str]=None ): # recognizes path parameter by name
    # Pydantic model is recognized as the request.body
    # if parameter is a primitive type it is interpreted as query parameter
    result = {'item_id': item_id, **item.dict()} # can merge two dicts z={**x, **y}
    if q:
        result.update({"q": q})
    return result
