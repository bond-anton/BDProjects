from __future__ import division, print_function
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ScientificProjects import Base
from ScientificProjects.EntityManagers.VersionManager import VersionManager
from ScientificProjects.EntityManagers.LogManager import LogManager
from ScientificProjects.EntityManagers.UserManager import UserManager
from ScientificProjects.Entities.User import User
from ScientificProjects.Entities.Project import Project


class SessionManager(object):

    def __init__(self, db_name='/:memory:', backend='sqlite',
                 hostname='', port='', user='', password='',
                 overwrite=False):
        credentials = user + ':' + password if password else user
        if credentials:
            credentials += '@'
        if port:
            hostname += ':' + str(port)
        self.engine = create_engine(backend + '://' + credentials + hostname + '/' + db_name)
        self.metadata = Base.metadata
        self._create_tables(overwrite)

        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()

        self.user = None
        self.project = None

        self.log_manager = LogManager(self.engine, self)
        self.version_manager = VersionManager(self.engine, self)
        self.user_manager = UserManager(self.engine, self)
        self.user = self.session.query(User).filter(User.login == 'bot').all()[0]

    def _create_tables(self, overwrite=False):
        if overwrite:
            self.metadata.drop_all(self.engine)
        self.metadata.create_all(self.engine)

    def signed_in_users(self):
        return self.session.query(User).filter(User.signed_in == 1).all()

    def log_signed_in_users(self):
        self.log_manager.log_record(record='Listing signed in users',
                                    category='Information')
        for user in self.signed_in_users():
            signed_in_for = (datetime.datetime.utcnow() - user.last_sign_in)
            las_login_string = user.last_sign_in.strftime("%Y-%m-%d %H:%M:%S")
            self.log_manager.log_record(record='@%s is signed in for %s (since %s)' % (user.login,
                                                                                       signed_in_for,
                                                                                       las_login_string),
                                        category='Information')

    def logoff_all(self):
        self.log_manager.log_record(record='Kick-off ALL signed in users',
                                    category='Warning')
        self.close_all_projects()
        for user in self.signed_in_users():
            user.signed_in = False
            user.last_sign_out = datetime.datetime.utcnow()
            self.session.commit()
            self.log_manager.log_record(record='@%s was logged off' % user.login,
                                        category='Warning')

    def opened_projects(self):
        return self.session.query(Project).filter(Project.opened == 1).all()

    def close_all_projects(self):
        for project in self.opened_projects():
            project.opened = False
            self.session.commit()
            self.log_manager.log_record(record='Project %s was closed' % project.name,
                                        category='Information')
