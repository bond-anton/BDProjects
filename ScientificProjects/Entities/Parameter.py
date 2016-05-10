from __future__ import division, print_function

from sqlalchemy import Column, DateTime, String, Text, Integer, BigInteger, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base


class ParameterType(Base):

    __tablename__ = 'parameter_type'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    registered = Column(DateTime, default=func.now())


class Parameter(Base):

    __tablename__ = 'parameter'
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('parameter_type.id'))
    type = relationship(ParameterType, backref=backref('parameters', uselist=True, cascade='delete,all'))
    parent_id = Column(Integer, ForeignKey('parameter.id'))
    children = relationship('Parameter')
    name = Column(String, unique=True)
    description = Column(Text)
    unit_name = Column(String, unique=False)
    index = Column(BigInteger, nullable=False, default=0)
    string_value = Column(String)
    value_sign = Column(Integer, nullable=False)
    value_mantissa = Column(BigInteger, nullable=False)
    value_exponent = Column(Integer, nullable=False)
    value_bytecount = Column(Integer, nullable=False)
    value_measured = Column(DateTime, nullable=False)
    value_added = Column(DateTime, default=func.now())
    value_altered = Column(DateTime, default=func.now(), onupdate=func.now())
