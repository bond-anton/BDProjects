from __future__ import division, print_function

import os
import datetime

from sqlalchemy.exc import IntegrityError

from BDProjects.Entities import Session
from BDProjects.Entities import Project, SessionProject

from .EntityManager import EntityManager
from BDProjects.EntityManagers import LogManager
from ._helpers import require_signed_in


class ProjectManager(EntityManager):

    def __init__(self, session_manager):
        super(ProjectManager, self).__init__(session_manager)
        self._log_manager_backup = None

    @require_signed_in
    def create_project(self, name, data_dir, description=None):
        data_dir = str(data_dir)
        if os.path.isdir(data_dir) and os.access(data_dir, os.W_OK | os.X_OK):
            project = Project(name=str(name))
            project.created_session_id = self.session_manager.session_data.id
            project.data_dir = data_dir
            if description is not None:
                project.description = str(description)
            try:
                self.session.add(project)
                self.session.commit()
                record = 'Project "%s" created' % project.name
                self.session_manager.log_manager.log_record(record=record, category='Information')
            except IntegrityError:
                self.session.rollback()
                project = self.session.query(Project).filter(Project.name == str(name)).all()[0]
                record = 'Project "%s" already exists' % project.name
                self.session_manager.log_manager.log_record(record=record, category='Warning')
            return project
        else:
            record = 'Directory "%s" is not writable' % data_dir
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None

    @require_signed_in
    def delete_project(self, project):
        if isinstance(project, Project):
            if project in self.session:
                self.session.delete(project)
                self.session.commit()
                record = 'Project "%s" successfully deleted' % project.name
                self.session_manager.log_manager.log_record(record=record,
                                                            category='Information')
                return True
            else:
                record = 'Project "%s" not found in the database' % project.name
                self.session_manager.log_manager.log_record(record=record,
                                                            category='Warning')
                return False
        else:
            record = 'Wrong argument for project delete operation'
            self.session_manager.log_manager.log_record(record=record,
                                                        category='Warning')
            return False

    @require_signed_in
    def get_projects(self, name=None, exact=False):
        q = self.session.query(Project)
        if name is not None:
            if exact:
                q = q.filter(Project.name == str(name))
            elif len(str(name)) <= 2:
                record = 'Please use exact=True than searching projects with name shorter than 2 chars'
                self.session_manager.log_manager.log_record(record=record,
                                                            category='Warning')
                return None
            else:
                template = '%' + str(name) + '%'
                q = q.filter(Project.name.ilike(template))
        return q.all()

    @require_signed_in
    def open_project(self, project_name):
        project = self.get_projects(name=project_name, exact=True)
        if project:
            project = project[0]
            if not self.project_opened():
                sp = SessionProject(session_id=self.session_data.id,
                                    project_id=project.id)
                self.session_data.projects_opened.append(sp)
                self.session.commit()
                self.project = project
                self._log_manager_backup = self.session_manager.log_manager
                self.session_manager.log_manager = LogManager(self)
                record = 'Project "%s" opened (#%s)' % (self.project.name, self.session_data.token)
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return self.project
            elif self.project_opened(project=project):
                record = 'Project "%s" is already opened in #%s' % (project_name, self.session_data.token)
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return self.project
            else:
                record = 'Close opened project before opening another one'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return None
        else:
            record = 'Project "%s" not found' % project_name
            self.session_manager.log_manager.log_record(record=record, category='Information')
            return None

    @require_signed_in
    def project_opened(self, session=None, project=None):
        if session is None:
            session = self.session_data
        elif not isinstance(session, Session):
            record = 'Provide a valid session to search opened projects, or None for current session'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False
        if project is None:
            projects = self.session.query(SessionProject).filter(
                SessionProject.session_id == session.id,
                SessionProject.closed == None).all()
        elif isinstance(project, Project):
            projects = self.session.query(SessionProject).filter(
                SessionProject.session_id == session.id,
                SessionProject.closed == None,
                SessionProject.project == project).all()
        else:
            record = 'Provide a valid project to look for, or None'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False
        if projects:
            return True
        else:
            return False

    @require_signed_in
    def close_project(self, session=None, project=None):
        if session is None:
            session = self.session_data
        elif not isinstance(session, Session):
            record = 'Provide a valid session to close project for, or None for current session'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False
        if project is not None and not isinstance(project, Project):
            record = 'Provide a valid project to close, or None for current project'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False
        if self.project_opened(session, project):
            if project is None:
                projects = self.session.query(SessionProject).filter(
                    SessionProject.session_id == session.id,
                    SessionProject.closed == None).all()
            elif isinstance(project, Project):
                projects = self.session.query(SessionProject).filter(
                    SessionProject.session_id == session.id,
                    SessionProject.closed == None,
                    SessionProject.project == project).all()
            if projects:
                project = projects[0]
            project.closed = datetime.datetime.now()
            self.session.commit()
            record = 'Project "%s" closed (#%s)' % (project.project.name, session.token)
            self.session_manager.log_manager.log_record(record=record, category='Information')
            self.project = None
            self.session_manager.log_manager = self._log_manager_backup
            return True
        else:
            if project is None:
                record = 'Session #%s has no projects opened' % session.token
            else:
                record = 'Project "%s" is not opened' % str(project)
            self.session_manager.log_manager.log_record(record=record, category='Information')
            return True
