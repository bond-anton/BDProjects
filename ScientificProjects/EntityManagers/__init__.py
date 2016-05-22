from __future__ import division, print_function

from sqlalchemy.orm import sessionmaker


class EntityManager(object):

    def __init__(self, engine, session_manager=None):
        self.engine = engine
        self.session_manager = session_manager
        self.user = None
        self.session_data = None
        self.project = None
        self.session = None
        self.open_session()

    def open_session(self):
        if self.session_manager is None:
            session = sessionmaker()
            session.configure(bind=self.engine)
            self.session = session()
        else:
            self.session = self.session_manager.session
            self.user = self.session_manager.user

    def close_session(self):
        self.session.close()
        self.session = None
