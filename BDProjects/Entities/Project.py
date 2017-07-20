from __future__ import division, print_function

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from BDProjects import Base, default_date_time_format
from BDProjects.Entities.Session import Session


class SessionProject(Base):

    __tablename__ = 'session_project'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship('Session', back_populates='projects_opened', cascade='all, delete')
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates='sessions', cascade='all, delete')
    opened = Column(DateTime, default=func.now())
    closed = Column(DateTime)


class Project(Base):

    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    created = Column(DateTime, default=func.now())
    created_session_id = Column(Integer, ForeignKey('session.id'))
    created_session = relationship(Session, backref=backref('projects_created', uselist=True,
                                                            cascade='all, delete-orphan'))
    data_dir = Column(String)
    sessions = relationship('SessionProject', back_populates='project', cascade='all, delete-orphan')

    def __str__(self):
        description = 'Project: %s' % self.name
        if self.description is not None:
            description += '\n %s' % self.description
        description += '\n Data dir: %s' % self.data_dir
        created = self.created.strftime(default_date_time_format)
        description += '\n Created: %s' % created
        description += '\n Created by: @%s' % self.created_session.user.login
        return description
