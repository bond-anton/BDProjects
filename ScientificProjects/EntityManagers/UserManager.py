from __future__ import division, print_function
import datetime

from sqlalchemy.exc import IntegrityError

from ScientificProjects.Entities.User import User
from ScientificProjects.EntityManagers import EntityManager
from ScientificProjects.EntityManagers.LogManager import LogManager
from ScientificProjects.EntityManagers.ProjectManager import ProjectManager
from ScientificProjects.EntityManagers.ParameterManager import ParameterManager


class UserManager(EntityManager):

    def __init__(self, engine, session_manager):
        super(UserManager, self).__init__(engine, session_manager)
        self.log_manager = self.session_manager.log_manager
        self.project_manager = ProjectManager(self.engine, self)
        self.parameter_manager = ParameterManager(self.engine, self)
        self.default_users = {'bot': [None, None, None, 'bot', None]}
        self._create_default_users()

    def __exit__(self, exc_type, exc_value, traceback):
        self.sign_out()
        self.close_session()

    def create_user(self, name_first, name_last, email, login, password):
        user = User(name_first=str(name_first), name_last=str(name_last),
                    email=str(email), login=str(login), password=str(password))
        try:
            self.session.add(user)
            self.session.commit()
            if user.login not in self.default_users:
                self.log_manager.log_record(record='User @%s successfully created' % user.login,
                                            category='Information')
            return user
        except IntegrityError:
            self.session.rollback()
            if user.login not in self.default_users:
                self.log_manager.log_record(record='User @%s already exists' % user.login,
                                            category='Warning')
            return self.session.query(User).filter(User.login == str(login)).one()

    def sign_in(self, login, password):
        if login not in self.default_users:
            if self.signed_in():
                # UserManager works with only one User at a time
                self.sign_out()
            user = self.session.query(User).filter(User.login == str(login)).all()
            if user:
                user = user[0]
                if user.password == str(password):
                    self.user = user
                    self.user.signed_in = True
                    self.user.last_sign_in = datetime.datetime.utcnow()
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
            self.user.signed_in = False
            self.user.last_sign_out = datetime.datetime.utcnow()
            self.session.commit()
            self.log_manager.log_record(record='@%s signed out' % self.user.login,
                                        category='Information')
            self.user = self.session_manager.user
            self.log_manager = self.session_manager.log_manager

    def signed_in(self):
        if isinstance(self.user, User):
            users = self.session.query(User).filter(User.login == str(self.user.login),
                                                    User.signed_in == 1).all()
            if users:
                return True
            else:
                self.user = self.session_manager.user
                self.log_manager = self.session_manager.log_manager
                return False
        return False

    def _create_default_users(self):
        for user_data in self.default_users:
            user = self.default_users[user_data]
            self.create_user(user[0], user[1], user[2], user[3], user[4])
