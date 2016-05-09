from __future__ import division, print_function

from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.Project import Project
from ScientificProjects.Entities.User import User
from ScientificProjects.Entities.Parameter import Parameter


association_table = Table('assembly_parts', Base.metadata,
                          Column('assembly_id', Integer, ForeignKey('equipment_assembly.id')),
                          Column('equipment_id', Integer, ForeignKey('equipment.id')))

equipment_parameters_table = Table('equipment_parameters', Base.metadata,
                                   Column('equipment_id', Integer, ForeignKey('equipment.id')),
                                   Column('parameter_id', Integer, ForeignKey('parameter.id')))


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
    category_id = Column(Integer, ForeignKey('equipment_category.id'))
    category = relationship(EquipmentCategory, backref=backref('equipment', uselist=True,
                                                               cascade='delete,all'))
    assembly_id = Column(Integer, ForeignKey('equipment_assembly.id'))
    assembly = relationship('EquipmentAssembly', backref=backref('equipment', uselist=True,
                                                               cascade='delete,all'))
    description = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref=backref('equipment', uselist=True, cascade='delete,all'))
    parameters = relationship(Parameter, secondary=equipment_parameters_table, backref="equipment")
    created = Column(DateTime, default=func.now())

    def __str__(self):
        return self.name


class EquipmentAssembly(Base):

    __tablename__ = 'equipment_assembly'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    parts = relationship(Equipment, secondary=association_table, backref="assemblies")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref=backref('assemblies', uselist=True, cascade='delete,all'))
    created = Column(DateTime, default=func.now())
