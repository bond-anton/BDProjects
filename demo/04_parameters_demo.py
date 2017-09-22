from __future__ import division, print_function

import datetime as dt

from BDProjects import float_to_datetime
from BDProjects.EntityManagers.ParameterManager import get_range_parameter_value
from BDProjects.Client import Connector, Client

client = Client(Connector(config_file_name='config.ini'))

client.user_manager.sign_in('john_smith', 'secret_password')

my_parameter = client.user_manager.parameter_manager.create_numeric_parameter('secret_parameter', 2.345)
print(my_parameter, '\n')

my_parameter = client.user_manager.parameter_manager.create_string_parameter('secret_parameter', 'Parameter value')
print(my_parameter, '\n')

my_parameter = client.user_manager.parameter_manager.create_boolean_parameter('secret_parameter', True)
print(my_parameter, '\n')

my_parameter = client.user_manager.parameter_manager.create_boolean_parameter('secret_parameter', False)
print(my_parameter, '\n')

my_parameter = client.user_manager.parameter_manager.create_datetime_parameter('secret_parameter', dt.datetime.now())
print(my_parameter)
print('Decoded value: %s\n' % float_to_datetime(my_parameter.float_value), '\n')

my_parameter = client.user_manager.parameter_manager.create_numeric_range_parameter('secret_parameter', -1, 5)
print(my_parameter, '\n')
print(get_range_parameter_value(my_parameter), '\n')

my_parameter = client.user_manager.parameter_manager.create_datetime_range_parameter('secret_parameter',
                                                                                     dt.datetime.now(),
                                                                                     dt.datetime(2018, 1, 1))
print(my_parameter, '\n')
print(get_range_parameter_value(my_parameter), '\n')

client.user_manager.sign_out()
