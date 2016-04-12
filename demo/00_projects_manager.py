from __future__ import division, print_function
from ScientificProjects.Manager import ProjectsManager

pm = ProjectsManager('data/test.db')
pm.create_user('John', 'Smith', 'john.smith@somecorp.com', 'john_smith', 'secret_password')
pm.sign_in('john_smith', 'secret_password')

project_name = 'Super Project'
pm.create_project(project_name, 'My first ever really super project', 'data/files')

my_projects = pm.get_own_projects()
if my_projects:
    print('I have %d project(s):' % len(my_projects))
    for project in my_projects:
        print('  ' + project.name)

pm.open_project(project_name)
pm.create_team('ResearchLab 1', 'ResearchLab #1 from XXX State University')
