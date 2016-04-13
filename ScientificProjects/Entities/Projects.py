from __future__ import division, print_function

from sqlalchemy import Column, DateTime, String, Text, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.Users import User


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    created = Column(DateTime, default=func.now())
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship(User, backref=backref('projects', uselist=True, cascade='delete,all'))
    data_dir = Column(String)
