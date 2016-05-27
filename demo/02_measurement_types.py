from __future__ import division, print_function
import time

from ScientificProjects.Client import Client

client = Client(config_file_name='config.ini')

client.user_manager.sign_in('john_smith', 'secret_password')
client.user_manager.measurement_type_manager.create_measurement_type('Length measurement',
                                                                     description='Measurement of length')
client.user_manager.sign_out()
