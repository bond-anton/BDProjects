from __future__ import division, print_function

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from ScientificProjects import Base

from ScientificProjects.Users import User
from ScientificProjects.Projects import Project
from ScientificProjects.Teams import Team
from ScientificProjects.Roles import RoleType, Role


class ProjectsManager(object):
    def __init__(self, db_name='/:memory:', backend='sqlite',
                 hostname='', port='', user='', password='',
                 overwrite=False):
        # postgresql://scott:tiger@localhost:5432/mydatabase
        credentials = user + ':' + password if password else user
        if credentials:
            credentials += '@'
        if port:
            hostname += ':' + str(port)
        self.engine = create_engine(backend + '://' + credentials + hostname + '/' + db_name)
        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()
        self.metadata = Base.metadata
        self.create_tables(overwrite)
        self.user = None

    def create_tables(self, overwrite=False):
        if overwrite:
            self.metadata.drop_all(self.engine)
        self.metadata.create_all(self.engine)

    def add_user(self, name_first, name_last, email, login, password):
        user = User(name_first=str(name_first), name_last=str(name_last),
                    email=str(email), login=str(login), password=str(password))
        try:
            self.session.add(user)
            self.session.commit()
        except IntegrityError as e:
            print('User with provided login/email is already registered.')
            self.session.rollback()

    def sign_in(self, login, password):
        user = self.session.query(User).filter(User.login == str(login)).all()
        if user:
            user = user[0]
            if user.password == str(password):
                self.user = user
                print('Welcome back, %s %s' % (user.name_first, user.name_last))
            else:
                print('Incorrect username/password')
        else:
            print('Incorrect username/password')
