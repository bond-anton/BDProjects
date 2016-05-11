from __future__ import division, print_function

from sqlalchemy import Table, Column, DateTime, String, Text, Integer, BigInteger, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.Measurement import Measurement
from ScientificProjects.Entities.Parameter import Parameter


channel_parameter_table = Table('channel_parameter', Base.metadata,
                                Column('channel_id', Integer, ForeignKey('data_channel.id')),
                                Column('parameter_id', Integer, ForeignKey('parameter.id')))


class DataChannel(Base):

    __tablename__ = 'data_channel'
    id = Column(Integer, primary_key=True)
    measurement_id = Column(Integer, ForeignKey('measurement.id'))
    measurement = relationship(Measurement, backref=backref('data_channels', uselist=True,
                                                            cascade='delete,all'))
    name = Column(String, unique=True)
    description = Column(Text)
    unit_name = Column(String, unique=False)
    parameters = relationship(Parameter, secondary=channel_parameter_table,
                              backref="data_channels")


class DataPoint(Base):

    __tablename__ = 'data_point'
    channel_id = Column(Integer, ForeignKey('data_channel.id'))
    channel = relationship(DataChannel, backref=backref('data_points', uselist=True,
                                                        cascade='delete,all'))
    index = Column(BigInteger, nullable=False, default=0)
    string_value = Column(String)
    value_sign = Column(Integer, nullable=False)
    value_mantissa = Column(BigInteger, nullable=False)
    value_exponent = Column(Integer, nullable=False)
    value_bytecount = Column(Integer, nullable=False)
    value_measured = Column(DateTime, nullable=False)
    value_added = Column(DateTime, default=func.now())
    value_altered = Column(DateTime, default=func.now(), onupdate=func.now())
