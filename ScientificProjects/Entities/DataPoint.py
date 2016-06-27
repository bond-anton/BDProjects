from __future__ import division, print_function

from sqlalchemy import Table, Column, UniqueConstraint
from sqlalchemy import DateTime, String, Text, Integer, BigInteger, Float, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.Session import Session
from ScientificProjects.Entities.Measurement import Measurement
from ScientificProjects.Entities.Parameter import Parameter


channel_parameter_table = Table('channel_parameter', Base.metadata,
                                Column('channel_id', Integer, ForeignKey('data_channel.id')),
                                Column('parameter_id', Integer, ForeignKey('parameter.id')))


class DataChannel(Base):

    __tablename__ = 'data_channel'
    id = Column(Integer, primary_key=True)
    measurement_id = Column(Integer, ForeignKey('measurement.id'), nullable=False)
    measurement = relationship(Measurement, backref=backref('data_channels', uselist=True,
                                                            cascade='delete,all'))
    name = Column(String)
    description = Column(Text)
    unit_name = Column(String)
    parameters = relationship(Parameter, secondary=channel_parameter_table,
                              backref="data_channels")
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('data_channels', uselist=True,
                                                    cascade='delete,all'))
    __table_args__ = (UniqueConstraint('name', 'measurement_id', name='_measurement_channel'),)


class DataPoint(Base):

    __tablename__ = 'data_point'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('data_channel.id'))
    channel = relationship(DataChannel, backref=backref('data_points', uselist=True,
                                                        cascade='delete,all'))
    index = Column(BigInteger, nullable=False, default=0)
    string_value = Column(String)
    float_value = Column(Float)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('data_points', uselist=True,
                                                    cascade='delete,all'))
    value_measured = Column(DateTime, nullable=False)
    value_added = Column(DateTime, default=func.now())
    value_altered = Column(DateTime, default=func.now(), onupdate=func.now())
