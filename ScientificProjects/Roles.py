from __future__ import division, print_function

from sqlalchemy import Column, DateTime, String, Text, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from ScientificProjects import Base
from ScientificProjects.Users import User
from ScientificProjects.Teams import Team


class RoleType(Base):
    __tablename__ = 'role_type'
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    description = Column(Text)


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    role_type_id = Column(Integer, ForeignKey('role_type.id'))
    role_type = relationship(RoleType, backref=backref('roles', uselist=True, cascade='delete,all'))
    manager_id = Column(Integer, ForeignKey('role.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref=backref('user_roles', uselist=True, cascade='delete,all'))
    team_id = Column(Integer, ForeignKey('team.id'))
    team = relationship(Team, backref=backref('team_roles', uselist=True, cascade='delete,all'))
    created = Column(DateTime, default=func.now())
    accepted = Column(DateTime)
