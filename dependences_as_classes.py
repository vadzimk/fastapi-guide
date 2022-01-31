from typing import Optional

from fastapi import FastAPI, Depends

dependencies_as_classes_app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# instead of a function that returns a dict we declare a class
class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@dependencies_as_classes_app.get('/items')
async def read_items(
        commons: CommonQueryParams = Depends(CommonQueryParams),
        # commons: CommonQueryParams = Depends() # shortcut same as above
):
    response = {}
    if commons.q:
        response.update({'q': commons.q})
    items = fake_items_db[commons.skip: commons.skip + commons.limit]  # make a slice
    response.update({'items': items})
    return response
