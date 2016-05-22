from __future__ import division, print_function

from sqlalchemy import Column, DateTime, String, Text, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.Project import Project
from ScientificProjects.Entities.Session import Session


class LogCategory(Base):

    __tablename__ = 'log_category'
    id = Column(Integer, primary_key=True)
    category = Column(String, unique=True)
    description = Column(Text)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('log_categories', uselist=True, cascade='delete,all'))
    created = Column(DateTime, default=func.now())


class Log(Base):

    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    record = Column(String)
    category_id = Column(Integer, ForeignKey('log_category.id'))
    category = relationship(LogCategory, backref=backref('logs', uselist=True, cascade='delete,all'))
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('logs', uselist=True, cascade='delete,all'))
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project, backref=backref('logs', uselist=True, cascade='delete,all'))
    created = Column(DateTime, default=func.now())
