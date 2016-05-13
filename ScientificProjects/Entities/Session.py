from __future__ import division, print_function

from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.User import User


class Session(Base):

    __tablename__ = 'session'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref=backref('parameter_types', uselist=True, cascade='delete,all'))
    active = Column(Boolean, default=True)
    opened = Column(DateTime, default=func.now())
    closed = Column(DateTime, onupdate=func.now())
    host = Column(String)
    python = Column(String)
    hash = Column(String)
