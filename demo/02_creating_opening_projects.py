from __future__ import division, print_function

from ScientificProjects.Client import Client

client = Client(config_file_name='config.ini')

client.user_manager.sign_in('john_smith', 'secret_password')

project_name = 'Super Project'
client.user_manager.project_manager.create_project(name=project_name,
                                                   description='My first ever really super project',
                                                   data_dir='data/files')
client.user_manager.project_manager.open_project(project_name)
client.user_manager.project_manager.close_project()

client.user_manager.sign_out()

client.user_manager.sign_in('john_smith', 'secret_password')
client.user_manager.project_manager.open_project(project_name)
client.user_manager.project_manager.open_project(project_name)
client.user_manager.sign_out()
# client.user_manager.delete_user('john_smith', 'secret_password')
# client.user_manager.create_user('John', 'Smith', 'john.smith@somecorp.com', 'john_smith', 'secret_password')
