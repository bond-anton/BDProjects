from __future__ import division, print_function

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ScientificProjects import Base
from ScientificProjects.EntityManagers.VersionManager import VersionManager
from ScientificProjects.EntityManagers.LogManager import LogManager
from ScientificProjects.EntityManagers.UserManager import UserManager
from ScientificProjects.EntityManagers.ProjectManager import ProjectManager


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
        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()
        self.metadata = Base.metadata
        self._create_tables(overwrite)
        self.session.close()

        self.log_manager = LogManager(self.engine, self)
        self.version_manager = VersionManager(self.engine, self)
        self.user_manager = UserManager(self.engine, self)
        self.project_manager = ProjectManager(self.engine, self)

    def _create_tables(self, overwrite=False):
        if overwrite:
            self.metadata.drop_all(self.engine)
        self.metadata.create_all(self.engine)
