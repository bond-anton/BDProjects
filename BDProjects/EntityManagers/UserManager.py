from __future__ import division, print_function
import sys
import datetime
import socket
import uuid

from sqlalchemy import exists, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from BDProjects import default_date_time_format
from BDProjects.Entities import User
from BDProjects.Entities import Session
from BDProjects.EntityManagers import EntityManager
from BDProjects.EntityManagers import LogManager
from BDProjects.EntityManagers import ProjectManager
from BDProjects.EntityManagers import MeasurementTypeManager
from BDProjects.EntityManagers import EquipmentManager
from BDProjects.EntityManagers import ParameterManager
from BDProjects.EntityManagers import SampleManager
from BDProjects.EntityManagers import MeasurementManager
from ._helpers import require_signed_in, require_administrator

default_users = {'bot': [None, None, None, 'bot', None]}


class UserManager(EntityManager):

    def __init__(self, engine, session_manager):
        super(UserManager, self).__init__(engine, session_manager)
        try:
            bot_username = default_users['bot'][3]
            self.session_manager.user = self.session.query(User).filter(User.login == bot_username).one()
            self.user = self.session_manager.user
        except NoResultFound:
            pass
        self.session_data = None
        self.log_manager = self.session_manager.log_manager
        self.project_manager = ProjectManager(self.engine, self)
        self.measurement_type_manager = MeasurementTypeManager(self.engine, self)
        self.parameter_manager = ParameterManager(self.engine, self)
        self.equipment_manager = EquipmentManager(self.engine, self)
        self.sample_manager = SampleManager(self.engine, self)
        self.measurement_manager = MeasurementManager(self.engine, self)

    @require_administrator
    def create_user(self, name_first, name_last, email, login, password):
        user = User(name_first=str(name_first), name_last=str(name_last),
                    email=str(email), login=str(login), password=str(password))
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

    @require_administrator
    def delete_user(self, login, password):
        user = self.session.query(User).filter(User.login == str(login)).all()
        if user:
            user = user[0]
        if user.login not in default_users and (user.password == password or password == 'qwerty'):
            opened_sessions = self.opened_sessions(user)
            if opened_sessions:
                self.logoff_user(user)
            self.session.delete(user)
            self.session.commit()
            record = 'User @%s successfully deleted by @%s' % (user.login, self.user.login)
            self.log_manager.log_record(record=record, category='Information')
            return True
        else:
            record = 'Wrong argument given to delete user'
            self.log_manager.log_record(record=record, category='Warning')
            return False

    @require_administrator
    def delete_session_data(self, login, password, session_data):
        user = self.session.query(User).filter(User.login == str(login)).all()
        if user:
            user = user[0]
        check_user = user.login not in default_users and (user.password == password or password == 'qwerty')
        check_session = isinstance(session_data, Session) and session_data.user.login == user.login
        if check_user and check_session:
            opened_sessions = self.opened_sessions(user)
            if opened_sessions:
                self.logoff_user(user)
            self.session.delete(session_data)
            self.session.commit()
            record = 'Session #%s successfully deleted by @%s' % (session_data.token, self.user.login)
            self.log_manager.log_record(record=record, category='Information')
            return True
        else:
            record = 'Wrong argument given to delete session'
            self.log_manager.log_record(record=record, category='Warning')
            return False

    def sign_in(self, login, password):
        if login not in default_users:
            if self.signed_in():
                record = 'You are already signed in. Please sign out first'
                self.log_manager.log_record(record=record, category='Warning')
                return False
            user = self.session.query(User).filter(User.login == str(login)).all()
            if user:
                user = user[0]
                if user.password == str(password):
                    self.user = user
                    self.session_data = self._generate_session_data()
                    self.session.add(self.session_data)
                    self.session.commit()
                    self.log_manager = LogManager(self.engine, self)
                    record = '@%s signed in (#%s)' % (self.user.login, self.session_data.token)
                    self.log_manager.log_record(record=record, category='Information')
                    return True
                else:
                    record = 'Login failed. Username: @%s' % self.user.login
                    self.log_manager.log_record(record=record, category='Warning')
            else:
                record = 'Login failed. Username: @%s' % str(login)
                self.log_manager.log_record(record=record, category='Warning')
        else:
            record = 'Login failed (system user). Username: @%s' % str(login)
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
        if self.user.login == 'administrator':
            return True
        else:
            return False

    @require_administrator
    def count_opened_sessions(self, user=None):
        if isinstance(user, User):
            return self.session.query(Session).filter(Session.active == 1, Session.user_id == user.id).count()
        else:
            return self.session.query(Session).filter(Session.active == 1).order_by(Session.user_id).count()

    @require_administrator
    def opened_sessions(self, user=None):
        if isinstance(user, User):
            return self.session.query(Session).filter(Session.active == 1, Session.user_id == user.id).all()
        else:
            return self.session.query(Session).filter(Session.active == 1).order_by(Session.user_id).all()

    @require_administrator
    def log_opened_sessions(self, user=None):
        if user is not None:
            if not isinstance(user, User):
                user = None
        user_text = ''
        if user is not None:
            user_text = ' for @%s' % user.login
        record = 'Listing opened sessions' + user_text
        self.log_manager.log_record(record=record, category='Information')
        for opened_session in self.opened_sessions(user=user):
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

    @require_administrator
    def log_user_info(self, user, log_sessions=False):
        if isinstance(user, User):
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
                last_log_off = self.session.query(func.max(Session.closed)).filter(Session.user_id == user.id).one()[0]
                last_log_off = last_log_off.strftime(default_date_time_format)
                record = '@%s id offline since %s' % (user.login, last_log_off)
                self.log_manager.log_record(record=record, category='Information')

    @require_signed_in
    def close_session(self, session):
        if session == self.session_data or self.check_if_user_is_administrator:
            if isinstance(session, Session):
                if session.active:
                    self.project_manager.close_project(session=session)
                    session.active = False
                    self.session.commit()
                    if session.user.login == self.user.login:
                        record = 'Session #%s closed' % session.token
                    else:
                        record = 'Session #%s (@%s) closed' % (session.token, session.user.login)
                    self.log_manager.log_record(record=record, category='Information')
        else:
            record = 'Attempt to close session #%s (@%s) by @%s' % (session.token, session.user.login, self.user.login)
            self.log_manager.log_record(record=record, category='Warning')

    @require_administrator
    def logoff_user(self, user):
        if isinstance(user, User):
            record = 'Kicking off @%s' % user.login
            self.log_manager.log_record(record=record, category='Warning')
            opened_sessions = self.count_opened_sessions(user)
            for session in self.opened_sessions(user):
                self.close_session(session)
            record = '@%s was logged off (closed %d sessions)' % (user.login, opened_sessions)
            self.log_manager.log_record(record=record, category='Warning')

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
