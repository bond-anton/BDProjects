from __future__ import division, print_function

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ArgumentError
from BDProjects import Base
from BDProjects.Config import read_config
from BDProjects.EntityManagers.VersionManager import VersionManager
from BDProjects.EntityManagers.LogManager import LogManager
from BDProjects.EntityManagers.UserManager import UserManager


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
        try:
            self.engine = create_engine(db_url)
        except ArgumentError:
            raise ValueError('Wrong DB URL')
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
