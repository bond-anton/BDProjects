from __future__ import division, print_function

from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.User import User
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
    abbreviation = Column(String)
    description = Column(Text)
    created = Column(DateTime, default=func.now())


class EquipmentCategory(Base):

    __tablename__ = 'equipment_category'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('equipment_category.id'))
    subcategories = relationship('EquipmentCategory')
    name = Column(String, unique=True)
    description = Column(Text)
    created = Column(DateTime, default=func.now())


class Equipment(Base):

    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    manufacturer_id = Column(Integer, ForeignKey('manufacturer.id'))
    manufacturer = relationship('Manufacturer', backref=backref('equipment', uselist=True,
                                                                cascade='delete,all'))
    category_id = Column(Integer, ForeignKey('equipment_category.id'))
    category = relationship(EquipmentCategory, backref=backref('equipment', uselist=True,
                                                               cascade='delete,all'))
    assembly_id = Column(Integer, ForeignKey('equipment_assembly.id'))
    assembly = relationship('EquipmentAssembly', backref=backref('equipment', uselist=True,
                                                                 cascade='delete,all'))
    inventory_number = Column(String)
    serial_number = Column(String)
    version = Column(String)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref=backref('equipment', uselist=True, cascade='delete,all'))
    parameters = relationship(Parameter, secondary=equipment_parameters_table, backref="equipment")
    measurements = relationship(MeasurementType, secondary=equipment_measurement_table, backref="equipment")
    created = Column(DateTime, default=func.now())

    def __str__(self):
        return self.name


class EquipmentAssembly(Base):

    __tablename__ = 'equipment_assembly'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    parts = relationship(Equipment, secondary=equipment_assembly_table, backref="assemblies")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref=backref('assemblies', uselist=True, cascade='delete,all'))
    created = Column(DateTime, default=func.now())
