from __future__ import division, print_function

from sqlalchemy import Column, Integer, Boolean, String, DateTime, func
from sqlalchemy_utils import PasswordType

from BDProjects import Base


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

    def __str__(self):
        description = '@%s (%s %s) <%s>' % (self.login, self.name_first.title(), self.name_last.upper(), self.email)
        return description
