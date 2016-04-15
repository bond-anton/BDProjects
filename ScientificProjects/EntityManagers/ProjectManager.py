from __future__ import division, print_function

import os

from sqlalchemy.exc import IntegrityError

from ScientificProjects.Entities.Project import Project
from ScientificProjects.EntityManagers import EntityManager


class ProjectManager(EntityManager):

    def __init__(self, engine, session_manager):
        self.current_project = None
        super(ProjectManager, self).__init__(engine, session_manager)

    def create_project(self, name, description, data_dir):
        if self.session_manager.user_manager.signed_in():
            data_dir = str(data_dir)
            if os.path.isdir(data_dir) and os.access(data_dir, os.W_OK | os.X_OK):
                project = Project(name=str(name), description=str(description),
                                  owner_id=self.session_manager.user_manager.user.id,
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

    def get_own_projects(self):
        if self.session_manager.user_manager.signed_in():
            projects = self.session.query(Project).filter(Project.owner == self.session_manager.user_manager.user).all()
            return projects
        else:
            self.session_manager.log_manager.log_record(record='Attempt to get list of user project before signing in',
                                                        category='Warning')

    def open_project(self, project):
        if self.session_manager.user_manager.signed_in():
            if isinstance(project, Project):
                if project in self.get_own_projects():
                    self.current_project = project
                    self.session_manager.log_manager.log_record(record='Project %s opened' % project.name,
                                                                category='Information')
                else:
                    self.session_manager.log_manager.log_record(record='Project %s not found' % project.name,
                                                                category='Information')
            elif isinstance(project, str):
                projects = self.session.query(Project).filter(Project.owner == self.session_manager.user_manager.user,
                                                              Project.name == project).all()
                if projects:
                    self.current_project = projects[0]
                    self.session_manager.log_manager.log_record(record='Project %s opened' % self.current_project,
                                                                category='Information')
                else:
                    self.session_manager.log_manager.log_record(record='Project %s not found' % project,
                                                                category='Information')
            else:
                self.session_manager.log_manager.log_record(record='Can not open project: wrong argument',
                                                            category='Warning')
        else:
            self.session_manager.log_manager.log_record(record='Attempt to open project before signing in',
                                                        category='Warning')
