from __future__ import division, print_function

from sqlalchemy import Column, Integer, String, Text, DateTime, func

from BDProjects import Base


class Role(Base):

    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    registered = Column(DateTime, default=func.now())
    altered = Column(DateTime, default=func.now(), onupdate=func.now())

    def __str__(self):
        description = 'Role $%s (%s)' % (self.name, self.description)
        return description
