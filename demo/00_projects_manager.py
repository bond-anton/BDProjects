from __future__ import division, print_function
import time
import numpy as np
from ScientificProjects.Client import SessionManager

sm = SessionManager('data/test.db')
sm.user_manager.create_user('John', 'Smith', 'john.smith@somecorp.com', 'john_smith', 'secret_password')
sm.user_manager.sign_in('john_smith', 'secret_password')
sm.user_manager.create_user('Jack', 'Black', 'jack.black@somecorp.com', 'jack_black', 'secret_password')
sm.log_opened_sessions()
time.sleep(3)
sm.log_signed_in_users()
sm.logoff_all()
# print(sm.user_manager.signed_in_users())

project_name = 'Super Project'
sm.user_manager.project_manager.create_project(project_name, 'My first ever really super project', 'data/files')
sm.user_manager.project_manager.open_project(project_name)
sm.user_manager.sign_in('john_smith', 'secret_password')
sm.user_manager.project_manager.create_project(project_name, 'My first ever really super project', 'data/files')
sm.user_manager.project_manager.open_project(project_name)
sm.user_manager.parameter_manager.create_parameter('test parameter', 'Numeric value', np.pi, index=0, unit_name='m')
print(sm.user_manager.parameter_manager.get_parameter_types())
sm.logoff_all()
sm.close_all_projects()
sm.user_manager.project_manager.open_project(project_name)
sm.user_manager.parameter_manager.create_parameter('test parameter', 'Numeric value', 2*np.pi, index=0, unit_name='m')
sm.user_manager.sign_out()

'''
my_projects = pm.get_own_projects()
if my_projects:
    print('I have %d project(s):' % len(my_projects))
    for project in my_projects:
        print('  ' + project.name)

pm.create_team('ResearchLab 1', 'ResearchLab #1 from XXX State University')
'''
