from __future__ import division, print_function

from sqlalchemy.orm import sessionmaker


class EntityManager(object):

    def __init__(self, engine, session_manager):
        self.engine = engine
        self.session_manager = session_manager
        self.user = self.session_manager.user
        self.project = None
        self.session = None
        self.open_session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_session()

    def open_session(self):
        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()

    def close_session(self):
        self.session.close()
        self.session = None
