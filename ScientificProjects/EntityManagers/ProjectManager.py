from __future__ import division, print_function

import os

from sqlalchemy.exc import IntegrityError

from ScientificProjects.Entities.Project import Project
from ScientificProjects.EntityManagers import EntityManager


class ProjectManager(EntityManager):

    def __init__(self, engine, session_manager):
        self.user = None
        super(ProjectManager, self).__init__(engine, session_manager)

    def create_project(self, name, description, data_dir):
        if self.user:
            data_dir = str(data_dir)
            if os.path.isdir(data_dir) and os.access(data_dir, os.W_OK | os.X_OK):
                project = Project(name=str(name), description=str(description), owner=self.user)
                try:
                    self.session.add(project)
                    self.session.commit()
                    self.open_project(project)
                    team = self.create_team('Project board', 'Project executive managers')
                    role = self.create_role(team, 'Project owner', 'Project owner', self.user, 'Project manager')
                    print('Project created')
                except IntegrityError as e:
                    print('Project with provided name is already registered')
                    self.session.rollback()
            else:
                print('Can not create project: Either %s is not a directory or it is not writable' % data_dir)
        else:
            print('Please sign in, or create a new user')

    def get_own_projects(self):
        if self.user:
            projects = self.session.query(Project).filter(Project.owner == self.user).all()
            return projects
        else:
            print('Please sign in, or create a new user')

    def open_project(self, project):
        if isinstance(project, Project):
            if project in self.get_own_projects():
                self.current_project = project
                print('Opened project \'%s\'' % self.current_project.name)
            else:
                print('Project \'%s\' not found in the list of your projects' % project.name)
        elif isinstance(project, str):
            projects = self.session.query(Project).filter(Project.owner == self.user, Project.name == project).all()
            if projects:
                self.current_project = projects[0]
                print('Opened project %s' % self.current_project.name)
            else:
                print('Project \'%s\' not found in the list of your projects' % project)
        else:
            print('Please provide project name or Project instance')

    def get_current_project_teams(self):
        if self.current_project:
            return self.session.query(Team).filter(Team.project == self.current_project).all()
        else:
            print('Please select a working project first')