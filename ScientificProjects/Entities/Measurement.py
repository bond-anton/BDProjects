from __future__ import division, print_function

from sqlalchemy import Table, Column, Integer, Float, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.MeasurementType import MeasurementType
from ScientificProjects.Entities.Equipment import Equipment
from ScientificProjects.Entities.Project import Project
from ScientificProjects.Entities.Session import Session
from ScientificProjects.Entities.Parameter import Parameter
from ScientificProjects.Entities.Sample import Sample


measurement_sample_table = Table('measurement_sample', Base.metadata,
                                 Column('measurement_id', Integer, ForeignKey('measurement.id')),
                                 Column('sample_id', Integer, ForeignKey('sample.id')))

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
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('measurements_collections', uselist=True,
                                                    cascade='delete,all'))
    measurements = relationship('Measurement', secondary=measurement_collection_table,
                                backref="collections")
    created = Column(DateTime, default=func.now())


class Measurement(Base):

    __tablename__ = 'measurement'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    measurement_type_id = Column(Integer, ForeignKey('measurement_type.id'))
    measurement_type = relationship(MeasurementType, backref=backref('measurements', uselist=True,
                                                                     cascade='delete,all'))
    equipment_id = Column(Integer, ForeignKey('equipment.id'))
    equipment = relationship(Equipment, backref=backref('measurements', uselist=True,
                                                        cascade='delete,all'))
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project, backref=backref('measurements', uselist=True,
                                                    cascade='delete,all'))
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('measurements', uselist=True,
                                                    cascade='delete,all'))
    input_data_id = Column(Integer, ForeignKey('measurements_collection.id'))
    input_data = relationship(MeasurementsCollection, backref=backref('analyses', uselist=True,
                                                                      cascade='delete,all'))
    samples = relationship(Sample, secondary=measurement_sample_table, backref='measurements')
    parameters = relationship(Parameter, secondary=measurement_parameter_table,
                              backref='measurements')
    description = Column(Text)
    started = Column(DateTime, default=func.now())
    finished = Column(DateTime)
    progress = Column(Float, default=0.0)

    def __str__(self):
        return self.name
