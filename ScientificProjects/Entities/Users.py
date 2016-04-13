from __future__ import division, print_function

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy_utils import PasswordType

from ScientificProjects import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name_first = Column(String)
    name_last = Column(String)
    email = Column(String, unique=True)
    login = Column(String, unique=True)
    password = Column(PasswordType(schemes=['pbkdf2_sha512', 'md5_crypt']))
    signed_in = Column(Boolean, default=False)
    registered = Column(DateTime, default=func.now())
