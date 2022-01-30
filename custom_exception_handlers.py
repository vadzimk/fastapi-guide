from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

custom_exception_handler_app = FastAPI()

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name=name

@custom_exception_handler_app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=410,
        content={
            'message': f'oops {exc.name} did sometething wrong'
        }
    )


# RequestValidationError contains body it received with invalid data
# it can be used while developing your app to log thebody and debug it , return it to the user
@custom_exception_handler_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'detail': exc.errors(), 'body': exc.body})
    )


@custom_exception_handler_app.get('/unicorns/{name}')
async def read_unicorn(name:str):
    if name == 'yolo':
        raise UnicornException(name=name)
    return {'unicorn_name': name}
