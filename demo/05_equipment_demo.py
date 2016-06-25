from __future__ import division, print_function

from ScientificProjects.Client import Client

client = Client(config_file_name='config.ini')

client.user_manager.sign_in('john_smith', 'secret_password')

my_manufacturer = client.user_manager.equipment_manager.create_manufacturer(name='Advanced Instrumentation Company',
                                                                            name_short='AIC',
                                                                            description='Test manufacturer')
print(my_manufacturer)

manufacturers = client.user_manager.equipment_manager.get_manufacturers(name='aic')
print(manufacturers)

client.user_manager.sign_out()
