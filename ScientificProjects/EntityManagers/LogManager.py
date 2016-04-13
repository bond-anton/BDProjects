from __future__ import division, print_function

from sqlalchemy.exc import IntegrityError

from ScientificProjects.Entities.Log import LogCategory, Log
from ScientificProjects.EntityManagers import EntityManager


class LogManager(EntityManager):

    def __init__(self, engine):
        self.user = None
        super(LogManager, self).__init__(engine)

    def create_log_category(self, category, description=None):
        log_category = LogCategory(category=category, description=description)
        try:
            self.session.add(log_category)
            self.session.commit()
            print('Category %s successfully created' % log_category.category)
            return log_category
        except IntegrityError as e:
            print('Log category %s is already registered' % log_category.category)
            self.session.rollback()
            return self.session.query(LogCategory).filter(LogCategory.category == category).one()

    def log_record(self, record, category=None, project=None, role=None):
        if isinstance(category, LogCategory):
            if category in self.session.query(LogCategory).all():
                log_category = category
            else:
                print('Add log category %s first', category.category)
        elif isinstance(category, str):
            log_category = self.session.query(LogCategory).filter(LogCategory.category == category).one()
            if not log_category:
                print('Log category %s not found', category)
        else:
            print('Expected Log category to be of type LogCategory or string, got %s' % type(category))
        log = Log(record=str(record), category=log_category, project=project, role=role)
        self.session.add(log)
        self.session.commit()
