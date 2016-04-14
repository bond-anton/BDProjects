from __future__ import division, print_function

from sqlalchemy.exc import IntegrityError

from ScientificProjects.Entities.Log import LogCategory, Log
from ScientificProjects.Entities.Project import Project
from ScientificProjects.Entities.Role import Role
from ScientificProjects.EntityManagers import EntityManager


class LogManager(EntityManager):

    def __init__(self, engine, session_manager):
        self.user = None
        super(LogManager, self).__init__(engine, session_manager)
        self._create_default_log_categories()

    def create_log_category(self, category, description=None):
        log_category, category_exists = self._check_category_name(category, description)
        if log_category and not category_exists:
            self.session.add(log_category)
            self.session.commit()
            print('Category %s successfully created' % log_category.category)
            return log_category
        else:
            print('Log category %s is already registered' % log_category.category)
            self.session.rollback()
            return self.session.query(LogCategory).filter(LogCategory.category == log_category.category).one()

    def log_record(self, record, category=None, project=None, role=None):
        log_category, category_exists = self._check_category_name(category)
        if not category_exists:
            print('Create log category first')
        if project is not None:
            if not isinstance(project, Project):
                raise ValueError('provide a Project instance or None')
        if role is not None:
            if not isinstance(role, Role):
                raise ValueError('provide a Role instance or None')
        log = Log(record=record, category=log_category, project=project, role=role)
        self.session.add(log)
        self.session.commit()

    def _check_category_name(self, category, description=None):
        category_exists = False
        if isinstance(category, str):
            log_category = LogCategory(category=category, description=description)
        elif isinstance(category, LogCategory):
            log_category = category
        else:
            log_category = None
        existing_category = self.session.query(LogCategory).filter(LogCategory.category == log_category.category).all()
        if existing_category:
            log_category = existing_category[0]
            category_exists = True
        return log_category, category_exists

    def _create_default_log_categories(self):
        default_log_categories = {'Information': 'Informational messages',
                                  'Warning': 'Warning messages',
                                  'Error': 'Error messages',}
        for category in default_log_categories:
            self.create_log_category(category, default_log_categories[category])
