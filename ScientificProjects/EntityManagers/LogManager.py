from __future__ import division, print_function

from sqlalchemy import func

from ScientificProjects import default_log_categories
from ScientificProjects.Entities.Log import LogCategory, Log
from ScientificProjects.Entities.Project import Project
from ScientificProjects.Entities.Session import Session
from ScientificProjects.Entities.User import User
from ScientificProjects.EntityManagers import EntityManager


class LogManager(EntityManager):

    def __init__(self, engine, session_manager, echo=True):
        self.echo = echo
        super(LogManager, self).__init__(engine, session_manager)

    def create_log_category(self, category, description=None):
        log_category, category_exists = self._check_category_name(category, description)
        if log_category and not category_exists:
            if self.session_manager.session_data is not None:
                log_category.session_id = self.session_manager.session_data.id
            self.session.add(log_category)
            self.session.commit()
            if log_category.category not in default_log_categories:
                self.log_record('Log category %s successfully created' % log_category.category, 'Information')
            return log_category
        else:
            self.session.rollback()
            if log_category.category not in default_log_categories:
                self.log_record('Log category %s is already registered' % log_category.category, 'Warning')
            return self.session.query(LogCategory).filter(LogCategory.category == log_category.category).one()

    def log_record(self, record, category=None):
        log_category, category_exists = self._check_category_name(category)
        category_id, project_id, session_id = None, None, None
        if not category_exists:
            self.log_record('Create log category first', 'Warning')
        else:
            category_id = log_category.id
            if self.session_manager.project is not None:
                if not isinstance(self.session_manager.project, Project):
                    raise ValueError('provide a Project instance or None')
                project_id = self.session_manager.project.id
            if self.session_manager.session_data is not None:
                if not isinstance(self.session_manager.session_data, Session):
                    raise ValueError('provide a valid Session or None')
                session_id = self.session_manager.session_data.id
            log = Log(record=record, category_id=category_id, project_id=project_id, session_id=session_id)
            self.session.add(log)
            self.session.commit()
            if self.echo:
                login_length = self._get_max_login_length()
                user_login = self.session_manager.user.login
                user_login = '@' + user_login + ' ' * (login_length - len(user_login))
                print('[%s] %s: %s' % (log_category.category.upper()[:4], user_login, record))

    def _get_max_login_length(self):
        return self.session.query(func.max(func.length(User.login))).one()[0]

    def _check_category_name(self, category, description=None):
        category_exists = False
        if isinstance(category, str):
            log_category = LogCategory(category=category, description=description)
            existing_category = self.session.query(LogCategory).filter(
                LogCategory.category == log_category.category).all()
            if existing_category:
                log_category = existing_category[0]
                category_exists = True
        else:
            log_category = None
        return log_category, category_exists
