from __future__ import division, print_function

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Entities.Session import Session


class MeasurementType(Base):

    __tablename__ = 'measurement_type'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('measurement_type.id'))
    subtypes = relationship('MeasurementType', cascade='delete,all')
    name = Column(String, unique=True)
    description = Column(Text)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('measurement_types', uselist=True, cascade='delete,all'))
    created = Column(DateTime, default=func.now())

    def __str__(self):
        return self.name
