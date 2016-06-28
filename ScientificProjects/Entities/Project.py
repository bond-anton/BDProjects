from __future__ import division, print_function

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base, default_date_time_format
from ScientificProjects.Entities.Session import Session


class SessionProject(Base):

    __tablename__ = 'session_project'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('session.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    opened = Column(DateTime, default=func.now())
    closed = Column(DateTime)
    session = relationship('Session', back_populates='projects_opened', cascade='delete')
    project = relationship('Project', back_populates='sessions', cascade='delete')


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
        description = 'Project: %s' % self.name
        if self.description is not None:
            description += '\n %s' % self.description
        description += '\n Data dir: %s' % self.data_dir
        created = self.created.strftime(default_date_time_format)
        description += '\n Created: %s' % created
        description += '\n Created by: @%s' % self.created_session.user.login
        return description
