from __future__ import division, print_function

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from ScientificProjects import Base


class MeasurementType(Base):

    __tablename__ = 'measurement_type'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('measurement_type.id'))
    subtypes = relationship('MeasurementType')
    name = Column(String, unique=True)
    description = Column(Text)
    created = Column(DateTime, default=func.now())

    def __str__(self):
        return self.name
