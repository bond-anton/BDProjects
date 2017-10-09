from __future__ import division, print_function
import sys
import datetime
import socket
import uuid

from sqlalchemy import exists, func
from sqlalchemy.exc import IntegrityError
from passlib.apps import custom_app_context as pwd_context

from BDProjects import default_date_time_format
from BDProjects.Entities import Role, User, Session

from .EntityManager import EntityManager
from BDProjects.EntityManagers import LogManager, ParameterManager, ProjectManager
from BDProjects.EntityManagers import EquipmentManager, MeasurementTypeManager, MeasurementManager, SampleManager
from ._helpers import require_signed_in, require_administrator, require_not_system_user

system_users = {
    'bot': {
        'first': None,
        'last': None,
        'email': 'bot@bdprojects',
        'login': 'bot',
        'password': None
    }
}

default_roles = [
    {'name': 'administrator',
     'description': 'BDProjects admin'},
    {'name': 'system',
     'description': 'BDProjects system users'},
    {'name': 'user',
     'description': 'BDProjects user'}
]


class UserManager(EntityManager):

    def __init__(self, session_manager):
        super(UserManager, self).__init__(session_manager)
        self.session_data = self._generate_session_data()
        self.user = self.session_manager.user
        self.log_manager = self.session_manager.log_manager
        self.project_manager = ProjectManager(self)
        self.measurement_type_manager = MeasurementTypeManager(self)
        self.parameter_manager = ParameterManager(self)
        self.equipment_manager = EquipmentManager(self)
        self.sample_manager = SampleManager(self)
        self.measurement_manager = MeasurementManager(self)

    @require_administrator
    @require_not_system_user
    def create_user(self, login, password, email, name_first=None, name_last=None, roles=None, active=True):
        user_roles = []
        if roles is None:
            roles = ['user']
        for role_name in roles:
            user_roles += self.session.query(Role).filter(Role.name == role_name).all()
        password_hash = pwd_context.encrypt(password)
        user = User(name_first=name_first, name_last=name_last,
                    email=email, login=login, password_hash=password_hash, roles=user_roles, active=active)
        try:
            self.session.add(user)
            self.session.commit()
            record = 'User @%s successfully created by @%s' % (user.login, self.user.login)
            self.log_manager.log_record(record=record, category='Information')
            return user
        except IntegrityError:
            self.session.rollback()
            record = 'User @%s already exists' % user.login
            self.log_manager.log_record(record=record, category='Warning')
            return self.session.query(User).filter(User.login == str(login)).one()

    @require_signed_in
    @require_not_system_user
    def delete_user(self, user):
        if isinstance(user, User):
            if user.login == self.user.login or self.check_if_user_is_administrator():
                if user not in self.session:
                    record = 'User @%s not found in database' % user.login
                    self.log_manager.log_record(record=record, category='Information')
                    return False
                opened_sessions = self.opened_sessions(user)
                if opened_sessions:
                    self.logoff_user(user)
                self.session.delete(user)
                self.session.commit()
                record = 'User @%s successfully deleted by @%s' % (user.login, self.user.login)
                self.log_manager.log_record(record=record, category='Information')
                return True
            else:
                record = 'Attempt to delete user @%s by @%s failed, no rights' % (user.login, self.user.login)
                self.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Wrong argument given to delete user'
            self.log_manager.log_record(record=record, category='Warning')
            return False

    @require_signed_in
    @require_not_system_user
    def delete_session_data(self, user, session_data):
        if isinstance(user, User) and isinstance(session_data, Session):
            check_user = user.login == self.user.login or self.check_if_user_is_administrator()
            check_session = user.login == session_data.user.login
            if check_user and check_session:
                self.close_session(session_data)
                self.session.delete(session_data)
                self.session.commit()
                record = 'Session #%s(@%s) successfully deleted by @%s' % (session_data.token, session_data.user.login,
                                                                           self.user.login)
                self.log_manager.log_record(record=record, category='Information')
                return True
            else:
                record = 'Wrong argument given to delete session'
                self.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Wrong argument given to delete session'
            self.log_manager.log_record(record=record, category='Warning')
            return False

    @require_not_system_user
    def sign_in(self, login, password):
        if self.signed_in():
            record = 'You are already signed in. Please sign out first'
            self.log_manager.log_record(record=record, category='Warning')
            return False
        user = self.session.query(User).filter(User.login == str(login)).all()
        email = self.session.query(User).filter(User.email == str(login)).all()
        if user:
            user = user[0]
        elif email:
            user = email[0]
        else:
            record = 'Login failed. Username: @%s' % str(login)
            self.log_manager.log_record(record=record, category='Warning')
            return False
        if pwd_context.verify(password, user.password_hash):
            self.user = user
            self.session_data = self._generate_session_data()
            self.session.add(self.session_data)
            self.session.commit()
            self.log_manager = LogManager(self)
            record = '@%s signed in (#%s)' % (self.user.login, self.session_data.token)
            self.log_manager.log_record(record=record, category='Information')
            self.project_manager.session_data = self.session_data
            self.project_manager.user = self.user
            return True
        else:
            record = 'Login failed. Username: @%s' % str(login)
            self.log_manager.log_record(record=record, category='Warning')
            return False


    @require_signed_in
    def sign_out(self):
        record = '@%s (#%s) is going to sign out' % (self.user.login, self.session_data.token)
        self.log_manager.log_record(record=record, category='Information')
        self.close_session(session=self.session_data)
        record = '@%s (#%s) signed out' % (self.user.login, self.session_data.token)
        self.log_manager.log_record(record=record, category='Information')
        self.user = self.session_manager.user
        self.session_data = None
        self.project_manager.user = self.user
        self.project_manager.session_data = self.session_data
        self.log_manager = self.session_manager.log_manager

    def signed_in(self):
        if isinstance(self.session_data, Session):
            sessions = self.session.query(Session).filter(Session.token == self.session_data.token,
                                                          Session.active == 1).all()
            if sessions:
                return True
            else:
                self.user = self.session_manager.user
                self.session_data = None
                self.log_manager = self.session_manager.log_manager
                return False
        return False

    @require_signed_in
    def check_if_user_is_administrator(self):
        for role in self.user.roles:
            if role.name == 'administrator':
                return True
        return False

    @require_signed_in
    def count_opened_sessions(self, user=None):
        if isinstance(user, User):
            if user.login == self.user.login or self.check_if_user_is_administrator():
                return self.session.query(Session).filter(Session.active == 1, Session.user_id == user.id).count()
            else:
                record = 'Attempt to count opened sessions for @%s by @%s' % (user.login, self.user.login)
                self.log_manager.log_record(record=record, category='Warning')
                return None
        elif user is None and self.check_if_user_is_administrator():
            return self.session.query(Session).filter(Session.active == 1).order_by(Session.user_id).count()
        else:
            record = 'Attempt to count opened sessions by @%s' % self.user.login
            self.log_manager.log_record(record=record, category='Warning')
            return None

    @require_signed_in
    def opened_sessions(self, user=None):
        if isinstance(user, User):
            if user.login == self.user.login or self.check_if_user_is_administrator():
                return self.session.query(Session).filter(Session.active == 1, Session.user_id == user.id).all()
            else:
                record = 'Attempt to get opened sessions info for @%s by @%s' % (user.login, self.user.login)
                self.log_manager.log_record(record=record, category='Warning')
                return None
        elif user is None and self.check_if_user_is_administrator():
            return self.session.query(Session).filter(Session.active == 1).order_by(Session.user_id).all()
        else:
            record = 'Attempt to get opened sessions by @%s' % self.user.login
            self.log_manager.log_record(record=record, category='Warning')
            return None

    @require_signed_in
    def log_opened_sessions(self, user=None):
        opened_sessions = self.opened_sessions(user=user)
        if opened_sessions:
            user_text = ''
            if isinstance(user, User):
                user_text = ' for @%s' % user.login
            record = 'Listing opened sessions' + user_text
            self.log_manager.log_record(record=record, category='Information')
            for opened_session in opened_sessions:
                signed_in_for = (datetime.datetime.now() - opened_session.opened)
                opened = opened_session.opened.strftime(default_date_time_format)
                record = '#%s (@%s) is opened for %s (since %s)' % (opened_session.token,
                                                                    opened_session.user.login,
                                                                    signed_in_for,
                                                                    opened)
                self.log_manager.log_record(record=record, category='Information')

    @require_administrator
    def signed_in_users(self):
        return self.session.query(User).join(Session).filter(Session.active == 1).all()

    @require_administrator
    def log_signed_in_users(self, log_sessions=False):
        record = 'Listing signed in users'
        self.log_manager.log_record(record=record, category='Information')
        for user in self.signed_in_users():
            self.log_user_info(user, log_sessions=log_sessions)

    @require_signed_in
    @require_not_system_user
    def log_user_info(self, user, log_sessions=False):
        if isinstance(user, User):
            if user.login == self.user.login or self.check_if_user_is_administrator():
                opened_sessions = self.count_opened_sessions(user)
                if opened_sessions > 0:
                    since = self.session.query(func.min(Session.opened)).filter(Session.user_id == user.id,
                                                                                Session.active == 1).one()[0]
                    since = since.strftime(default_date_time_format)
                    record = '@%s has %d opened sessions since %s' % (user.login,
                                                                      opened_sessions,
                                                                      since)
                    self.log_manager.log_record(record=record, category='Information')
                    if log_sessions:
                        self.log_opened_sessions(user)
                else:
                    last_log_off = self.session.query(
                        func.max(Session.closed)).filter(Session.user_id == user.id).one()[0]
                    if last_log_off is None:
                        record = '@%s never logged in' % user.login
                    else:
                        last_log_off = last_log_off.strftime(default_date_time_format)
                        record = '@%s id offline since %s' % (user.login, last_log_off)
                    self.log_manager.log_record(record=record, category='Information')
                return True
        return False

    @require_signed_in
    def close_session(self, session):
        if isinstance(session, Session):
            if session.user.login == self.user.login or self.check_if_user_is_administrator():
                if session.active:
                    self.project_manager.close_project(session=session)
                    session.active = False
                    self.session.commit()
                    record = 'Session #%s (@%s) closed' % (session.token, session.user.login)
                    self.log_manager.log_record(record=record, category='Information')
                    return True
            else:
                record = 'Attempt to close session #%s (@%s) by @%s' % (session.token, session.user.login,
                                                                        self.user.login)
                self.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to close session failed. Wrong argument'
            self.log_manager.log_record(record=record, category='Warning')
            return False

    @require_signed_in
    @require_not_system_user
    def logoff_user(self, user):
        if isinstance(user, User):
            if self.user.login == user.login:
                record = 'Closing all opened sessions of @%s' % user.login
            elif self.check_if_user_is_administrator():
                record = 'Kicking off @%s' % user.login
            else:
                record = 'Attempt to log off @%s by @%s failed, no rights' % (user.login, self.user.login)
                self.log_manager.log_record(record=record, category='Warning')
                return False
            self.log_manager.log_record(record=record, category='Warning')
            opened_sessions = self.count_opened_sessions(user)
            for session in self.opened_sessions(user):
                self.close_session(session)
            record = '@%s was logged off (closed %d sessions)' % (user.login, opened_sessions)
            self.log_manager.log_record(record=record, category='Warning')
            return True

    @require_administrator
    def logoff_users(self, users):
        if isinstance(users, (list, tuple)):
            for user in users:
                self.logoff_user(user)

    @require_administrator
    def logoff_all(self):
        record = 'Kick-off ALL signed in users'
        self.log_manager.log_record(record=record, category='Warning')
        self.logoff_users(self.signed_in_users())

    def _generate_session_data(self):
        if isinstance(self.user, User):
            session_data = Session(user_id=self.user.id)
            session_data.host = socket.gethostname()
            session_data.python = sys.version
            session_data.platform = sys.platform
            session_data.active = True
            token = str(uuid.uuid4())
            while self.session.query(exists().where(Session.token == token)).scalar():
                token = str(uuid.uuid4())
            session_data.token = token
        else:
            session_data = None
        return session_data
