from __future__ import division, print_function

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ScientificProjects import Base
from ScientificProjects.Config import read_config
from ScientificProjects.EntityManagers.VersionManager import VersionManager
from ScientificProjects.EntityManagers.LogManager import LogManager, default_log_categories
from ScientificProjects.EntityManagers.UserManager import UserManager, default_users
from ScientificProjects.EntityManagers.ParameterManager import default_parameter_types
from ScientificProjects.Entities.User import User
from ScientificProjects.Entities.Session import Session
from ScientificProjects.Entities.Project import Project
from ScientificProjects.Entities.Sample import Sample
from ScientificProjects.Entities.Equipment import Equipment
from ScientificProjects.Entities.Measurement import Measurement
from ScientificProjects.Entities.DataPoint import DataPoint


class Installer(object):

    def __init__(self, config=None, config_file_name=None,
                 overwrite=False):
        if config is None:
            config = read_config(config_file_name)
        credentials = config['user'] + ':' + config['password'] if config['password'] else config['user']
        if credentials:
            credentials += '@'
        hostname = config['host']
        if config['port']:
            hostname += ':' + str(config['port'])
        db_url = config['backend'] + '://' + credentials + hostname + '/' + config['db_name']

        self.engine = create_engine(db_url)
        self.metadata = Base.metadata
        self._create_tables(overwrite)

        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()

        self.user = None
        self.session_data = None
        self.project = None

        self.log_manager = LogManager(self.engine, self)
        self._create_default_log_categories()

        self.user_manager = UserManager(self.engine, self)
        self._create_default_users()
        self._create_default_parameter_types()

        self.version_manager = VersionManager(self.engine, self)

    def _create_tables(self, overwrite=False):
        print('Creating tables')
        if overwrite:
            print('  deleting old tables')
            self.metadata.drop_all(self.engine)
        self.metadata.create_all(self.engine)
        print(' new tables created.')

    def _create_default_log_categories(self):
        print('adding default log categories')
        for category in default_log_categories:
            print('  category: %s' % category)
            self.log_manager.create_log_category(category, default_log_categories[category])

    def _create_default_users(self):
        print('adding default system users')
        for user_data in default_users:
            user = default_users[user_data]
            print('  user: @%s' % user[3])
            self.user_manager.create_user(user[0], user[1], user[2], user[3], user[4])

        bot_username = default_users['bot'][3]
        self.user = self.session.query(User).filter(User.login == bot_username).one()
        self.user_manager.user = self.user

    def _create_default_parameter_types(self):
        print('adding default parameter types')
        for parameter_type in default_parameter_types:
            print('  parameter type: %s' % parameter_type)
            self.user_manager.parameter_manager.create_parameter_type(parameter_type,
                                                                      default_parameter_types[parameter_type])
