from __future__ import division, print_function

from sqlalchemy.orm import sessionmaker


class EntityManager(object):

    def __init__(self, engine, session_manager):
        self.engine = engine
        self.session_manager = session_manager
        self.session = None
        self.open_session()

    def open_session(self):
        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()

    def close_session(self):
        self.session.close()
        self.session = None


class DependentEntityManager(object):

    def __init__(self, session, session_manager):
        self.session = session
        self.session_manager = session_manager
