from __future__ import division, print_function
import numpy as np
import time

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from ScientificProjects.Client import Client


config = configparser.ConfigParser()
config.read('config.ini')
db_config = config['Database']

db_name = db_config['name']
backend = db_config['backend']
hostname = db_config['host']
port = db_config['port']
user = db_config['user']
password = db_config['password']

client = Client(db_name=db_name, backend=backend, hostname=hostname, port=port,
                user=user, password=password)
client.user_manager.create_user('John', 'Smith', 'john.smith@somecorp.com', 'john_smith', 'secret_password')
client.user_manager.sign_in('john_smith', 'secret_password')
client.user_manager.create_user('Jack', 'Black', 'jack.black@somecorp.com', 'jack_black', 'secret_password')
client.log_opened_sessions()
time.sleep(3)
client.log_signed_in_users()
client.logoff_all()

project_name = 'Super Project'
client.user_manager.project_manager.create_project(project_name, 'My first ever really super project', 'data/files')
client.user_manager.project_manager.open_project(project_name)
client.user_manager.sign_in('john_smith', 'secret_password')
client.user_manager.project_manager.create_project(project_name, 'My first ever really super project', 'data/files')
client.user_manager.project_manager.open_project(project_name)
client.user_manager.parameter_manager.create_parameter('test parameter', 'Numeric value', np.pi, index=0, unit_name='m')
print(client.user_manager.parameter_manager.get_parameter_types())
client.logoff_all()
client.close_all_projects()
client.user_manager.project_manager.open_project(project_name)
client.user_manager.parameter_manager.create_parameter('test parameter', 'Numeric value', 2 * np.pi, index=0,
                                                       unit_name='m')
client.user_manager.sign_out()

