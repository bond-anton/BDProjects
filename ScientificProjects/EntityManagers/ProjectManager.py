from __future__ import division, print_function

import os
import datetime

from sqlalchemy.exc import IntegrityError

from ScientificProjects.Entities.User import User
from ScientificProjects.Entities.Session import Session
from ScientificProjects.Entities.Project import Project, SessionProject
from ScientificProjects.EntityManagers import EntityManager
from ScientificProjects.EntityManagers.LogManager import LogManager


class ProjectManager(EntityManager):

    def __init__(self, engine, session_manager):
        super(ProjectManager, self).__init__(engine, session_manager)
        self.log_manager = None

    def create_project(self, name, description, data_dir):
        if self.session_manager.signed_in():
            self.session_data = self.session_manager.session_data
            data_dir = str(data_dir)
            if os.path.isdir(data_dir) and os.access(data_dir, os.W_OK | os.X_OK):
                project = Project(name=str(name), description=str(description),
                                  created_session_id=self.session_manager.session_data.id,
                                  data_dir=data_dir)
                try:
                    self.session.add(project)
                    self.session.commit()
                    self.session_manager.log_manager.log_record(record='Project %s created' % project.name,
                                                                category='Information')
                except IntegrityError:
                    self.session.rollback()
                    self.session_manager.log_manager.log_record(record='Project %s already exists' % project.name,
                                                                category='Warning')
            else:
                self.session_manager.log_manager.log_record(record='Directory %s not writable' % data_dir,
                                                            category='Warning')
        else:
            self.session_manager.log_manager.log_record(record='Attempt to create project before signing in',
                                                        category='Warning')

    def get_projects_list(self):
        if self.session_manager.signed_in():
            self.session_data = self.session_manager.session_data
            projects = self.session.query(Project).all()
            return projects
        else:
            record = 'Attempt to get list of available projects before signing in'
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
                    self.log_manager = LogManager(self.engine, self)
                    record = 'Project %s opened' % self.project
                    self.log_manager.log_record(record=record, category='Information')
                    return True
                elif self.project_opened(project):
                    record = 'Project %s already opened' % project_name
                    self.log_manager.log_record(record=record, category='Information')
                    return True
                else:
                    record = 'Close opened project before opening another one'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
            else:
                record = 'Project %s not found' % project_name
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return False
        else:
            record = 'Attempt open project before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

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
                record = 'Project %s closed (#%s)' % (self.project, session.token)
                self.log_manager.log_record(record=record, category='Information')
                self.project = None
                self.log_manager = None
                return True
            else:
                if project is None:
                    record = 'Session %s has no projects opened' % session.token
                else:
                    record = 'Project %s is not opened' % self.project
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return True
        else:
            record = 'Attempt to close project before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False
