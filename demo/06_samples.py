from __future__ import division, print_function

from ScientificProjects.Client import Client
from ScientificProjects.EntityManagers.ParameterManager import get_range_parameter_value

client = Client(config_file_name='config.ini')

client.user_manager.sign_in('john_smith', 'secret_password')

project_name = 'Super Project'
client.user_manager.project_manager.open_project(project_name)

ans = client.user_manager.project_manager.project_opened()
if ans:
    print(client.user_manager.project_manager.project)

client.user_manager.sign_out()
