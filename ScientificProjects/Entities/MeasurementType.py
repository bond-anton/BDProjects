from __future__ import division, print_function

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base, default_date_time_format
from ScientificProjects.Entities.Session import Session


class MeasurementType(Base):

    __tablename__ = 'measurement_type'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('measurement_type.id'))
    subtypes = relationship('MeasurementType', cascade='delete,all', backref=backref('parent', remote_side=[id]))
    name = Column(String, unique=True)
    description = Column(Text)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('measurement_types', uselist=True, cascade='delete,all'))
    created = Column(DateTime, default=func.now())

    def __str__(self):
        description = 'Measurement type: %s' % self.name
        if self.description is not None:
            description += '\n %s' % self.description
        if self.parent is not None:
            description += '\n Parent: %s' % self.parent.name
        else:
            description += '\n Parent: %s' % self.parent
        description += '\n Subtypes number: %i' % len(self.subtypes)
        created = self.created.strftime(default_date_time_format)
        description += '\n Created: %s' % created
        description += '\n Created by: @%s' % self.session.user.login
        return description
