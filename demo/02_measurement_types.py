from __future__ import division, print_function
import pprint

from ScientificProjects.Client import Client

client = Client(config_file_name='config.ini')

client.user_manager.sign_in('john_smith', 'secret_password')
client.user_manager.measurement_type_manager.create_measurement_type('Length measurement',
                                                                     description='Measurement of length')
client.user_manager.measurement_type_manager.create_measurement_type('Electrical measurement',
                                                                     description='Measurement of electrical values')
client.user_manager.measurement_type_manager.create_measurement_type('Resistance measurement',
                                                                     description='Measurement of electrical resistance',
                                                                     parent='Electrical measurement')
client.user_manager.measurement_type_manager.create_measurement_type('Current measurement',
                                                                     description='Measurement of electrical current',
                                                                     parent='Electrical measurement')
client.user_manager.measurement_type_manager.create_measurement_type('Voltage measurement',
                                                                     description='Measurement of electrical voltage',
                                                                     parent='Electrical measurement')
client.user_manager.measurement_type_manager.create_measurement_type('Current transient measurement',
                                                                     description='Measurement of electrical current',
                                                                     parent='Current measurement')
client.user_manager.measurement_type_manager.create_measurement_type('IV measurement',
                                                                     description='Measurement of electrical current',
                                                                     parent='Current measurement')

meas_types = client.user_manager.measurement_type_manager.get_measurement_types()
pprint.pprint(meas_types)


client.user_manager.sign_out()
