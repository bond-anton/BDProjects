from __future__ import division, print_function
import datetime as dt
import timeit
import numpy as np

from sqlalchemy.exc import IntegrityError

from BDProjects.Entities import MeasurementType
from BDProjects.Entities import Measurement, MeasurementsCollection
from BDProjects.Entities import DataChannel, DataPoint
from BDProjects.Entities import Equipment
from BDProjects.Entities import Sample
from BDProjects.Entities import Parameter
from BDProjects.EntityManagers import EntityManager


class MeasurementManager(EntityManager):

    def __init__(self, engine, session_manager):
        super(MeasurementManager, self).__init__(engine, session_manager)

    def create_measurement(self, name, measurement_type, equipment, description=None):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                project = self.session_manager.project_manager.project
                measurement = Measurement(name=str(name))
                measurement.project_id = project.id
                measurement.session_id = self.session_manager.session_data.id
                if description is not None:
                    measurement.description = str(description)
                if isinstance(measurement_type, MeasurementType):
                    measurement.measurement_type_id = measurement_type.id
                else:
                    measurement_types = self.session_manager.measurement_type_manager.get_measurement_types(
                        measurement_type)
                    if len(measurement_types) == 1:
                        measurement.measurement_type_id = measurement_types[0].id
                        measurement_type = measurement_types[0]
                    elif len(measurement_types) == 0:
                        record = 'No measurement type found for keyword "%s"' % measurement_type
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                        return None
                    else:
                        record = 'More than one measurement type found for keyword "%s"' % measurement_type
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                        return None
                if isinstance(equipment, Equipment):
                    measurement.equipment_id = equipment.id
                else:
                    equipment_list = self.session_manager.equipment_manager.get_equipment(equipment)
                    if len(equipment_list) == 1:
                        measurement.equipment_id = equipment_list[0].id
                        equipment = equipment_list[0]
                    elif len(equipment_list) == 0:
                        record = 'No equipment found for keyword "%s"' % equipment
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                        return None
                    else:
                        record = 'More than one equipment item found for keyword "%s"' % equipment
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                        return None
                if measurement_type not in equipment.measurement_types:
                    record = 'Equipment "%s" does not support measurement type "%s"' % \
                             (measurement.equipment.name, measurement.measurement_type.name)
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return None
                self.session.add(measurement)
                self.session.commit()
                record = 'Measurement "%s" created' % measurement.name
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return measurement
            else:
                record = 'Attempt to create measurement before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return None
        else:
            record = 'Attempt to create measurement before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None

    def delete_measurement(self, measurement):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if not isinstance(measurement, Measurement):
                    record = 'Expected valid Measurement object for delete operation'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
                self.session.delete(measurement)
                self.session.commit()
                record = 'Measurement "%s" successfully deleted' % measurement.name
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return True
            else:
                record = 'Attempt to delete measurement before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to delete measurement before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def add_sample_to_measurement(self, measurement, sample):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurement, Measurement) and isinstance(sample, Sample):
                    try:
                        measurement.samples.append(sample)
                        self.session.commit()
                        record = 'Sample "%s" added to measurement "%s"' % (sample.name,
                                                                            measurement.name)
                        self.session_manager.log_manager.log_record(record=record, category='Information')
                    except IntegrityError:
                        self.session.rollback()
                        record = 'Sample "%s" already added to measurement "%s"' % (sample.name, measurement.name)
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return True
                else:
                    record = 'Wrong argument for adding sample to measurement'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
            else:
                record = 'Attempt to add sample to measurement before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to add sample to measurement before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def remove_sample_from_measurement(self, measurement, sample):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurement, Measurement) and isinstance(sample, Sample):
                    if sample in measurement.samples:
                        measurement.samples.remove(sample)
                        self.session.commit()
                        record = 'Sample "%s" removed from measurement "%s"' % (sample.name, measurement.name)
                        self.session_manager.log_manager.log_record(record=record, category='Information')
                    else:
                        record = 'Sample "%s" not found in measurement "%s"' % (sample.name, measurement.name)
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return True
                else:
                    record = 'Wrong argument for removing sample from measurement'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
            else:
                record = 'Attempt to remove sample from measurement before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to remove sample from measurement before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def add_parameter_to_measurement(self, measurement, parameter):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurement, Measurement) and isinstance(parameter, Parameter):
                    try:
                        measurement.parameters.append(parameter)
                        self.session.commit()
                        record = 'Parameter "%s" added to measurement "%s"' % (parameter.name,
                                                                               measurement.name)
                        self.session_manager.log_manager.log_record(record=record, category='Information')
                    except IntegrityError:
                        self.session.rollback()
                        record = 'Parameter "%s" already added to measurement "%s"' % (parameter.name, measurement.name)
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return True
                else:
                    record = 'Wrong argument for adding parameter to measurement'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
            else:
                record = 'Attempt to add parameter to measurement before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to add parameter to measurement before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def remove_parameter_from_measurement(self, measurement, parameter):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurement, Measurement) and isinstance(parameter, Parameter):
                    if parameter in measurement.parameters:
                        measurement.parameters.remove(parameter)
                        self.session.commit()
                        record = 'Parameter "%s" removed from measurement "%s"' % (parameter.name, measurement.name)
                        self.session_manager.log_manager.log_record(record=record, category='Information')
                    else:
                        record = 'Parameter "%s" not found in measurement "%s"' % (parameter.name, measurement.name)
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return True
                else:
                    record = 'Wrong argument for removing parameter from measurement'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
            else:
                record = 'Attempt to remove parameter from measurement before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to remove parameter from measurement before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def create_collection(self, name, description=None):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                project = self.session_manager.project_manager.project
                measurements_collection = MeasurementsCollection(name=str(name))
                measurements_collection.project_id = project.id
                measurements_collection.session_id = self.session_manager.session_data.id
                if description is not None:
                    measurements_collection.description = str(description)
                try:
                    self.session.add(measurements_collection)
                    self.session.commit()
                    record = 'Measurements collection "%s" created' % measurements_collection.name
                    self.session_manager.log_manager.log_record(record=record, category='Information')
                except IntegrityError:
                    self.session.rollback()
                    q = self.session.query(MeasurementsCollection).filter(MeasurementsCollection.name == str(name))
                    q = q.filter(MeasurementsCollection.project_id == project.id)
                    measurements_collection = q.all()[0]
                    record = 'Measurements collection "%s" already exist' % measurements_collection.name
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                return measurements_collection
            else:
                record = 'Attempt to create measurements collection before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return None
        else:
            record = 'Attempt to create measurements collection before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None

    def delete_collection(self, collection):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if not isinstance(collection, MeasurementsCollection):
                    record = 'Expected valid MeasurementCollection object for delete operation'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
                self.session.delete(collection)
                self.session.commit()
                record = 'Measurement collection "%s" successfully deleted' % collection.name
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return True
            else:
                record = 'Attempt to delete measurement collection before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to delete measurement collection before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def add_measurement_to_collection(self, measurements_collection, measurement):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurements_collection, MeasurementsCollection) and isinstance(measurement, Measurement):
                    try:
                        measurements_collection.measurements.append(measurement)
                        self.session.commit()
                        record = 'Measurement "%s" added to collection "%s"' % (measurement.name,
                                                                                measurements_collection.name)
                        self.session_manager.log_manager.log_record(record=record, category='Information')
                    except IntegrityError:
                        self.session.rollback()
                        record = 'Measurement "%s" already added to collection "%s"' % (measurement.name,
                                                                                        measurements_collection.name)
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return True
                else:
                    record = 'Wrong argument for adding measurement to collection'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
            else:
                record = 'Attempt to add measurement to collection before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to add measurement to collection before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def remove_measurement_from_collection(self, measurements_collection, measurement):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurements_collection, MeasurementsCollection) and isinstance(measurement, Measurement):
                    if measurement in measurements_collection.measurements:
                        measurements_collection.measurements.remove(measurement)
                        self.session.commit()
                        record = 'Measurement "%s" removed from collection "%s"' % (measurement.name,
                                                                                    measurements_collection.name)
                        self.session_manager.log_manager.log_record(record=record, category='Information')
                        return True
                    else:
                        record = 'Measurement "%s" not found in collection "%s"' % (measurement.name,
                                                                                    measurements_collection.name)
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                        return False
                else:
                    record = 'Wrong argument for removing measurement from collection'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
            else:
                record = 'Attempt to remove measurement from collection before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to remove measurement from collection before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def add_input_data_to_measurement(self, measurement, measurements_collection):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurement, Measurement) and isinstance(measurements_collection, MeasurementsCollection):
                    try:
                        measurement.input_data_id = measurements_collection.id
                        self.session.commit()
                        record = 'Input data "%s" added to measurement "%s"' % (measurements_collection.name,
                                                                                measurement.name)
                        self.session_manager.log_manager.log_record(record=record, category='Information')
                    except IntegrityError:
                        self.session.rollback()
                        record = 'Input data "%s" already added to measurement "%s"' % (measurements_collection.name,
                                                                                        measurement.name)
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return True
                else:
                    record = 'Wrong argument for adding input data to measurement'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
            else:
                record = 'Attempt to add input data to measurement before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to add input data to measurement before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def remove_input_data_from_measurement(self, measurement, measurements_collection):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurement, Measurement) and isinstance(measurements_collection, MeasurementsCollection):
                    if measurements_collection in measurement.parameters:
                        measurement.parameters.remove(measurements_collection)
                        self.session.commit()
                        record = 'Collection "%s" removed from measurement "%s"' % (measurements_collection.name,
                                                                                    measurement.name)
                        self.session_manager.log_manager.log_record(record=record, category='Information')
                    else:
                        record = 'Collection "%s" not found in measurement "%s"' % (measurements_collection.name,
                                                                                    measurement.name)
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return True
                else:
                    record = 'Wrong argument for removing collection from measurement'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
            else:
                record = 'Attempt to remove collection from measurement before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to remove collection from measurement before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def get_measurements(self, name=None):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                project = self.session_manager.project_manager.project
                q = self.session.query(Measurement).filter(Measurement.project_id == project.id)
                if name is not None and len(str(name)) > 2:
                    template = '%' + str(name) + '%'
                    q = q.filter(Measurement.name.ilike(template))
                return q.all()
            else:
                record = 'Attempt to query measurements before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return []
        else:
            record = 'Attempt to query measurements before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return []

    def get_collection(self, name=None):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                project = self.session_manager.project_manager.project
                q = self.session.query(MeasurementsCollection).filter(MeasurementsCollection.project_id == project.id)
                if name is not None and len(str(name)) > 2:
                    template = '%' + str(name) + '%'
                    q = q.filter(MeasurementsCollection.name.ilike(template))
                return q.all()
            else:
                record = 'Attempt to query measurements collections before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return []
        else:
            record = 'Attempt to query measurements collections before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return []

    def create_data_channel(self, name, measurement, description=None, unit_name=None):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                data_channel = DataChannel(name=str(name))
                data_channel.session_id = self.session_manager.session_data.id
                if isinstance(measurement, Measurement):
                    data_channel.measurement_id = measurement.id
                else:
                    record = 'Not valid Measurement object to create data channel'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return None
                if description is not None:
                    data_channel.description = str(description)
                if unit_name is not None:
                    data_channel.unit_name = str(unit_name)
                try:
                    self.session.add(data_channel)
                    self.session.commit()
                    record = 'Data channel "%s" created' % data_channel.name
                    self.session_manager.log_manager.log_record(record=record, category='Information')
                except IntegrityError:
                    self.session.rollback()
                    q = self.session.query(DataChannel).filter(DataChannel.name == str(name))
                    q = q.filter(DataChannel.measurement_id == measurement.id)
                    data_channel = q.all()[0]
                    record = 'Data channel "%s" already exists' % data_channel.name
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                return data_channel
            else:
                record = 'Attempt to create data channel before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return None
        else:
            record = 'Attempt to create data channel before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None

    def delete_data_channel(self, data_channel):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if not isinstance(data_channel, DataChannel):
                    record = 'Expected valid DataChannel object for delete operation'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
                self.session.delete(data_channel)
                self.session.commit()
                record = 'Data channel "%s" successfully deleted' % data_channel.name
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return True
            else:
                record = 'Attempt to delete data channel before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to delete data channel before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def add_parameter_to_data_channel(self, data_channel, parameter):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(data_channel, DataChannel) and isinstance(parameter, Parameter):
                    try:
                        data_channel.parameters.append(parameter)
                        self.session.commit()
                        record = 'Parameter "%s" added to data channel "%s"' % (parameter.name,
                                                                                data_channel.name)
                        self.session_manager.log_manager.log_record(record=record, category='Information')
                    except IntegrityError:
                        self.session.rollback()
                        record = 'Parameter "%s" already added to data channel "%s"' % (parameter.name,
                                                                                        data_channel.name)
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return True
                else:
                    record = 'Wrong argument for adding parameter to data channel'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
            else:
                record = 'Attempt to add parameter to data channel before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to add parameter to data channel before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def remove_parameter_from_data_channel(self, data_channel, parameter):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(data_channel, DataChannel) and isinstance(parameter, Parameter):
                    if parameter in data_channel.parameters:
                        data_channel.parameters.remove(parameter)
                        self.session.commit()
                        record = 'Parameter "%s" removed from data channel "%s"' % (parameter.name, data_channel.name)
                        self.session_manager.log_manager.log_record(record=record, category='Information')
                    else:
                        record = 'Parameter "%s" not found in data channel "%s"' % (parameter.name, data_channel.name)
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return True
                else:
                    record = 'Wrong argument for removing parameter from data channel'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
            else:
                record = 'Attempt to remove parameter from data channel before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to remove parameter from data channel before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def get_data_channels(self, measurement, name=None, exact=False):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurement, Measurement):
                    q = self.session.query(DataChannel).filter(DataChannel.measurement_id == measurement.id)
                    if name is not None and len(str(name)) > 2:
                        if exact:
                            q = q.filter(DataChannel.name == str(name))
                        else:
                            template = '%' + str(name) + '%'
                            q = q.filter(DataChannel.name.ilike(template))
                    return q.all()
                else:
                    record = 'Wrong Measurement object to query data channels'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return []
            else:
                record = 'Attempt to query data channel before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return []
        else:
            record = 'Attempt to query data channel before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return []

    def create_data_point(self, channel, string_value=None, float_value=None, point_index=None, measured=None):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if string_value is None and float_value is None:
                    record = 'Either string or float value is needed to create data point'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return None
                if not isinstance(channel, DataChannel):
                    record = 'Wrong DataChannel object to create data point'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return None
                data_point = DataPoint()
                data_point.channel_id = channel.id
                data_point.session_id = self.session_manager.session_data.id
                if string_value is not None:
                    data_point.string_value = str(string_value)
                if float_value is not None:
                    data_point.float_value = float(float_value)
                if point_index is not None:
                    data_point.point_index = int(abs(point_index))
                if isinstance(measured, dt.datetime):
                    data_point.measured = measured
                self.session.add(data_point)
                self.session.commit()
                record = 'Data point added to channel "%s"' % channel.name
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return data_point
            else:
                record = 'Attempt to create data point before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return None
        else:
            record = 'Attempt to create data point before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None

    def delete_data_point(self, data_point):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if not isinstance(data_point, DataPoint):
                    record = 'Expected valid DataPoint object for delete operation'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
                self.session.delete(data_point)
                self.session.commit()
                record = 'Data point successfully deleted'
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return True
            else:
                record = 'Attempt to delete data point before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to delete data point before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def create_data_points(self, channel, string_value=None, float_value=None, point_index=None, measured=None):
        start_time = timeit.default_timer()
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if string_value is None and float_value is None:
                    record = 'Either string or float value is needed to create data point'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return None
                if not isinstance(channel, DataChannel):
                    record = 'Wrong DataChannel object to create data point'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return None
                if string_value is None:
                    string_value = np.array([None] * float_value.size)
                elif float_value is None:
                    float_value = np.array([None] * string_value.size)
                if point_index is None:
                    point_index = np.zeros(float_value.size, dtype=np.int)
                if measured is None:
                    measured = np.array([dt.datetime.now()] * float_value.size)
                data_points = [{'channel_id': channel.id,
                                'string_value': string_value[i],
                                'float_value': float_value[i],
                                'point_index': int(point_index[i]),
                                'point_measured': measured[i],
                                'session_id': self.session_manager.session_data.id,
                                } for i in range(float_value.size)]
                self.engine.execute(DataPoint.__table__.insert(), data_points)
                elapsed = timeit.default_timer() - start_time
                record = '%i data points added to channel "%s" in %3.3f s' % (len(data_points), channel.name, elapsed)
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return data_points
            else:
                record = 'Attempt to create data point before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return None
        else:
            record = 'Attempt to create data point before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None

    def delete_data_points(self, channel, point_index=None):
        start_time = timeit.default_timer()
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if not isinstance(channel, DataChannel):
                    record = 'Expected valid DataChannel object for data points delete operation'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
                q = self.session.query(DataPoint).filter(DataPoint.channel_id == channel.id)
                if point_index is not None:
                    q = q.filter(DataPoint.point_index.in_(point_index))
                count = q.delete(synchronize_session='fetch')
                # count = q.delete(synchronize_session=False) # try this if performance is low
                self.session.commit()
                elapsed = timeit.default_timer() - start_time
                record = '%i data points deleted from channel "%s" in %3.3f s' % (count, channel.name, elapsed)
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return True
            else:
                record = 'Attempt to delete data points before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to delete data points before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def get_data_points_num(self, channel):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if not isinstance(channel, DataChannel):
                    record = 'Wrong DataChannel object to query data points num'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return None
                return self.session.query(DataPoint).filter(DataPoint.channel_id == channel.id).count()
            else:
                record = 'Attempt to query data point before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return []
        else:
            record = 'Attempt to query data point before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return []

    def get_data_points(self, channel, point_index=None):
        start_time = timeit.default_timer()
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if not isinstance(channel, DataChannel):
                    record = 'Wrong DataChannel object to query data point'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return []
                q = self.session.query(DataPoint).filter(DataPoint.channel_id == channel.id)
                if point_index is not None:
                    q = q.filter(DataPoint.point_index.in_(point_index))
                result = q.all()
                elapsed = timeit.default_timer() - start_time
                record = '%i data points pooled from channel "%s" in %3.3f s' % (len(result), channel.name, elapsed)
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return result
            else:
                record = 'Attempt to query data point before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return []
        else:
            record = 'Attempt to query data point before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return []

    def get_data_points_array(self, channel, point_index=None):
        start_time = timeit.default_timer()
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if not isinstance(channel, DataChannel):
                    record = 'Wrong DataChannel object to query data point'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return np.array([[None, None, None, None]])
                q = self.session.query(DataPoint.float_value,
                                       DataPoint.string_value,
                                       DataPoint.point_index,
                                       DataPoint.measured).filter(DataPoint.channel_id == channel.id)
                if point_index is not None:
                    q = q.filter(DataPoint.point_index.in_(point_index))
                result = np.array(q.all())
                if result.size == 0:
                    result = np.array([[None, None, None, None]])
                elapsed = timeit.default_timer() - start_time
                record = '%i data points pooled from channel "%s" in %3.3f s' % (len(result), channel.name, elapsed)
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return result
            else:
                record = 'Attempt to query data point before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return np.array([[None, None, None, None]])
        else:
            record = 'Attempt to query data point before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return np.array([[None, None, None, None]])

    def finish_measurement(self, measurement, finished=None):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if not isinstance(measurement, Measurement):
                    record = 'Expected valid Measurement object for measurement finish'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
                if finished is None:
                    finished = dt.datetime.now()
                elif not isinstance(finished, dt.datetime):
                    record = 'Expected datetime argument for measurement finish'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
                measurement.finished = finished
                self.session.commit()
                return True
            else:
                record = 'Attempt to finish measurement before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to finish measurement before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def update_measurement_progress(self, measurement, progress):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if not isinstance(measurement, Measurement):
                    record = 'Expected valid Measurement object for progress update'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
                measurement.progress = float(progress)
                self.session.commit()
                return True
            else:
                record = 'Attempt to update measurement progress before opening project'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to update measurement progress before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False
