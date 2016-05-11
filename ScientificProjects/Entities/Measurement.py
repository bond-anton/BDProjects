from __future__ import division, print_function

from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.MeasurementType import MeasurementType
from ScientificProjects.Entities.Equipment import Equipment
from ScientificProjects.Entities.Project import Project
from ScientificProjects.Entities.User import User
from ScientificProjects.Entities.Parameter import Parameter


measurement_collection_table = Table('measurement_collection', Base.metadata,
                                     Column('collection_id', Integer,
                                            ForeignKey('measurements_collection.id')),
                                     Column('measurement_id', Integer,
                                            ForeignKey('measurement.id')))


measurement_parameter_table = Table('measurement_parameter', Base.metadata,
                                    Column('measurement_id', Integer, ForeignKey('measurement.id')),
                                    Column('parameter_id', Integer, ForeignKey('parameter.id')))


class MeasurementsCollection(Base):

    __tablename__ = 'measurements_collection'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref=backref('measurements_collections', uselist=True,
                                              cascade='delete,all'))
    measurements = relationship(Measurement, secondary=measurement_collection_table,
                                backref="collections")
    created = Column(DateTime, default=func.now())


class Measurement(Base):

    __tablename__ = 'measurement'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    measurement_type_id = Column(Integer, ForeignKey('measurement_type.id'))
    measurement_type = relationship(MeasurementType, backref=backref('measurements', uselist=True,
                                                                     cascade='delete,all'))
    tool_id = Column(Integer, ForeignKey('equipment.id'))
    tool = relationship(Equipment, backref=backref('measurements', uselist=True,
                                                   cascade='delete,all'))
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project, backref=backref('measurements', uselist=True,
                                                    cascade='delete,all'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref=backref('measurements', uselist=True,
                                              cascade='delete,all'))
    input_data_id = Column(Integer, ForeignKey('measurements_collection.id'))
    input_data = relationship(MeasurementsCollection, backref=backref('measurements', uselist=True,
                                                                      cascade='delete,all'))
    parameters = relationship(Parameter, secondary=measurement_parameter_table,
                              backref="measurements")
    description = Column(Text)
    started = Column(DateTime, default=func.now())
    finished = Column(DateTime)

    def __str__(self):
        return self.name
