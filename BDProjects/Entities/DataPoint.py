from __future__ import division, print_function

from sqlalchemy import Table, Column, UniqueConstraint
from sqlalchemy import DateTime, String, Text, Integer, Float, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from BDProjects import Base
from BDProjects.Entities.Session import Session
from BDProjects.Entities.Measurement import Measurement
from BDProjects.Entities.Parameter import Parameter


channel_parameter_table = Table('channel_parameter', Base.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('channel_id', Integer, ForeignKey('data_channel.id')),
                                Column('parameter_id', Integer, ForeignKey('parameter.id')),
                                UniqueConstraint('channel_id', 'parameter_id', name='_channel_parameter'))


class DataChannel(Base):

    __tablename__ = 'data_channel'
    id = Column(Integer, primary_key=True)
    measurement_id = Column(Integer, ForeignKey('measurement.id'), nullable=False)
    measurement = relationship(Measurement, backref=backref('data_channels', uselist=True,
                                                            cascade='all, delete-orphan'))
    name = Column(String)
    description = Column(Text)
    unit_name = Column(String)
    parameters = relationship(Parameter, secondary=channel_parameter_table,
                              backref='data_channels')
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('data_channels', uselist=True,
                                                    cascade='all, delete-orphan'))
    __table_args__ = (UniqueConstraint('name', 'measurement_id', name='_measurement_channel'),)


class DataPoint(Base):

    __tablename__ = 'data_point'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('data_channel.id'))
    channel = relationship(DataChannel, backref=backref('data_points', uselist=True,
                                                        cascade='all, delete-orphan'))
    point_index = Column(Integer, default=0)
    float_value = Column(Float)
    string_value = Column(String)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('data_points', uselist=True,
                                                    cascade='all, delete-orphan'))
    measured = Column(DateTime, default=func.now())
    added = Column(DateTime, default=func.now())
    altered = Column(DateTime, default=func.now(), onupdate=func.now())
