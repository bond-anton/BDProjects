from __future__ import division, print_function
from ScientificProjects.SessionManager import SessionManager

sm = SessionManager('data/test.db')
sm.user_manager.create_user('John', 'Smith', 'john.smith@somecorp.com', 'john_smith', 'secret_password')
sm.user_manager.sign_in('john_smith', 'secret_password')
for logged_in_user in sm.user_manager.signed_in_users():
    print('\t', logged_in_user)
sm.user_manager.logoff_all()
# print(sm.user_manager.signed_in_users())

project_name = 'Super Project'
sm.project_manager.create_project(project_name, 'My first ever really super project', 'data/files')
sm.project_manager.open_project(project_name)
sm.user_manager.sign_in('john_smith', 'secret_password')
sm.project_manager.create_project(project_name, 'My first ever really super project', 'data/files')
sm.project_manager.open_project(project_name)
sm.user_manager.sign_out()

'''
my_projects = pm.get_own_projects()
if my_projects:
    print('I have %d project(s):' % len(my_projects))
    for project in my_projects:
        print('  ' + project.name)

pm.create_team('ResearchLab 1', 'ResearchLab #1 from XXX State University')
'''
