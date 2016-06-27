from __future__ import division, print_function

from sqlalchemy.exc import IntegrityError

from ScientificProjects.Entities.MeasurementType import MeasurementType
from ScientificProjects.Entities.Measurement import Measurement, MeasurementsCollection
from ScientificProjects.Entities.DataPoint import DataChannel
from ScientificProjects.Entities.Equipment import Equipment
from ScientificProjects.Entities.Sample import Sample
from ScientificProjects.Entities.Parameter import Parameter
from ScientificProjects.EntityManagers import EntityManager


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
                    elif len(equipment_list) == 0:
                        record = 'No equipment found for keyword "%s"' % equipment
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                        return None
                    else:
                        record = 'More than one equipment item found for keyword "%s"' % equipment
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                        return None
                if measurement.measurement_type not in measurement.equipment.measurement_types:
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

    def add_sample_to_measurement(self, measurement, sample):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurement, Measurement) and isinstance(sample, Sample):
                    measurement.samples.append(sample)
                    self.session.commit()
                    record = 'sample "%s" added to measurement "%s"' % (sample.name,
                                                                        measurement.name)
                    self.session_manager.log_manager.log_record(record=record, category='Information')
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

    def add_parameter_to_measurement(self, measurement, parameter):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurement, Measurement) and isinstance(parameter, Parameter):
                    measurement.parameters.append(parameter)
                    self.session.commit()
                    record = 'Parameter "%s" added to measurement "%s"' % (parameter.name,
                                                                           measurement.name)
                    self.session_manager.log_manager.log_record(record=record, category='Information')
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

    def add_measurement_to_collection(self, measurements_collection, measurement):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurements_collection, MeasurementsCollection) and isinstance(measurement, Measurement):
                    measurements_collection.measurements.append(measurement)
                    self.session.commit()
                    record = 'Measurement "%s" added to collection "%s"' % (measurement.name,
                                                                            measurements_collection.name)
                    self.session_manager.log_manager.log_record(record=record, category='Information')
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

    def add_input_data_to_measurement(self, measurement, measurements_collection):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurement, Measurement) and isinstance(measurements_collection, MeasurementsCollection):
                    measurement.input_data_id = measurements_collection.id
                    self.session.commit()
                    record = 'Input data "%s" added to Measurement "%s"' % (measurements_collection.name,
                                                                            measurement.name)
                    self.session_manager.log_manager.log_record(record=record, category='Information')
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

    def add_parameter_to_data_channel(self, data_channel, parameter):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(data_channel, DataChannel) and isinstance(parameter, Parameter):
                    data_channel.parameters.append(parameter)
                    self.session.commit()
                    record = 'Parameter "%s" added to data channel "%s"' % (parameter.name,
                                                                            data_channel.name)
                    self.session_manager.log_manager.log_record(record=record, category='Information')
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

    def get_data_channels(self, measurement, name=None):
        if self.session_manager.signed_in():
            if self.session_manager.project_manager.project_opened():
                if isinstance(measurement, Measurement):
                    q = self.session.query(DataChannel).filter(DataChannel.measurement_id == measurement.id)
                    if name is not None and len(str(name)) > 2:
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
