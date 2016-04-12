from __future__ import division, print_function
from ScientificProjects.Manager import ProjectsManager

pm = ProjectsManager('data/test.db')
pm.add_user('John', 'Smith', 'john.smith@somecorp.com', 'john_smith', 'secret_password')
pm.sign_in('john_smith', 'secret_password')
pm.sign_in('john_smith', 'secret_password_wrong')
pm.sign_in('john_black', 'secret_password')
pm.sign_in('john_smith', 'secret_password')
pm.create_project('Super Project', 'My first ever really super project', 'data/files')
my_projects = pm.get_own_projects()
if my_projects:
    print('I have %d project(s)' % len(my_projects))
    for project in my_projects:
        print('  ' + project.name)
    pm.open_project(my_projects[0])
print(pm.get_current_project_teams())
