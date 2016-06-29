from __future__ import division, print_function
import numpy as np

from ScientificProjects.Client import Client

client = Client(config_file_name='config.ini')

client.user_manager.sign_in('john_smith', 'secret_password')

project_name = 'Super Project'
project = client.user_manager.project_manager.open_project(project_name)
print(project)

sample = client.user_manager.sample_manager.get_samples(name='SCF343')[0]
tool = client.user_manager.equipment_manager.get_equipment(name='Super setup')[0]
measurement_type = client.user_manager.measurement_type_manager.get_measurement_types('IV measurement')[0]

measurement = client.user_manager.measurement_manager.get_measurements(name='Test IV measurement')
if measurement:
    measurement = measurement[0]
else:
    measurement = client.user_manager.measurement_manager.create_measurement(name='Test IV measurement',
                                                                             measurement_type=measurement_type,
                                                                             equipment=tool,
                                                                             description='Fake measurement for testing')
client.user_manager.measurement_manager.add_sample_to_measurement(measurement, sample)
current_meter_channel = client.user_manager.measurement_manager.create_data_channel(name='Current channel',
                                                                                    measurement=measurement,
                                                                                    description='Current meter channel',
                                                                                    unit_name='A')
voltmeter_channel = client.user_manager.measurement_manager.create_data_channel(name='Voltage channel',
                                                                                measurement=measurement,
                                                                                description='Voltmeter channel',
                                                                                unit_name='V')
print(measurement)

current_points = np.linspace(-1, 1, num=11, endpoint=True)
index = range(current_points.size)
resistance = 10
voltage_points = resistance * np.copy(current_points)

print('Measurement progress:', measurement.progress)
if measurement.finished is None:
    client.user_manager.measurement_manager.create_data_points(channel=current_meter_channel,
                                                               float_value=current_points,
                                                               point_index=index)
    client.user_manager.measurement_manager.create_data_points(channel=voltmeter_channel,
                                                               float_value=voltage_points,
                                                               point_index=index)
    client.user_manager.measurement_manager.update_measurement_progress(measurement=measurement,
                                                                        progress=100)
    client.user_manager.measurement_manager.finish_measurement(measurement=measurement)
print('Measurement finished:', measurement.finished)

i_data = client.user_manager.measurement_manager.get_data_points_array(channel=current_meter_channel)
v_data = client.user_manager.measurement_manager.get_data_points_array(channel=voltmeter_channel)
print(i_data[:, 0])
print(v_data)


client.user_manager.measurement_manager.delete_measurement(measurement)
#client.user_manager.measurement_manager.delete_data_points(channel=voltmeter_channel,
#                                                           point_index=index[:5])

dp = client.user_manager.parameter_manager.get_dangling_parameters(delete=True)

client.user_manager.sign_out()

#client.user_manager.delete_user('john_smith', 'secret_password')
