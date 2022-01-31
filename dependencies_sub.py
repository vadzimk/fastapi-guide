from typing import Optional

from fastapi import FastAPI, Depends, Cookie

dependencies_sub_app = FastAPI()


# first dependency
def query_extractor(q: Optional[str] = None):
    return q


def query_or_cookie_extractor(
        q: str = Depends(query_extractor), # may use_cache=False to call it only once per request
        last_query: Optional[str] = Cookie(None)
):
    if not q:
        return last_query
    return q


@dependencies_sub_app.get('/items')
async def read_query(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {'q_or_cookie': query_or_default}
