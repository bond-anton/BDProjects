from __future__ import division, print_function

from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.Session import Session
from ScientificProjects.Entities.Parameter import Parameter
from ScientificProjects.Entities.MeasurementType import MeasurementType


equipment_assembly_table = Table('assembly_parts', Base.metadata,
                                 Column('assembly_id', Integer, ForeignKey('equipment_assembly.id')),
                                 Column('equipment_id', Integer, ForeignKey('equipment.id')))

equipment_parameters_table = Table('equipment_parameters', Base.metadata,
                                   Column('equipment_id', Integer, ForeignKey('equipment.id')),
                                   Column('parameter_id', Integer, ForeignKey('parameter.id')))

equipment_measurement_table = Table('equipment_measurement', Base.metadata,
                                    Column('equipment_id', Integer, ForeignKey('equipment.id')),
                                    Column('measurement_type_id', Integer, ForeignKey('measurement_type.id')))


class Manufacturer(Base):

    __tablename__ = 'manufacturer'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    name_short = Column(String, unique=True)
    description = Column(Text)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('manufacturers', uselist=True, cascade='delete,all'))
    created = Column(DateTime, default=func.now())

    def __str__(self):
        return self.name


class EquipmentCategory(Base):

    __tablename__ = 'equipment_category'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('equipment_category.id'))
    subcategories = relationship('EquipmentCategory')
    name = Column(String, unique=True)
    description = Column(Text)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('equipment_categories', uselist=True, cascade='delete,all'))
    created = Column(DateTime, default=func.now())

    def __str__(self):
        return self.name


class Equipment(Base):

    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    manufacturer_id = Column(Integer, ForeignKey('manufacturer.id'))
    manufacturer = relationship('Manufacturer', backref=backref('equipment', uselist=True,
                                                                cascade='delete,all'))
    category_id = Column(Integer, ForeignKey('equipment_category.id'))
    category = relationship(EquipmentCategory, backref=backref('equipment', uselist=True,
                                                               cascade='delete,all'))
    assembly_id = Column(Integer, ForeignKey('equipment_assembly.id'))
    assembly = relationship('EquipmentAssembly', backref=backref('equipment', uselist=True,
                                                                 cascade='delete,all'))
    description = Column(Text)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('equipment', uselist=True, cascade='delete,all'))
    parameters = relationship(Parameter, secondary=equipment_parameters_table, backref="equipment")
    measurement_types = relationship(MeasurementType, secondary=equipment_measurement_table, backref="equipment")
    created = Column(DateTime, default=func.now())

    def __str__(self):
        return self.name


class EquipmentAssembly(Base):

    __tablename__ = 'equipment_assembly'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    parts = relationship(Equipment, secondary=equipment_assembly_table, backref="assemblies")
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('assemblies', uselist=True, cascade='delete,all'))
    created = Column(DateTime, default=func.now())

    def __str__(self):
        return self.name
