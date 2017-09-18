from __future__ import division, print_function

from sqlalchemy import Table, Column, ForeignKey, UniqueConstraint, Integer, String, DateTime, func
from sqlalchemy_utils import PasswordType
from sqlalchemy.orm import relationship

from BDProjects import Base
from BDProjects.Entities import Role


user_role_table = Table('user_role', Base.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('user_id', Integer, ForeignKey('user.id')),
                        Column('role_id', Integer, ForeignKey('role.id')),
                        UniqueConstraint('user_id', 'role_id', name='_user_role'))


class User(Base):

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name_first = Column(String)
    name_last = Column(String)
    email = Column(String, unique=True)
    login = Column(String, unique=True)
    password = Column(PasswordType(schemes=['pbkdf2_sha512', 'md5_crypt']))
    registered = Column(DateTime, default=func.now())
    altered = Column(DateTime, default=func.now(), onupdate=func.now())
    roles = relationship(Role, secondary=user_role_table, backref='users')

    def __str__(self):
        description = '@%s (%s %s) <%s>' % (self.login, self.name_first.title(), self.name_last.upper(), self.email)
        return description
