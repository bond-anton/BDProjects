from __future__ import division, print_function

from sqlalchemy.exc import IntegrityError

from ScientificProjects.Entities.Log import LogCategory, Log
from ScientificProjects.Entities.Project import Project
from ScientificProjects.Entities.Role import Role
from ScientificProjects.EntityManagers import EntityManager


class LogManager(EntityManager):

    def __init__(self, engine, session_manager, echo=True):
        self.echo = echo
        self.default_log_categories = {'Information': 'Informational messages',
                                       'Warning': 'Warning messages',
                                       'Error': 'Error messages'}
        super(LogManager, self).__init__(engine, session_manager)
        self._create_default_log_categories()

    def create_log_category(self, category, description=None):
        log_category, category_exists = self._check_category_name(category, description)
        if log_category and not category_exists:
            self.session.add(log_category)
            self.session.commit()
            if log_category.category not in self.default_log_categories:
                self.log_record('Log category %s successfully created' % log_category.category, 'Information')
            return log_category
        else:
            self.session.rollback()
            if log_category.category not in self.default_log_categories:
                self.log_record('Log category %s is already registered' % log_category.category, 'Warning')
            return self.session.query(LogCategory).filter(LogCategory.category == log_category.category).one()

    def log_record(self, record, category=None, project=None, role=None):
        log_category, category_exists = self._check_category_name(category)
        category_id, project_id, role_id = None, None, None
        if not category_exists:
            self.log_record('Create log category first', 'Warning', project=project, role=role)
        else:
            category_id = log_category.id
            if project is not None:
                if not isinstance(project, Project):
                    raise ValueError('provide a Project instance or None')
                project_id = project.id
            if role is not None:
                if not isinstance(role, Role):
                    raise ValueError('provide a Role instance or None')
                role_id = role.id
            log = Log(record=record, category_id=category_id, project_id=project_id, role_id=role_id)
            self.session.add(log)
            self.session.commit()
            if self.echo:
                if role is None:
                    role_title = 'bot'
                    user_login = 'bot'
                else:
                    role_title = role.title
                    user_login = role.user.login
                print('[%s] %s (@%s): %s' % (log_category.category, role_title, user_login, record))

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
        for category in self.default_log_categories:
            self.create_log_category(category, self.default_log_categories[category])
