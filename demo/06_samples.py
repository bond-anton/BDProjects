from __future__ import division, print_function

from BDProjects.Client import Client

client = Client(config_file_name='config.ini')

client.user_manager.sign_in('john_smith', 'secret_password')

project_name = 'Super Project'
project = client.user_manager.project_manager.open_project(project_name)
print(project)

my_sample = client.user_manager.sample_manager.create_sample(name='SCF343 ab',
                                                             description='My new shiny sample')
print(my_sample)

params = client.user_manager.sample_manager.get_sample_parameters(my_sample, 'Color')
if len(params) == 0:
    my_parameter = client.user_manager.parameter_manager.create_string_parameter('Color', 'Blue')
    print(my_parameter, '\n')
    client.user_manager.sample_manager.add_parameter_to_sample(my_sample, my_parameter)
elif len(params) == 1:
    print(params[0])
else:
    for param in params:
        print(param)
print(my_sample)

client.user_manager.sign_out()
