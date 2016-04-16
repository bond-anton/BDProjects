from __future__ import division, print_function

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ScientificProjects import Base
from ScientificProjects.EntityManagers.VersionManager import VersionManager
from ScientificProjects.EntityManagers.LogManager import LogManager
from ScientificProjects.EntityManagers.UserManager import UserManager
from ScientificProjects.Entities.User import User


class SessionManager(object):

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
        self.metadata = Base.metadata
        self._create_tables(overwrite)

        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()

        self.user = User(name_first='Bot', name_last='Bot', login='bot')
        self.project = None

        self.log_manager = LogManager(self.engine, self)
        self.version_manager = VersionManager(self.engine, self)
        self.user_manager = UserManager(self.engine, self)

    def _create_tables(self, overwrite=False):
        if overwrite:
            self.metadata.drop_all(self.engine)
        self.metadata.create_all(self.engine)

    def signed_in_users(self):
        return self.session.query(User).filter(User.signed_in == 1).all()

    def logoff_all(self):
        for user in self.signed_in_users():
            user.signed_in = False
            self.session.commit()
            self.log_manager.log_record(record='@%s was logged off' % user.login,
                                        category='Information')
