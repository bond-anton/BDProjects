from __future__ import division, print_function

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.Session import Session


class SessionProject(Base):

    __tablename__ = 'session_project'
    session_id = Column(Integer, ForeignKey('session.id'), primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'), primary_key=True)
    opened = Column(DateTime, default=func.now())
    closed = Column(DateTime)
    session = relationship('Session', back_populates='projects_opened')
    project = relationship('Project', back_populates='sessions')


class Project(Base):

    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    created = Column(DateTime, default=func.now())
    created_session_id = Column(Integer, ForeignKey('session.id'))
    created_session = relationship(Session, backref=backref('projects_created', uselist=True, cascade='delete,all'))
    data_dir = Column(String)
    sessions = relationship('SessionProject', back_populates='project')

    def __str__(self):
        return self.name
