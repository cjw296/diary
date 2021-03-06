from enum import Enum

from sqlalchemy import Column, Integer, Text, Date
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker()


class Types(Enum):
    event = 'EVENT'
    done = 'DONE'
    cancelled = 'CANCELLED'
    postponed = 'POSTPONED'


class Event(Base):

    __tablename__ = 'entry'

    id = Column(Integer(), primary_key=True)
    date = Column(Date, nullable=False)
    type = Column(ENUM(Types, name='types_enum'), nullable=False, default=Types.event)
    text = Column(Text, nullable=False)
