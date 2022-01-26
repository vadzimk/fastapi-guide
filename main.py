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
from typing import Optional, List, Set, Dict

from fastapi import FastAPI, Query, Path, Body, Cookie, Header
from pydantic import BaseModel, Field, HttpUrl

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


@app.get('/items/')
async def read_items(q: Optional[str] = Query(
    ...,  # ... indicates that the query parameter is required as opposed to None which means optional
    min_length=3,  # Query provides validators
    max_length=50,
    regex="^fixedquery$",
    title='Query string',  # metadata for swagger documentation
    description='Query string for the item s to search in the db',
    alias='item-query'  # can be used in place of a key
)):
    results = {'items': [{'item_id': 'Foo'}, {'item_id': 'Bar'}]}
    if q:
        results.update({'q': q})
    return results


# query parameter can take multiple values
# http://localhost:8000/items/?q=foo&q=bar
# @app.get('/items/')
# async def read_items(q: Optional[List[str]] = Query(
#     ...)):  # need to explicitly use Query otherwise it will be interpreted as a request body
#     query_items = {'q': q}
#     return query_items

# @app.get('/items/')
# async def read_items(ads_id: Optional[str] = Cookie(None)):
#     """ Query, Path, Cookie are subclass from Param, the import is for a function that returns the corresponding class"""
#     return {'ads_id': ads_id}

@app.get('/items/')
async def read_items(
        user_agent: Optional[str] = Header(None),  # Header will convert header key from hyphenated to underscored
        x_token: Optional[List[str]]=Header(None) # to declare that a header has multiple values and can be accessed with a list
        # X-Token: foo
        # X-Token: bar
):

    return {'user-agent': user_agent}

@app.get('/items/{item_id}')
async def read_item(item_id: str, q: Optional[
    str] = None):  # query parameter q is optional, when default is not specified it becomes required
    if q:
        return {"item_id": item_id, 'q': q}
    return {'item_id': item_id}


# path parameters and validators can be declared in the Path() default value
@app.get('/items/{item_id}')
async def read_items(
        item_id: int = Path(..., title='The id of th item to get'),  # is always required and declared with ... object
        q: Optional[str] = Query(None, alias="item-query")
):
    results = {'item_id': item_id}
    if q:
        results.update({'q': q})
    return results

# pydantic models can be nested - i.e type can be another model
class Image(BaseModel):
    url: HttpUrl # will be validated as url and documented
    name: str

@app.post('/images/multiple')
async def create_multiple_images(images: List[Image]):
    return images

## to send data in request.body use operations POST, DELETE, PATCH
# to declare a request.body use Pydantic models
# to declare additional validation and metadata use pydantic.Field
class Item(BaseModel):
    name: str = Field(..., example='Foo')  # required, can pass extra argumens for documentation e.g example
    description: Optional[str] = Field(None, title='The description of the item', max_length=300)
    price: float = Field(..., gt=0, description='The price must be >0')
    tax: Optional[float] = None,
    tags: Set[str]=set() # will remove duplicates from request
    images: Optional[List[Image]] = None

    # inside model can declare examples of request body
    # it will be automatically added to api docs
    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }

# This would mean that FastAPI would expect a body similar to:
#
# {
#     "name": "Foo",
#     "description": "The pretender",
#     "price": 42.0,
#     "tax": 3.2,
#     "tags": ["rock", "metal", "bar"],
#     "images": [{
#         "url": "http://example.com/baz.jpg",
#         "name": "The Foo live"
#     }]
# }

@app.post('/items/')
async def create_item(item: Item):  # request.body variable
    item_dict = item.dict()
    if item.tax:
        price_w_tax = item.price + item.tax
        item_dict.update({'pirce_with_tax': price_w_tax})
    return item_dict


## request.body and path parameters
@app.put('/items1/{item_id}')
async def update_item(
        item_id: int,  # recognizes path parameter by name
        item: Item,  # Pydantic model is recognized as the request.body
        q: Optional[str] = None  # if parameter is a primitive type it is interpreted as query parameter
):
    result = {'item_id': item_id, **item.dict()}  # can merge two dicts z={**x, **y}
    if q:
        result.update({"q": q})
    return result


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


# multiple body parameters
@app.put('/items2/{item_id}')
async def update_item(
        item_id: int,
        item: Item,
        user: User,
        importance: int = Body(...)
        # singular value will be interpreted as a query parameter if not defaulted to Body(...) object
):
    results = {'item_id': item_id, 'item': item, 'user': user}
    return results


# with more than one body parameters in the function FastAPI will use parameter names as keys in the body and expect body like
# {
#     "item": {
#         "name": "Foo",
#         "description": "The pretender",
#         "price": 42.0,
#         "tax": 3.2
#     },
#     "user": {
#         "username": "dave",
#         "full_name": "Dave Grohl"
#     },
#      "importance": 5
# }

# Embed a single body parameter
# by default a body parameter is interpreted as a whole but with
# item: Body(..., embed=True) it will expect a json with a key item
# and extract just it
@app.put('/items3/{item_id}')
async def update_item(
        item_id: int,
        item: Item = Body(..., embed=True)
):
    results = {'item_id': item_id, 'item': item}
    return results

# In this case FastAPI will expect a body like:
#
# {
#     ...
#     "item": {
#         "name": "Foo",
#         "description": "The pretender",
#         "price": 42.0,
#         "tax": 3.2
#     }
# }

# Bodies of arbitrary dicts
@app.post('/index-weights/')
async def create_index_weights(
        weights: Dict[int, float] # bc it is not a primitive type, interpreted as body
):
    return weights

