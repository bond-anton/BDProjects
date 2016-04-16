from __future__ import division, print_function

from sqlalchemy.exc import IntegrityError

from ScientificProjects.Entities.User import User
from ScientificProjects.EntityManagers import EntityManager
from ScientificProjects.EntityManagers.LogManager import LogManager
from ScientificProjects.EntityManagers.ProjectManager import ProjectManager


class UserManager(EntityManager):

    def __init__(self, engine, session_manager):
        super(UserManager, self).__init__(engine, session_manager)
        self.log_manager = self.session_manager.log_manager
        self.project_manager = None

    def create_user(self, name_first, name_last, email, login, password):
        user = User(name_first=str(name_first), name_last=str(name_last),
                    email=str(email), login=str(login), password=str(password))
        try:
            self.session.add(user)
            self.session.commit()
            self.log_manager.log_record(record='User @%s successfully created' % user.login,
                                        category='Information')
            return user
        except IntegrityError:
            self.session.rollback()
            self.log_manager.log_record(record='User @%s already exists' % user.login,
                                        category='Warning')
            return self.session.query(User).filter(User.login == str(login)).one()

    def sign_in(self, login, password):
        if self.signed_in():
            # UserManager works with only one User at a time
            self.sign_out()
        user = self.session.query(User).filter(User.login == str(login)).all()
        if user:
            user = user[0]
            if user.password == str(password):
                self.user = user
                self.user.signed_in = True
                self.session.commit()
                self.log_manager = LogManager(self.engine, self)
                self.log_manager.log_record(record='@%s signed in' % self.user.login,
                                            category='Information')
                # Project manager is created only if user signed in
                self.project_manager = ProjectManager(self.engine, self)
            else:
                self.log_manager.log_record(record='Login failed. Username: @%s' % self.user.login,
                                            category='Warning')
        else:
            self.log_manager.log_record(record='Login failed. Username: @%s' % str(login),
                                        category='Warning')

    def sign_out(self):
        if self.signed_in():
            self.user.signed_in = False
            self.session.commit()
            self.log_manager.log_record(record='@%s signed out' % self.user.login,
                                        category='Information')
            self.user = self.session_manager.user
            self.log_manager = self.session_manager.log_manager
            self.project_manager = None

    def signed_in(self):
        if isinstance(self.user, User):
            if self.user.signed_in:
                return True
        return False
