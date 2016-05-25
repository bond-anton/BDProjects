from __future__ import division, print_function

import os
import datetime

from sqlalchemy.exc import IntegrityError

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
            projects = self.session.query(Project).all()
            return projects
        else:
            self.session_manager.log_manager.log_record(record='Attempt to get list of projects before signing in',
                                                        category='Warning')

    def open_project(self, project_name):
        project = self.session.query(Project).filter(Project.name == str(project_name)).all()
        if project:
            project = project[0]
            if not self.project_opened(project):
                sp = SessionProject(session_id=self.session_data.id,
                                    project_id=project.id)
                self.session_data.projects_opened.append(sp)
                self.session.commit()
                self.session_manager.log_manager.log_record(record='Project %s opened' % self.project,
                                                            category='Information')
            else:
                self.session_manager.log_manager.log_record(record='Project %s already opened' % project_name,
                                                            category='Information')
            return True
        else:
            self.session_manager.log_manager.log_record(record='Project %s not found' % project_name,
                                                        category='Information')
            return False

    def project_opened(self, project):
        if self.session_manager.signed_in():
            self.session_data = self.session_manager.session_data
            projects = self.session.query(SessionProject).filter(
                SessionProject.session_id == self.session_data.id,
                SessionProject.closed == None).join(
                Project).filter(Project.name == str(project)).all()
            if projects:
                return True
            else:
                return False
        else:
            self.session_manager.log_manager.log_record(record='Attempt to get list of opened projects before signing in',
                                                        category='Warning')
            return False

    def close_project(self, project_name):
        if self.project_opened(project_name):
            self.session_data.projects_opened.closed = datetime.datetime.now()
            self.session.commit()
            self.session_manager.log_manager.log_record(record='Project %s closed' % self.project,
                                                        category='Information')
        else:
            self.session_manager.log_manager.log_record(record='Project %s is not opened' % self.project,
                                                        category='Information')

    def opened_projects(self, only_own=True):
        if self.session_manager.signed_in():
            self.session_data = self.session_manager.session_data
            if not only_own:
                projects = self.session.query(SessionProject).filter(SessionProject.closed == None).all()
            else:
                projects = self.session.query(SessionProject).filter(
                    SessionProject.session_id == self.session_data.id,
                    SessionProject.closed == None).all()
            return projects
        else:
            self.session_manager.log_manager.log_record(record='Attempt to get list of user project before signing in',
                                                        category='Warning')
            return []

    def close_all_projects(self, only_own=True):
        if only_own:
            log_message = 'Closing all opened by @%s projects' % self.session_manager.user.login
        else:
            log_message = 'Closing all opened projects'
        self.session_manager.log_manager.log_record(record=log_message,
                                                    category='Information')
        for project in self.opened_projects(only_own):
            project.opened = False
            self.session.commit()
            self.session_manager.log_manager.log_record(record='Project %s was closed' % project.name,
                                                        category='Information')

    def activate_project(self, project_name):
        if self.project_opened(project_name):
            self.session_data.projects_opened.closed = datetime.datetime.now()
            self.session.commit()
            self.session_manager.log_manager.log_record(record='Project %s closed' % self.project,
                                                        category='Information')
        else:
            self.session_manager.log_manager.log_record(record='Project %s is not opened' % self.project,
                                                        category='Information')
