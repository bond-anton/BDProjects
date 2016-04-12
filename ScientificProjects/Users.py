from __future__ import division, print_function

from sqlalchemy import Column, DateTime, String, Text, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name_first = Column(String)
    name_last = Column(String)
    registered = Column(DateTime, default=func.now())


class RoleType(Base):
    __tablename__ = 'role_type'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    role_description = Column(Text)



