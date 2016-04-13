from __future__ import division, print_function

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from ScientificProjects import Base
from ScientificProjects.Entities.Log import LogCategory, Log
from ScientificProjects.Entities.Role import RoleType, Role
from ScientificProjects.Entities.Team import Team
from ScientificProjects.EntityManagers.ProjectManager import ProjectManager
from ScientificProjects.EntityManagers.UserManager import UserManager


class SessionManager(object):

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
        self.user_manager = UserManager(self.engine)
        self.project_manager = ProjectManager(self.engine)

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
