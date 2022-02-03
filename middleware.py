import time
from fastapi import FastAPI
from starlette.requests import Request

middleware_app = FastAPI()


@middleware_app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-process-time'] = str(process_time)
    return response
