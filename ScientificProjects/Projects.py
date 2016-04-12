from __future__ import division, print_function

from sqlalchemy import Column, DateTime, String, Text, Integer, ForeignKey, func

from ScientificProjects import Base


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    created = Column(DateTime, default=func.now())
    owner_id = Column(Integer, ForeignKey('user.id'))
