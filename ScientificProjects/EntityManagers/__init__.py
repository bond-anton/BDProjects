from __future__ import division, print_function

from sqlalchemy.orm import sessionmaker


class EntityManager(object):

    def __init__(self, engine):
        self.engine = engine
        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()
