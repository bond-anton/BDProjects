from __future__ import division, print_function

from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from BDProjects import Base
from BDProjects.Entities.User import User


class Session(Base):

    __tablename__ = 'session'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref=backref('sessions', uselist=True, cascade='all, delete-orphan'))
    active = Column(Boolean, default=True)
    opened = Column(DateTime, default=func.now())
    closed = Column(DateTime, onupdate=func.now())
    host = Column(String)
    python = Column(String)
    platform = Column(String)
    token = Column(String)
    projects_opened = relationship('SessionProject', back_populates='session',
                                   cascade='all, delete-orphan')
