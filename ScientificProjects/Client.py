from __future__ import division, print_function
import datetime

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from ScientificProjects import Base, default_date_time_format
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


class Client(object):

    def __init__(self, db_name='/:memory:', backend='sqlite',
                 hostname='', port='', user='', password=''):
        credentials = user + ':' + password if password else user
        if credentials:
            credentials += '@'
        if port:
            hostname += ':' + str(port)
        db_url = backend + '://' + credentials + hostname + '/' + db_name
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
        self.close_all_projects()
        self.logoff_users(self.signed_in_users())

    def opened_projects(self):
        return self.session.query(Project).filter(Project.opened == 1).all()

    def close_all_projects(self):
        for project in self.opened_projects():
            project.opened = False
            self.session.commit()
            self.log_manager.log_record(record='Project %s was closed' % project.name,
                                        category='Information')
