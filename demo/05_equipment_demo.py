from __future__ import division, print_function

from ScientificProjects.Client import Client
from ScientificProjects.EntityManagers.ParameterManager import get_range_parameter_value

client = Client(config_file_name='config.ini')

client.user_manager.sign_in('john_smith', 'secret_password')

my_manufacturer = client.user_manager.equipment_manager.create_manufacturer(name='Advanced Instrumentation Company',
                                                                            name_short='AIC',
                                                                            description='Test manufacturer')
print(my_manufacturer)

manufacturers = client.user_manager.equipment_manager.get_manufacturers(name='aic')
print(manufacturers)

category = client.user_manager.equipment_manager.create_equipment_category(name='Software',
                                                                           description='Software tools',
                                                                           parent=None)
print(category)

category_tree = client.user_manager.equipment_manager.get_equipment_categories_tree()
print(category_tree)


my_tool_1 = client.user_manager.equipment_manager.create_equipment(name='MST-01',
                                                                   category=category,
                                                                   manufacturer=my_manufacturer,
                                                                   serial_number='AAA 56-789-FR',
                                                                   assembly=None,
                                                                   description='My super duper tool')
print(my_tool_1)

my_tool_2 = client.user_manager.equipment_manager.create_equipment(name='Integrator',
                                                                   category=category,
                                                                   manufacturer=my_manufacturer,
                                                                   serial_number=None,
                                                                   assembly=None,
                                                                   description='My super duper integrator')
print(my_tool_2)


my_assembly = client.user_manager.equipment_manager.create_equipment_assembly(name='Advanced pipeline',
                                                                              description='Nice software combination')
client.user_manager.equipment_manager.add_equipment_to_assembly(my_assembly, my_tool_1)
client.user_manager.equipment_manager.add_equipment_to_assembly(my_assembly, my_tool_2)
print(my_assembly)

my_tool_3 = client.user_manager.equipment_manager.create_equipment(name='Super setup',
                                                                   category=category,
                                                                   manufacturer=None,
                                                                   serial_number=None,
                                                                   assembly=my_assembly,
                                                                   description='My super experimental setup')
print(my_tool_3)
measurement_type = client.user_manager.measurement_type_manager.get_measurement_types('IV measurement')[0]
client.user_manager.equipment_manager.add_measurement_type_to_equipment(my_tool_3, measurement_type)
print(my_tool_3)

params = client.user_manager.equipment_manager.get_equipment_parameter_by_name(my_tool_3, 'Voltage range')
print(params)
#my_parameter = client.user_manager.parameter_manager.create_numeric_range_parameter('Voltage range', -1, 5)
#print(my_parameter, '\n')
#print(get_range_parameter_value(my_parameter), '\n')
#client.user_manager.equipment_manager.add_parameter_to_equipment(my_tool_3, my_parameter)
#print(my_tool_3)

client.user_manager.sign_out()
