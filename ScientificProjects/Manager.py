from __future__ import division, print_function

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ScientificProjects import Base, default_log_categories, default_users, default_parameter_types
from ScientificProjects.EntityManagers.VersionManager import VersionManager
from ScientificProjects.EntityManagers.LogManager import LogManager
from ScientificProjects.EntityManagers.UserManager import UserManager
from ScientificProjects.Entities.User import User
from ScientificProjects.Entities.Session import Session
from ScientificProjects.Entities.Project import Project
from ScientificProjects.Entities.Sample import Sample
from ScientificProjects.Entities.Equipment import Equipment
from ScientificProjects.Entities.Measurement import Measurement
from ScientificProjects.Entities.DataPoint import DataPoint


class Installer(object):

    def __init__(self, db_name='/:memory:', backend='sqlite',
                 hostname='', port='', user='', password='',
                 overwrite=False):
        credentials = user + ':' + password if password else user
        if credentials:
            credentials += '@'
        if port:
            hostname += ':' + str(port)
        db_url = backend + '://' + credentials + hostname + '/' + db_name
        print(db_url)
        self.engine = create_engine(db_url)
        self.metadata = Base.metadata
        self._create_tables(overwrite)

        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()

        self.user = None
        self.project = None

        self.log_manager = LogManager(self.engine, self)
        self._create_default_log_categories()

        self.version_manager = VersionManager(self.engine, self)

        self.user_manager = UserManager(self.engine, self)
        self._create_default_users()
        self._create_default_parameter_types()

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
