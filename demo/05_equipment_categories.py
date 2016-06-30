from __future__ import division, print_function

from ScientificProjects.Client import Client
from ScientificProjects.EntityManagers.ParameterManager import get_range_parameter_value

client = Client(config_file_name='config.ini')

client.user_manager.sign_in('john_smith', 'secret_password')

category = client.user_manager.equipment_manager.create_equipment_category(name='Software',
                                                                           description='Software tools',
                                                                           parent=None)
print(category)

category_tree = client.user_manager.equipment_manager.get_equipment_categories_tree()
print(category_tree)

client.user_manager.sign_out()
