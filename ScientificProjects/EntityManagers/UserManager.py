from __future__ import division, print_function
import sys
import datetime
import socket
import uuid

from sqlalchemy import exists, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from ScientificProjects import default_users, default_date_time_format
from ScientificProjects.Entities.User import User
from ScientificProjects.Entities.Session import Session
from ScientificProjects.EntityManagers import EntityManager
from ScientificProjects.EntityManagers.LogManager import LogManager
from ScientificProjects.EntityManagers.ProjectManager import ProjectManager
from ScientificProjects.EntityManagers.ParameterManager import ParameterManager


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
        self.parameter_manager = ParameterManager(self.engine, self)

    def create_user(self, name_first, name_last, email, login, password):
        user = User(name_first=str(name_first), name_last=str(name_last),
                    email=str(email), login=str(login), password=str(password))
        try:
            self.session.add(user)
            self.session.commit()
            if user.login not in default_users:
                self.log_manager.log_record(record='User @%s successfully created' % user.login,
                                            category='Information')
            return user
        except IntegrityError:
            self.session.rollback()
            if user.login not in default_users:
                self.log_manager.log_record(record='User @%s already exists' % user.login,
                                            category='Warning')
            return self.session.query(User).filter(User.login == str(login)).one()

    def sign_in(self, login, password):
        if login not in default_users:
            if self.signed_in():
                # UserManager works with only one User at a time
                self.sign_out()
            user = self.session.query(User).filter(User.login == str(login)).all()
            if user:
                user = user[0]
                if user.password == str(password):
                    self.user = user
                    self.session_data = self._generate_session_data()
                    self.session.add(self.session_data)
                    self.session.commit()
                    self.log_manager = LogManager(self.engine, self)
                    self.log_manager.log_record(record='@%s signed in' % self.user.login,
                                                category='Information')
                else:
                    self.log_manager.log_record(record='Login failed. Username: @%s' % self.user.login,
                                                category='Warning')
            else:
                self.log_manager.log_record(record='Login failed. Username: @%s' % str(login),
                                            category='Warning')
        else:
            self.log_manager.log_record(record='Login failed (system user). Username: @%s' % str(login),
                                        category='Warning')

    def sign_out(self):
        if self.signed_in():
            self.project_manager.close_project()
            self.session_data.active = False
            self.session.commit()
            self.log_manager.log_record(record='@%s signed out' % self.user.login,
                                        category='Information')
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

    def count_opened_sessions(self, user=None):
        if isinstance(user, User):
            return self.session.query(Session).filter(Session.active == 1, Session.user_id == user.id).count()
        else:
            return self.session.query(Session).filter(Session.active == 1).order_by(Session.user_id).count()

    def opened_sessions(self, user=None):
        if isinstance(user, User):
            return self.session.query(Session).filter(Session.active == 1, Session.user_id == user.id).all()
        else:
            return self.session.query(Session).filter(Session.active == 1).order_by(Session.user_id).all()

    def log_opened_sessions(self, user=None):
        if user is not None:
            if not isinstance(user, User):
                user = None
        user_text = ''
        if user is not None:
            user_text = ' for @%s' % user.login
        self.log_manager.log_record(record='Listing opened sessions' + user_text,
                                    category='Information')
        for opened_session in self.opened_sessions(user=user):
            signed_in_for = (datetime.datetime.utcnow() - opened_session.opened)
            opened = opened_session.opened.strftime(default_date_time_format)
            self.log_manager.log_record(record='#%s (@%s) is opened for %s (since %s)' % (opened_session.token,
                                                                                          opened_session.user.login,
                                                                                          signed_in_for,
                                                                                          opened),
                                        category='Information')

    def signed_in_users(self):
        return self.session.query(User).join(Session).filter(Session.active == 1).all()

    def log_signed_in_users(self, log_sessions=False):
        self.log_manager.log_record(record='Listing signed in users',
                                    category='Information')
        for user in self.signed_in_users():
            self.log_user_info(user, log_sessions=log_sessions)

    def log_user_info(self, user, log_sessions=False):
        if isinstance(user, User):
            opened_sessions = self.count_opened_sessions(user)
            if opened_sessions > 0:
                since = self.session.query(func.min(Session.opened)).filter(Session.user_id == user.id,
                                                                            Session.active == 1).one()[0]
                since = since.strftime(default_date_time_format)
                self.log_manager.log_record(record='@%s has %d opened sessions since %s' % (user.login,
                                                                                            opened_sessions,
                                                                                            since),
                                            category='Information')
                if log_sessions:
                    self.log_opened_sessions(user)
            else:
                last_log_off = self.session.query(func.max(Session.closed)).filter(Session.user_id == user.id).one()[0]
                last_log_off = last_log_off.strftime(default_date_time_format)
                self.log_manager.log_record(record='@%s id offline since %s' % (user.login,
                                                                                last_log_off),
                                            category='Information')

    def logoff_user(self, user):
        if isinstance(user, User):
            opened_sessions = self.count_opened_sessions(user)
            for session in self.opened_sessions(user):
                session.active = False
            self.session.commit()
            self.log_manager.log_record(record='@%s was logged off (closed %d sessions)' % (user.login,
                                                                                            opened_sessions),
                                        category='Warning')

    def logoff_users(self, users):
        if isinstance(users, (list, tuple)):
            for user in users:
                self.logoff_user(user)

    def logoff_all(self):
        self.log_manager.log_record(record='Kick-off ALL signed in users',
                                    category='Warning')
        self.project_manager.close_all_projects()
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
