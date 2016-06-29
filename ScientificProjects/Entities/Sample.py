from __future__ import division, print_function

from sqlalchemy import Table, Column, UniqueConstraint, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base, default_date_time_format
from ScientificProjects.Entities.Project import Project
from ScientificProjects.Entities.Session import Session
from ScientificProjects.Entities.Parameter import Parameter


association_table = Table('sample_parameter', Base.metadata,
                          Column('id', Integer, primary_key=True),
                          Column('sample_id', Integer, ForeignKey('sample.id')),
                          Column('parameter_id', Integer, ForeignKey('parameter.id')),
                          UniqueConstraint('sample_id', 'parameter_id', name='_sample_parameter'))


class Sample(Base):

    __tablename__ = 'sample'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    created = Column(DateTime, default=func.now())
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project, backref=backref('samples', uselist=True, cascade='all, delete-orphan'))
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('samples', uselist=True, cascade='all, delete-orphan'))
    parameters = relationship(Parameter, secondary=association_table, backref='samples')
    __table_args__ = (UniqueConstraint('name', 'project_id', name='_name_project'),)

    def __str__(self):
        description = 'Sample: %s' % self.name
        if self.description is not None:
            description += '\n %s' % self.description
        if self.project is not None:
            description += '\n Project: %s' % self.project.name
        else:
            description += '\n Project: %s' % self.project
        description += '\n Parameters number: %i' % len(self.parameters)
        created = self.created.strftime(default_date_time_format)
        description += '\n Created: %s' % created
        description += '\n Created by: @%s' % self.session.user.login
        return description
