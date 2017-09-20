from __future__ import division, print_function

from BDProjects.Entities import Role, User


def require_signed_in(protected_function):
    def wrapper(self, *args, **kwargs):
        if self.session_manager.signed_in():
            return protected_function(self, *args, **kwargs)
        else:
            record = 'Attempt to %s before signing in' % protected_function.__name__.replace('_', ' ')
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None
    wrapper.__name__ = protected_function.__name__
    return wrapper


def require_administrator(protected_function):
    def wrapper(self, *args, **kwargs):
        if self.session_manager.check_if_user_is_administrator():
            return protected_function(self, *args, **kwargs)
        else:
            record = 'Attempt to %s without administrator rights' % protected_function.__name__.replace('_', ' ')
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None

    wrapper.__name__ = protected_function.__name__
    return wrapper


def require_not_system_user(protected_function):
    def wrapper(self, *args, **kwargs):
        user = args[0]
        if isinstance(user, User):
            login = user.login
        else:
            login = str(user)
        system_users = self.session.query(Role).filter(Role.name == 'system').one().users
        for system_user in system_users:
            if system_user.login == login:
                record = 'Attempt to %s using system user credentials' % protected_function.__name__.replace('_', ' ')
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return None
        else:
            return protected_function(self, *args, **kwargs)
    wrapper.__name__ = protected_function.__name__
    return wrapper


def require_project_opened(protected_function):
    def wrapper(self, *args, **kwargs):
        if self.session_manager.project_manager.project_opened():
            return protected_function(self, *args, **kwargs)
        else:
            record = 'Attempt to %s before opening project' % protected_function.__name__.replace('_', ' ')
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None
    wrapper.__name__ = protected_function.__name__
    return wrapper
