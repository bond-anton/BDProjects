from __future__ import division, print_function

from sqlalchemy import Column, DateTime, String, Text, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Projects import Project


class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project, backref=backref('teems', uselist=True, cascade='delete,all'))
    registered = Column(DateTime, default=func.now())
