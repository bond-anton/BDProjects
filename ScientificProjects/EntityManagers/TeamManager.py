from ScientificProjects.Entities.Team import Team


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