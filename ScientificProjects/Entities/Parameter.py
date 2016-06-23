from __future__ import division, print_function

from sqlalchemy import Column, DateTime, String, Text, Integer, BigInteger, Float, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
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
    children = relationship('Parameter')
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
