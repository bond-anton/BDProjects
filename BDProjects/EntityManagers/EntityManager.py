from __future__ import division, print_function

from sqlalchemy.orm.session import Session as orm_Session

from BDProjects.Entities import Session, Project, User


class EntityManager(object):

    def __init__(self, session_manager):
        self.__session_manager = session_manager
        self.__engine = self.session_manager.engine
        self.__user = None
        self.__session_data = None
        self.__project = None
        self.__session = None
        self.session = self.session_manager.session
        self.user = self.session_manager.user
        self.project = None

    @property
    def session_manager(self):
        return self.__session_manager

    @property
    def engine(self):
        return self.__engine

    @property
    def session(self):
        return self.__session

    @session.setter
    def session(self, session):
        if isinstance(session, orm_Session) or session is None:
            self.__session = session
        else:
            raise ValueError('Can not set session')

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
