from __future__ import division, print_function

from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.Project import Project
from ScientificProjects.Entities.User import User
from ScientificProjects.Entities.Parameter import Parameter


association_table = Table('sample_parameter', Base.metadata,
                          Column('sample_id', Integer, ForeignKey('sample.id')),
                          Column('parameter_id', Integer, ForeignKey('parameter.id')))


class Sample(Base):

    __tablename__ = 'sample'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    created = Column(DateTime, default=func.now())
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship(User, backref=backref('samples', uselist=True, cascade='delete,all'))
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project, backref=backref('samples', uselist=True, cascade='delete,all'))
    parameters = relationship(Parameter, secondary=association_table, backref="samples")

    def __str__(self):
        return self.name
