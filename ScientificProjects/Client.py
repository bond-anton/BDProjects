from __future__ import division, print_function

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ScientificProjects import Base
from ScientificProjects.EntityManagers.VersionManager import VersionManager
from ScientificProjects.EntityManagers.LogManager import LogManager
from ScientificProjects.EntityManagers.UserManager import UserManager


class Client(object):

    def __init__(self, db_name='/:memory:', backend='sqlite',
                 hostname='', port='', user='', password=''):
        credentials = user + ':' + password if password else user
        if credentials:
            credentials += '@'
        if port:
            hostname += ':' + str(port)
        db_url = backend + '://' + credentials + hostname + '/' + db_name

        self.engine = create_engine(db_url)
        self.metadata = Base.metadata

        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()

        self.user = None
        self.session_data = None
        self.project = None

        self.log_manager = LogManager(self.engine, self)
        self.user_manager = UserManager(self.engine, self)
        self.version_manager = VersionManager(self.engine, self)
