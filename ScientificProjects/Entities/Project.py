from __future__ import division, print_function

from sqlalchemy import Column, Integer, Boolean, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.Session import Session


class Project(Base):

    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    created = Column(DateTime, default=func.now())
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('projects', uselist=True, cascade='delete,all'))
    data_dir = Column(String)
    opened = Column(Boolean, default=False)

    def __str__(self):
        return self.name
