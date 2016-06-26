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
print(my_assembly)

client.user_manager.sign_out()
