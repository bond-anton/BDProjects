from __future__ import division, print_function

import os
import datetime

from sqlalchemy.exc import IntegrityError

from BDProjects.Entities import Session
from BDProjects.Entities import Project, SessionProject
from BDProjects.EntityManagers import EntityManager
from BDProjects.EntityManagers import LogManager


class ProjectManager(EntityManager):

    def __init__(self, engine, session_manager):
        super(ProjectManager, self).__init__(engine, session_manager)
        self._log_manager_backup = self.session_manager.log_manager

    def create_project(self, name, data_dir, description=None):
        if self.session_manager.signed_in():
            self.session_data = self.session_manager.session_data
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
        else:
            record = 'Attempt to create project before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
        return None

    def delete_project(self, project):
        if self.session_manager.signed_in():
            self.session_data = self.session_manager.session_data
            if isinstance(project, Project):
                self.session.delete(project)
                self.session.commit()
                record = 'Project "%s" successfully deleted' % project.name
                self.session_manager.log_manager.log_record(record=record,
                                                            category='Information')
                return True
            else:
                record = 'Wrong argument for project delete operation'
                self.session_manager.log_manager.log_record(record=record,
                                                            category='Warning')
                return False
        else:
            record = 'Attempt to delete project before signing in'
            self.session_manager.log_manager.log_record(record=record,
                                                        category='Warning')
            return False

    def get_projects(self, name=None):
        if self.session_manager.signed_in():
            self.session_data = self.session_manager.session_data
            q = self.session.query(Project)
            if name is not None and len(str(name)) > 2:
                template = '%' + str(name) + '%'
                q = q.filter(Project.name.ilike(template))
            return q.all()
        else:
            record = 'Attempt to query projects before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')

    def open_project(self, project_name):
        if self.session_manager.signed_in():
            self.session_data = self.session_manager.session_data
            project = self.session.query(Project).filter(Project.name == str(project_name)).all()
            if project:
                project = project[0]
                if not self.project_opened():
                    sp = SessionProject(session_id=self.session_data.id,
                                        project_id=project.id)
                    self.session_data.projects_opened.append(sp)
                    self.session.commit()
                    self.project = project
                    self.user = self.session_manager.user
                    self.session_manager.log_manager = LogManager(self.engine, self)
                    record = 'Project "%s" opened (#%s)' % (self.project.name, self.session_data.token)
                    self.session_manager.log_manager.log_record(record=record, category='Information')
                    return self.project
                elif self.project_opened(project):
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
        else:
            record = 'Attempt open project before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None

    def project_opened(self, session=None, project=None):
        if self.session_manager.signed_in():
            self.session_data = self.session_manager.session_data
            if not isinstance(session, Session):
                session = self.session_data
            if project is None:
                projects = self.session.query(SessionProject).filter(
                    SessionProject.session_id == session.id,
                    SessionProject.closed == None).all()
            else:
                projects = self.session.query(SessionProject).filter(
                    SessionProject.session_id == session.id,
                    SessionProject.closed == None).join(
                    Project).filter(Project.name == str(project)).all()
            if projects:
                return True
            else:
                return False
        else:
            record = 'Attempt to check if project is opened before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def close_project(self, session=None, project=None):
        if self.session_manager.signed_in():
            self.session_data = self.session_manager.session_data
            if self.project_opened(session, project):
                if not isinstance(session, Session):
                    session = self.session_data
                if project is None:
                    projects = self.session.query(SessionProject).filter(
                        SessionProject.session_id == session.id,
                        SessionProject.closed == None).all()
                else:
                    projects = self.session.query(SessionProject).filter(
                        SessionProject.session_id == session.id,
                        SessionProject.closed == None).join(
                        Project).filter(Project.name == str(project)).all()
                projects[0].closed = datetime.datetime.now()
                self.session.commit()
                record = 'Project "%s" closed (#%s)' % (projects[0].project.name, session.token)
                self.session_manager.log_manager.log_record(record=record, category='Information')
                self.project = None
                self.session_manager.log_manager = self._log_manager_backup
                return True
            else:
                if project is None:
                    record = 'Session #%s has no projects opened' % session.token
                else:
                    # record = 'Project "%s" is not opened' % self.project.name
                    record = 'Project "%s" is not opened' % str(project)
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return True
        else:
            record = 'Attempt to close project before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False
