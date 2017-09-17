from __future__ import division, print_function


def require_signed_in(protected_function):
    def wrapper(self, *args, **kwargs):
        if self.session_manager.signed_in():
            return protected_function(self, *args, **kwargs)
        else:
            record = 'Attempt to %s before signing in' % protected_function.__name__.replace('_', ' ')
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None
    return wrapper


def require_project_opened(protected_function):
    def wrapper(self, *args, **kwargs):
        if self.session_manager.project_manager.project_opened():
            return protected_function(self, *args, **kwargs)
        else:
            record = 'Attempt to %s before opening project' % protected_function.__name__.replace('_', ' ')
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None
    return wrapper
