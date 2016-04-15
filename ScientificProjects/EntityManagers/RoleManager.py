from ScientificProjects.Entities.Role import RoleType, Role


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