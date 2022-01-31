from fastapi import FastAPI, Header, HTTPException, Depends

dependencies_path_decorators = FastAPI()


# when you don't need the return value of the dependency inside the path operation function but you still need it executed
# you can add a list of dependencies to the path operation decorator

async def verify_token(x_token: str = Header(...)):
    if x_token != 'fake-super-secret-token':
        raise HTTPException(status_code=400, detail='X-Token header invalid')


async def verify_key(x_key: str = Header(...)):
    if x_key != 'fake-super-secret-key':
        raise HTTPException(status_code=400, detail='X-Key header invalid')
    return x_key


@dependencies_path_decorators.get(
    '/items/',
    dependencies=[Depends(verify_token), Depends(verify_key)] # return values will not be used
)
async def read_items():
    return [{'item': 'foo'}, {'item': 'bar'}]
