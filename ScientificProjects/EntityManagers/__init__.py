from __future__ import division, print_function

from sqlalchemy.orm import sessionmaker


class EntityManager(object):

    def __init__(self, engine, session_manager):
        self.engine = engine
        self.session_manager = session_manager
        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()
