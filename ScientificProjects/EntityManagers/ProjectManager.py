from __future__ import division, print_function

import os

from sqlalchemy.exc import IntegrityError

from ScientificProjects.Entities.Project import Project
from ScientificProjects.EntityManagers import EntityManager
from ScientificProjects.EntityManagers.LogManager import LogManager


class ProjectManager(EntityManager):

    def __init__(self, engine, session_manager):
        super(ProjectManager, self).__init__(engine, session_manager)
        self.log_manager = self.session_manager.log_manager

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_project()
        self.close_session()

    def create_project(self, name, description, data_dir):
        if self.project_opened():
            self.close_project()
        if self.session_manager.signed_in():
            self.user = self.session_manager.user
            self.log_manager = LogManager(self.engine, self)
            data_dir = str(data_dir)
            if os.path.isdir(data_dir) and os.access(data_dir, os.W_OK | os.X_OK):
                project = Project(name=str(name), description=str(description),
                                  owner_id=self.session_manager.user.id,
                                  data_dir=data_dir)
                try:
                    self.session.add(project)
                    self.session.commit()
                    self.log_manager.log_record(record='Project %s created' % project.name,
                                                category='Information')
                    self.open_project(project)
                except IntegrityError:
                    self.session.rollback()
                    self.log_manager.log_record(record='Project %s already exists' % project.name,
                                                category='Warning')
                    self.open_project(project)
            else:
                self.log_manager.log_record(record='Directory %s not writable' % data_dir,
                                            category='Warning')
        else:
            self.log_manager.log_record(record='Attempt to create project before signing in',
                                        category='Warning')

    def get_own_projects(self):
        if self.session_manager.signed_in():
            self.user = self.session_manager.user
            projects = self.session.query(Project).filter(Project.owner == self.session_manager.user).all()
            return projects
        else:
            self.log_manager.log_record(record='Attempt to get list of user project before signing in',
                                        category='Warning')

    def open_project(self, project):
        if self.project_opened():
            if self.project.name == str(project):
                self.log_manager.log_record(record='Project %s already opened' % self.project,
                                            category='Information')
                return True
            else:
                self.close_project()
        if self.session_manager.signed_in():
            self.user = self.session_manager.user
            if isinstance(project, Project):
                self.open_project(project.name)
            elif isinstance(project, str):
                projects = self.session.query(Project).filter(Project.owner == self.session_manager.user,
                                                              Project.name == project).all()
                if projects:
                    self.project = projects[0]
                    self.project.opened = True
                    self.session.commit()
                    self.log_manager = LogManager(self.engine, self)
                    self.log_manager.log_record(record='Project %s opened' % self.project,
                                                category='Information')
                    return True
                else:
                    self.log_manager.log_record(record='Project %s not found' % project,
                                                category='Information')
                    return False
            else:
                self.log_manager.log_record(record='Can not open project: wrong argument',
                                            category='Warning')
                return False
        else:
            self.log_manager.log_record(record='Attempt to open project before signing in',
                                        category='Warning')
            return False

    def project_opened(self):
        if isinstance(self.project, Project):
            projects = self.session.query(Project).filter(Project.name == str(self.project.name),
                                                          Project.opened == 1).all()
            if projects:
                return True
            else:
                self.project = None
                self.log_manager = self.session_manager.log_manager
        return False

    def close_project(self):
        if self.project_opened():
            self.project.opened = False
            self.session.commit()
            self.log_manager.log_record(record='Project %s closed' % self.project,
                                        category='Information')
            self.project = None
            self.user = self.session_manager.user
            self.log_manager = self.session_manager.log_manager
