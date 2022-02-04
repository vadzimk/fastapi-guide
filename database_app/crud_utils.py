# contains reusable functions to interact with the data in the database
# by creating dedicated functions to interact with db you can add unit tests and reuse them

from . import models, schemas
from sqlalchemy.orm import Session


# Querying (1.x Style)
# https://docs.sqlalchemy.org/en/14/orm/session_basics.html#querying-1-x-style
# https://docs.sqlalchemy.org/en/14/orm/tutorial.html
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + 'notreallyhashed'
    db_user = models.User(
        email=user.email,
        hashed_password=fake_hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # refreshes the python object from db with select, it will populate the id on the object and any relationships
    return db_user


def get_items(db: Session, skip: int=0, limit: int=100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item=models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item