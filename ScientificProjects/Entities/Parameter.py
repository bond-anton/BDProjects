from __future__ import division, print_function

from sqlalchemy import Column, DateTime, String, Text, Integer, BigInteger, Float, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base, default_date_time_format
from ScientificProjects.Entities.Session import Session


class ParameterType(Base):

    __tablename__ = 'parameter_type'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    registered = Column(DateTime, default=func.now())
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('parameter_types', uselist=True, cascade='delete,all'))

    def __str__(self):
        return self.name


class Parameter(Base):

    __tablename__ = 'parameter'
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('parameter_type.id'))
    type = relationship(ParameterType, backref=backref('parameters', uselist=True, cascade='delete,all'))
    parent_id = Column(Integer, ForeignKey('parameter.id'))
    children = relationship('Parameter', backref=backref('parent', remote_side=[id]))
    name = Column(String)
    description = Column(Text)
    unit_name = Column(String, unique=False)
    index = Column(BigInteger, nullable=False, default=0)
    string_value = Column(String)
    float_value = Column(Float)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('parameters', uselist=True, cascade='delete,all'))
    value_added = Column(DateTime, default=func.now())
    value_altered = Column(DateTime, default=func.now(), onupdate=func.now())

    def __str__(self):
        description = 'Parameter: %s' % self.name
        if self.description is not None:
            description += '\n %s' % self.description
        description += '\n Type: %s' % self.type.name
        description += '\n Numeric val: %s' % str(self.float_value)
        description += '\n String val: %s' % str(self.string_value)
        created = self.value_added.strftime(default_date_time_format)
        altered = self.value_altered.strftime(default_date_time_format)
        description += '\n Created: %s' % created
        description += '\n Altered: %s' % altered
        description += '\n Created by: @%s' % self.session.user.login
        description += '\n Parent: %s' % self.parent
        description += '\n Children number: %i' % len(self.children)
        return description
