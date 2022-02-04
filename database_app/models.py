# contains database orm models

from sqlalchemy.orm import relationship

from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # contains the name of the other table related to this one
    # user.items-> list[Item] that have a FK pointing to this user
    items = relationship('Item', back_populates='owner')

class Item(Base):
    __tablename__='items'
    id=Column(Integer, primary_key=True, index=True)
    title=Column(String, index=True)
    description=Column(String, index=True)
    owner_id=Column(Integer, ForeignKey('users.id'))

    owner= relationship('User', back_populates='items')