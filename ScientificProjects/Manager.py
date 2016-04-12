from __future__ import division, print_function
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from ScientificProjects import Base

from ScientificProjects.Users import User
from ScientificProjects.Projects import Project
from ScientificProjects.Teams import Team
from ScientificProjects.Roles import RoleType, Role


class ProjectsManager(object):
    def __init__(self, db_name='/:memory:', backend='sqlite',
                 hostname='', port='', user='', password='',
                 overwrite=False):
        # postgresql://scott:tiger@localhost:5432/mydatabase
        credentials = user + ':' + password if password else user
        if credentials:
            credentials += '@'
        if port:
            hostname += ':' + str(port)
        self.engine = create_engine(backend + '://' + credentials + hostname + '/' + db_name)
        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()
        self.metadata = Base.metadata
        self.create_tables(overwrite)
        self.user = None
        self.current_project = None

    def create_tables(self, overwrite=False):
        if overwrite:
            self.metadata.drop_all(self.engine)
        self.metadata.create_all(self.engine)
        self.register_basic_role_types()

    def register_basic_role_types(self):
        self.create_role_type(title='Project manager', description='Manager of the project')
        self.create_role_type(title='Team manager', description='Manager of the team')

    def create_role_type(self, title, description=None):
        role = RoleType(title=str(title), description=str(description))
        try:
            self.session.add(role)
            self.session.commit()
            return role
        except IntegrityError:
            self.session.rollback()
            return self.session.query(RoleType).filter(RoleType.title == str(title)).one()

    def create_user(self, name_first, name_last, email, login, password):
        user = User(name_first=str(name_first), name_last=str(name_last),
                    email=str(email), login=str(login), password=str(password))
        try:
            self.session.add(user)
            self.session.commit()
            print('User %s successfully created' % user.login)
            return user
        except IntegrityError as e:
            print('User with provided login/email is already registered')
            self.session.rollback()
            return self.session.query(User).filter(User.login == str(login)).one()

    def sign_in(self, login, password):
        user = self.session.query(User).filter(User.login == str(login)).all()
        if user:
            user = user[0]
            if user.password == str(password):
                self.user = user
                print('Welcome back, %s %s' % (user.name_first, user.name_last))
            else:
                print('Incorrect username/password')
        else:
            print('Incorrect username/password')

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

    def create_team(self, name, description):
        if self.current_project in self.get_own_projects():
            team = Team(name=name, description=description)
            try:
                self.session.add(team)
                self.session.commit()
                print('Team created')
                return team
            except IntegrityError as e:
                print('Team with provided name is already registered')
                self.session.rollback()
                return self.session.query(Team).filter(Team.name == name).one()
        else:
            print('To create a new team you have to select project which you own')

    def create_role(self, team, title, description, user, role_type, manager=None):
        if isinstance(role_type, str):
            role_type_title = role_type
            role_type = self.session.query(RoleType).filter(RoleType.title == role_type).one()
            if not role_type:
                role_type = self.create_role_type(title=role_type_title)
        elif isinstance(role_type, RoleType):
            if role_type not in self.session.query(RoleType).all():
                role_type = self.create_role_type(title=role_type.title, description=role_type.description)
        else:
            raise ValueError('bad role type provided')
        if isinstance(manager, Role):
            manager_id = manager.id
        else:
            manager_id = None
        role = Role(title=title, description=description, role_type=role_type,
                    team=team, user=user, manager_id=manager_id)
        self.session.add(role)
        self.session.commit()
