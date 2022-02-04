# start app
# uvicorn database_app.main:app --reload

from typing import List

from sqlalchemy.orm import Session
from starlette import status

from . import models, crud_utils, schemas
from .database import SessionLocal, engine
from fastapi import FastAPI, Depends, HTTPException

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db  # each request must have a new db session(connection) and close it after the request is finished
    finally:  # response has been sent, close the connection
        db.close()

# path operations are declared as synchronous functions

@app.post('/users/', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud_utils.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='email already registered'
        )
    return crud_utils.create_user(db=db, user=user)


@app.get('/users/', response_model=schemas.User)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud_utils.get_users(db, skip, limit)
    return users


@app.get('/uses/{user_id}', response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud_utils.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='user not found'
        )
    return db_user


@app.post('/users/{user_id}/items/', response_model=schemas.Item)
def create_item_for_user(
        user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud_utils.create_user_item(db, item, user_id)


@app.get('/items/', response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud_utils.get_items(db, skip, limit)
    return items # List of orm models will be passed to pydantic response model
