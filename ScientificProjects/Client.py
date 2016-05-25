from __future__ import division, print_function

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ScientificProjects import Base
from ScientificProjects.Config import read_config
from ScientificProjects.EntityManagers.VersionManager import VersionManager
from ScientificProjects.EntityManagers.LogManager import LogManager
from ScientificProjects.EntityManagers.UserManager import UserManager


class Client(object):

    def __init__(self, config=None, config_file_name=None):
        if config is None:
            config = read_config(config_file_name)
        credentials = config['user'] + ':' + config['password'] if config['password'] else config['user']
        if credentials:
            credentials += '@'
        hostname = config['host']
        if config['port']:
            hostname += ':' + str(config['port'])
        db_url = config['backend'] + '://' + credentials + hostname + '/' + config['db_name']
        print(db_url)

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
