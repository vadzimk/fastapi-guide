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

from fastapi import FastAPI

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
@app.get('/files/{file_path:path}') # declare parameter of type path
async def read_file(file_path: str):
    return {'file_path': file_path}


