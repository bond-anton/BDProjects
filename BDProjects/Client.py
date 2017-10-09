from __future__ import division, print_function

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as orm_Session
from sqlalchemy.exc import ArgumentError
from sqlalchemy.exc import IntegrityError

from passlib.apps import custom_app_context as pwd_context
from passlib import pwd

from BDProjects import Base
from BDProjects.Config import read_config
from BDProjects.Entities import Role, User, LogCategory, ParameterType, Session, Project
from BDProjects.EntityManagers import VersionManager
from BDProjects.EntityManagers import LogManager
from BDProjects.EntityManagers import UserManager
from BDProjects.EntityManagers import default_log_categories, default_parameter_types, system_users, default_roles


class Connector(object):

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
            self.__engine = create_engine(db_url)
        except ArgumentError:
            raise ValueError('Wrong DB URL')

        self.__metadata = Base.metadata

        self.__session = sessionmaker()
        self.__session.configure(bind=self.engine)

    @property
    def engine(self):
        return self.__engine

    @property
    def metadata(self):
        return self.__metadata

    @property
    def session(self):
        return self.__session


class Installer(object):

    def __init__(self, connector, administrator_password='admin', administrator_email=None, overwrite=False):
        self.__connector = connector

        self._create_tables(overwrite)

        self.__session = None
        self.session = self.connector.session()

        self._create_default_log_categories()
        self._create_default_roles()
        self._create_default_users()
        self._create_administrator(password=administrator_password, email=administrator_email)

        bot_username = system_users['bot']['login']
        self.user = self.session.query(User).filter(User.login == bot_username).one()
        self.session_data = None
        self.project = None

        self.log_manager = LogManager(self)
        self.user_manager = UserManager(self)
        self.user_manager.sign_in('administrator', administrator_password)
        self.version_manager = VersionManager(self)

        self._create_default_parameter_types()

        self.user_manager.sign_out()

    @property
    def connector(self):
        return self.__connector

    @property
    def engine(self):
        return self.connector.engine

    @property
    def session(self):
        return self.__session

    @session.setter
    def session(self, session):
        if isinstance(session, orm_Session) or session is None:
            self.__session = session

    def signed_in(self):
        return self.user_manager.signed_in()

    def check_if_user_is_administrator(self):
        return self.user_manager.check_if_user_is_administrator()

    def _create_tables(self, overwrite=False):
        print('Creating tables')
        if overwrite:
            print('  deleting old tables')
            self.connector.metadata.drop_all(self.connector.engine)
        self.connector.metadata.create_all(self.connector.engine)
        print(' new tables created.')

    def _create_default_log_categories(self):
        print('adding default log categories')
        for category in default_log_categories:
            print('  category: %s' % category)
            try:
                log_category = LogCategory(category=category, description=None)
                self.session.add(log_category)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()

    def _create_default_roles(self):
        print('adding default user roles')
        for role_data in default_roles:
            print('  role: $%s' % role_data['name'])
            role = Role(name=str(role_data['name']), description=str(role_data['description']))
            try:
                self.session.add(role)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()

    def _create_administrator(self, password='admin', email=None):
        admin_login = 'administrator'
        roles = self.session.query(Role).filter(Role.name == 'administrator').all()
        roles += self.session.query(Role).filter(Role.name == 'user').all()
        print('creating admin user')
        if email is None:
            email = 'admin@bdprojects'
        print('  user: @%s' % admin_login)
        password_hash = pwd_context.encrypt(password)
        user = User(name_first='Storage', name_last='Administrator', email=email,
                    login=admin_login, password_hash=password_hash, roles=roles)
        try:
            self.session.add(user)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

    def _create_default_users(self):
        print('adding default system users')
        roles = self.session.query(Role).filter(Role.name == 'system').all()
        for user_data in system_users:
            user_fields = system_users[user_data]
            print('  user: @%s' % user_fields['login'])
            if user_fields['password'] is None:
                user_fields['password'] = pwd.genword()
            password_hash = pwd_context.encrypt(user_fields['password'])
            user = User(name_first=str(user_fields['first']), name_last=str(user_fields['last']),
                        email=str(user_fields['email']), login=user_fields['login'], password_hash=password_hash,
                        roles=roles)
            try:
                self.session.add(user)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()

    def _create_default_parameter_types(self):
        print('adding default parameter types')
        for parameter_type in default_parameter_types:
            print('  parameter type: %s' % parameter_type)
            parameter_type_object = ParameterType(name=parameter_type,
                                                  description=default_parameter_types[parameter_type])
            try:
                self.session.add(parameter_type_object)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()


class Client(object):

    def __init__(self, connector):
        self.__connector = connector

        self.__session = None
        self.session = self.connector.session()

        self.__session_data = None
        self.__user = None
        self.__project = None

        bot_username = system_users['bot']['login']
        self.user = self.session.query(User).filter(User.login == bot_username).one()
        self.session_data = None
        self.project = None

        self.log_manager = LogManager(self)
        self.user_manager = UserManager(self)
        self.version_manager = VersionManager(self)

    @property
    def connector(self):
        return self.__connector

    @property
    def engine(self):
        return self.connector.engine

    @property
    def session(self):
        return self.__session

    @session.setter
    def session(self, session):
        if isinstance(session, orm_Session) or session is None:
            self.__session = session

    @property
    def session_data(self):
        return self.__session_data

    @session_data.setter
    def session_data(self, session):
        if isinstance(session, Session) or session is None:
            self.__session_data = session
        else:
            raise ValueError('Can not set session data')

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, user):
        if isinstance(user, User) or user is None:
            self.__user = user
        else:
            raise ValueError('Can not set user')

    @property
    def project(self):
        return self.__project

    @project.setter
    def project(self, project):
        if isinstance(project, Project) or project is None:
            self.__project = project
        else:
            raise ValueError('Can not set project')

    def signed_in(self):
        return self.user_manager.signed_in()

    def check_if_user_is_administrator(self):
        return self.user_manager.check_if_user_is_administrator()
