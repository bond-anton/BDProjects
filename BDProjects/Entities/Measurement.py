from __future__ import division, print_function

from sqlalchemy import Table, Column, UniqueConstraint, Integer, Float, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from BDProjects import Base, default_date_time_format
from BDProjects.Entities.MeasurementType import MeasurementType
from BDProjects.Entities.Equipment import Equipment
from BDProjects.Entities.Project import Project
from BDProjects.Entities.Session import Session
from BDProjects.Entities.Parameter import Parameter
from BDProjects.Entities.Sample import Sample


measurement_sample_table = Table('measurement_sample', Base.metadata,
                                 Column('id', Integer, primary_key=True),
                                 Column('measurement_id', Integer, ForeignKey('measurement.id')),
                                 Column('sample_id', Integer, ForeignKey('sample.id')),
                                 UniqueConstraint('measurement_id', 'sample_id', name='_measurement_sample'))

measurement_collection_table = Table('measurement_collection', Base.metadata,
                                     Column('id', Integer, primary_key=True),
                                     Column('collection_id', Integer,
                                            ForeignKey('measurements_collection.id')),
                                     Column('measurement_id', Integer,
                                            ForeignKey('measurement.id')),
                                     UniqueConstraint('collection_id', 'measurement_id',
                                                      name='_measurement_collection'))


measurement_parameter_table = Table('measurement_parameter', Base.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('measurement_id', Integer, ForeignKey('measurement.id')),
                                    Column('parameter_id', Integer, ForeignKey('parameter.id')),
                                    UniqueConstraint('measurement_id', 'parameter_id', name='_measurement_parameter'))


class MeasurementsCollection(Base):

    __tablename__ = 'measurements_collection'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project, backref=backref('measurements_collections', uselist=True,
                                                    cascade='all, delete-orphan'))
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('measurements_collections', uselist=True,
                                                    cascade='all, delete-orphan'))
    measurements = relationship('Measurement', secondary=measurement_collection_table,
                                backref='collections', cascade='all, delete')
    created = Column(DateTime, default=func.now())
    __table_args__ = (UniqueConstraint('name', 'project_id', name='_collection_project'),)


class Measurement(Base):

    __tablename__ = 'measurement'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    measurement_type_id = Column(Integer, ForeignKey('measurement_type.id'))
    measurement_type = relationship(MeasurementType, backref=backref('measurements', uselist=True,
                                                                     cascade='all, delete-orphan'))
    equipment_id = Column(Integer, ForeignKey('equipment.id'))
    equipment = relationship(Equipment, backref=backref('measurements', uselist=True,
                                                        cascade='all, delete-orphan'))
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project, backref=backref('measurements', uselist=True,
                                                    cascade='all, delete-orphan'))
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('measurements', uselist=True,
                                                    cascade='all, delete-orphan'))
    input_data_id = Column(Integer, ForeignKey('measurements_collection.id'))
    input_data = relationship(MeasurementsCollection, backref=backref('analyses', uselist=True,
                                                                      cascade='all, delete-orphan'))
    samples = relationship(Sample, secondary=measurement_sample_table, backref='measurements')
    parameters = relationship(Parameter, secondary=measurement_parameter_table, backref='measurements')
    description = Column(Text)
    started = Column(DateTime, default=func.now())
    finished = Column(DateTime)
    progress = Column(Float, default=0.0)

    def __str__(self):
        description = 'Measurement: %s' % self.name
        if self.description is not None:
            description += '\n %s' % self.description
        description += '\n Type: %s' % self.measurement_type.name
        description += '\n Equipment: %s' % self.equipment.name
        started = self.started.strftime(default_date_time_format)
        description += '\n Started: %s' % started
        if self.finished:
            finished = self.started.strftime(default_date_time_format)
            description += '\n Finished: %s' % finished
        description += '\n Samples number: %i' % len(self.samples)
        description += '\n Parameters number: %i' % len(self.parameters)
        description += '\n Data channels number: %i' % len(self.data_channels)
        if self.input_data:
            description += '\n Input data: %s' % self.input_data.name
        description += '\n Created by: @%s' % self.session.user.login
        return description
