from typing import Optional

from fastapi import FastAPI, Depends

dependencies_guide_app = FastAPI()


# dependency is a function that can take all the same parameters that a path operation function can take
async def common_parameters(
        q: Optional[str] = None, # optional query parameters
        skip: int = 0,
        limit: int = 100):
    return {'q': q, 'skip': skip, 'limit': limit}


@dependencies_guide_app.get('/items/')
async def read_items(commons: dict = Depends(common_parameters)):
    return commons


@dependencies_guide_app.get('/users/')
async def read_users(
        commons: dict = Depends(common_parameters) # Depends takes a single parameter, the dependency callable or function
):
    return commons
