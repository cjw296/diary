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
    type = Column(ENUM(Types, name='types_enum'), nullable=False)
    text = Column(Text, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': Types.event,
        'polymorphic_on':type
    }


class Done(Event):
    __mapper_args__ = {
        'polymorphic_identity': Types.done,
    }


class Cancelled(Event):
    __mapper_args__ = {
        'polymorphic_identity': Types.cancelled,
    }


class Postponed(Event):
    __mapper_args__ = {
        'polymorphic_identity': Types.postponed,
    }
