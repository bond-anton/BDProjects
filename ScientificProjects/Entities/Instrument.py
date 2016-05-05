from __future__ import division, print_function

from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.Project import Project
from ScientificProjects.Entities.User import User
from ScientificProjects.Entities.Parameter import Parameter

association_table = Table('experimental_setup_parameter', Base.metadata,
                          Column('setup_id', Integer, ForeignKey('experimental_setup.id')),
                          Column('parameter_id', Integer, ForeignKey('parameter.id')))


class ExperimentalSetup(Base):
    __tablename__ = 'experimental_setup'
    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey('instrument.id'))
    measurement_type_id = Column(Integer, ForeignKey('measurement_type.id'))
    registered = Column(DateTime, default=func.now())
    instrument = relationship("Instrument", back_populates="methods")
    measurement_type = relationship("MeasurementType", back_populates="instruments")


class Instrument(Base):

    __tablename__ = 'instrument'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    created = Column(DateTime, default=func.now())

    def __str__(self):
        return self.name
