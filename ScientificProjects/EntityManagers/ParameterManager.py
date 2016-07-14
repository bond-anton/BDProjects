from __future__ import division, print_function

import datetime as dt
import numpy as np
import numbers

from ScientificProjects import datetime_to_float, float_to_datetime
from ScientificProjects.Entities.Parameter import ParameterType, Parameter
from ScientificProjects.EntityManagers import EntityManager

default_parameter_types = {'Generic': 'Unspecified parameter',
                           # Single value parameters
                           'Numeric value': 'Single numeric value',
                           'String value': 'String value',
                           'Boolean value': 'Boolean value',
                           'DateTime value': 'Single DateTime value',
                           # dictionary
                           'Dictionary': 'Dictionary',
                           # ranges
                           'Numeric range': 'Numeric values range',
                           'DateTime range': 'DateTime values range',
                           # grids
                           'Uniform numeric grid': 'Uniform numeric grid',
                           'NonUniform numeric grid': 'NonUniform numeric grid',
                           }


class ParameterManager(EntityManager):

    def __init__(self, engine, session_manager):
        super(ParameterManager, self).__init__(engine, session_manager)

    def create_parameter_type(self, parameter_type, description=None):
        parameter_type_object, parameter_type_exists = self._check_parameter_type_name(parameter_type, description)
        if isinstance(parameter_type_object, ParameterType):
            if self.session_manager.signed_in() or parameter_type_object.name in default_parameter_types:
                if not parameter_type_exists:
                    parameter_type_object.user_id = self.session_manager.user.id
                    self.session.add(parameter_type_object)
                    self.session.commit()
                    if parameter_type_object.name not in default_parameter_types:
                        record = 'Parameter type "%s" successfully created' % parameter_type_object.name
                        self.session_manager.log_manager.log_record(record=record, category='Information')
                    return parameter_type_object
                else:
                    self.session.rollback()
                    if parameter_type_object.name not in default_parameter_types:
                        record = 'Parameter type "%s" is already registered' % parameter_type_object.name
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return self.session.query(ParameterType).filter(
                        ParameterType.name == parameter_type_object.name).one()
            else:
                record = 'Attempt to create Parameter Type before signing in'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
        else:
            record = 'Wrong Parameter Type argument'
            self.session_manager.log_manager.log_record(record=record, category='Warning')

    def delete_parameter_type(self, parameter_type):
        if self.session_manager.signed_in():
            if not isinstance(parameter_type, ParameterType):
                record = 'Wrong argument for Parameter Type delete operation'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
            self.session.delete(parameter_type)
            self.session.commit()
            record = 'Parameter type "%s" deleted' % parameter_type.name
            self.session_manager.log_manager.log_record(record=record, category='Information')
            return True
        else:
            record = 'Attempt to delete Parameter Type before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def _create_parameter(self, name, parameter_type, float_value=None, string_value=None,
                          index=0, unit_name=None, description=None, parent=None, commit=True,
                          suppres_log_message=False):
        if self.session_manager.signed_in():
            parameter_type_object, parameter_type_exists = self._check_parameter_type_name(parameter_type, description)
            if unit_name is None:
                unit_name = ''
            else:
                unit_name = str(unit_name)
            if not parameter_type_exists:
                record = 'Parameter type "%s" not exist' % parameter_type_object.name
                self.session_manager.log_manager.log_record(record=record, category='Warning')
            else:
                parameter_type_id = parameter_type_object.id
                parent_id = None
                if parent is not None:
                    if isinstance(parent, Parameter):
                        existing_parameter = self.session.query(Parameter).filter(Parameter.id == parent.id).all()
                        if existing_parameter:
                            parent_id = existing_parameter[0].id
                        else:
                            record = 'Parameter "%s", id=%d not exist' % (parent.name, parent.id)
                            self.session_manager.log_manager.log_record(record=record, category='Warning')
                    elif isinstance(parent, int):
                        existing_parameter = self.session.query(Parameter).filter(Parameter.id == parent).all()
                        if existing_parameter:
                            parent_id = existing_parameter[0].id
                        else:
                            record = 'Parameter with id=%d not exist' % parent
                            self.session_manager.log_manager.log_record(record=record, category='Warning')
                    else:
                        record = 'Parent must be valid Parameter or its ID'
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                parameter = Parameter(name=name, type_id=parameter_type_id, index=index,
                                      session_id=self.session_manager.session_data.id)
                parameter.unit_name = unit_name
                if parent_id:
                    parameter.parent_id = parent_id
                if string_value is not None:
                    parameter.string_value = string_value
                if float_value is not None:
                    parameter.float_value = float_value
                if commit:
                    self.session.add(parameter)
                    self.session.commit()
                    if not suppres_log_message:
                        record = 'Parameter "%s" created' % parameter.name
                        self.session_manager.log_manager.log_record(record=record, category='Information')
                return parameter
        else:
            record = 'Attempt to create Parameter before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')

    def delete_parameter(self, parameter):
        if self.session_manager.signed_in():
            if not isinstance(parameter, Parameter):
                record = 'Wrong argument for Parameter delete operation'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
            if parameter.parent:
                if 'range' in parameter.parent.type.name and (parameter.name == 'start' or parameter.name == 'stop'):
                    record = 'Can not delete START or STOP from RANGE parameter. Delete RANGE parameter itself.'
                    self.session_manager.log_manager.log_record(record=record, category='Warning')
                    return False
            self.session.delete(parameter)
            self.session.commit()
            record = 'Parameter "%s" deleted' % parameter.name
            self.session_manager.log_manager.log_record(record=record, category='Information')
            return True
        else:
            record = 'Attempt to delete Parameter before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def copy_parameter(self, parameter, suppress_parent_warning=False, commit=True):
        if self.session_manager.signed_in():
            if not isinstance(parameter, Parameter):
                record = 'Wrong argument for Parameter copy operation'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return None
            if parameter.parent and not suppress_parent_warning:
                record = 'Parameter belongs to its PARENT. This information will be lost in parameter copy.'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
            new = self._create_parameter(name=parameter.name,
                                         parameter_type=parameter.type,
                                         float_value=parameter.float_value,
                                         string_value=parameter.string_value,
                                         index=parameter.index,
                                         unit_name=parameter.unit_name,
                                         description=parameter.description,
                                         parent=None,
                                         commit=commit,
                                         suppres_log_message=True)
            for child in parameter.children:
                child_copy = self.copy_parameter(child, suppress_parent_warning=True, commit=commit)
                child_copy.parent_id = new.id
            if commit:
                self.session.commit()
                record = 'Parameter "%s" copied' % parameter.name
                self.session_manager.log_manager.log_record(record=record, category='Information')
            return new
        else:
            record = 'Attempt to copy Parameter before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None

    def _check_parameter_type_name(self, parameter_type, description=None):
        parameter_type_exists = False
        if isinstance(parameter_type, str):
            parameter_type_object = ParameterType(name=parameter_type, description=description)
        elif isinstance(parameter_type, ParameterType):
            parameter_type_object = parameter_type
        else:
            parameter_type_object = None
            return parameter_type_object, parameter_type_exists
        existing_parameter_type = \
            self.session.query(ParameterType).filter(ParameterType.name == parameter_type_object.name).all()
        if existing_parameter_type:
            parameter_type_object = existing_parameter_type[0]
            parameter_type_exists = True
        return parameter_type_object, parameter_type_exists

    def get_parameter_types(self, name=None):
        q = self.session.query(ParameterType)
        if name is not None and len(str(name)) > 2:
            template = '%' + str(name) + '%'
            q = q.filter(ParameterType.name.ilike(template))
        return q.all()

    def create_generic_parameter(self, name, float_value=None, string_value=None,
                                 unit_name=None, description=None, parent=None, commit=True):
        if not isinstance(float_value, numbers.Number):
            raise ValueError('Expected numeric value for a float_value')
        return self._create_parameter(name, parameter_type='Generic',
                                      float_value=np.float(float_value),
                                      string_value=string_value,
                                      unit_name=unit_name, description=description,
                                      parent=parent,
                                      commit=commit)

    def create_dict_parameter(self, name, description=None, parent=None, commit=True):
        return self._create_parameter(name, parameter_type='Dictionary',
                                      description=description,
                                      parent=parent,
                                      commit=commit)

    def create_numeric_parameter(self, name, value, unit_name=None, description=None, parent=None, commit=True):
        if not isinstance(value, numbers.Number):
            raise ValueError('Expected numeric value for a parameter')
        return self._create_parameter(name, parameter_type='Numeric value',
                                      float_value=np.float(value), unit_name=unit_name, description=description,
                                      parent=parent, commit=commit)

    def create_string_parameter(self, name, value, unit_name=None, description=None, parent=None, commit=True):
        if not isinstance(value, str):
            raise ValueError('Expected string value for a parameter')
        return self._create_parameter(name, parameter_type='String value',
                                      string_value=value, unit_name=unit_name, description=description,
                                      parent=parent, commit=commit)

    def create_boolean_parameter(self, name, value, description=None, parent=None, commit=True):
        if not isinstance(value, numbers.Number):
            raise ValueError('Expected boolean or numeric value for a parameter')
        return self._create_parameter(name, parameter_type='Boolean value',
                                      float_value=np.float(bool(value)), description=description,
                                      parent=parent, commit=commit)

    def create_datetime_parameter(self, name, value, description=None, parent=None, commit=True):
        if not isinstance(value, dt.datetime):
            raise ValueError('Expected datetime value for a parameter')
        td = datetime_to_float(value)
        return self._create_parameter(name, parameter_type='DateTime value',
                                      float_value=td, description=description, parent=parent, commit=commit)

    def create_numeric_range_parameter(self, name, start, stop, description=None, parent=None, commit=True):
        if not (isinstance(start, numbers.Number) and isinstance(stop, numbers.Number)):
            raise ValueError('Expected numeric value for start and stop')
        range_parameter = self._create_parameter(name, parameter_type='Numeric range',
                                                 description=description, parent=parent, commit=commit)
        self.create_numeric_parameter(name='start', value=start, parent=range_parameter, commit=commit)
        self.create_numeric_parameter(name='stop', value=stop, parent=range_parameter, commit=commit)
        return range_parameter

    def create_datetime_range_parameter(self, name, start, stop, description=None, parent=None, commit=True):
        if not (isinstance(start, dt.datetime) and isinstance(stop, dt.datetime)):
            raise ValueError('Expected datetime value for start and stop')
        range_parameter = self._create_parameter(name, parameter_type='DateTime range',
                                                 description=description, parent=parent, commit=commit)
        self.create_datetime_parameter(name='start', value=start, parent=range_parameter, commit=commit)
        self.create_datetime_parameter(name='stop', value=stop, parent=range_parameter, commit=commit)
        return range_parameter

    def get_dangling_parameters(self, delete=False):
        if self.session_manager.signed_in():
            q = self.session.query(Parameter).filter(Parameter.parent == None)
            q = q.filter(Parameter.measurements == None)
            q = q.filter(Parameter.samples == None)
            q = q.filter(Parameter.equipment == None)
            q = q.filter(Parameter.data_channels == None)
            if delete:
                result = q.delete(synchronize_session='fetch')
                self.session.commit()
                record = 'Deleted %i dangling Parameters' % result
                self.session_manager.log_manager.log_record(record=record, category='Information')
            else:
                result = q.all()
                self.session.commit()
                record = 'Found %i dangling Parameters' % len(result)
                self.session_manager.log_manager.log_record(record=record, category='Information')
            return result
        else:
            record = 'Attempt to query Parameter before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return []


def get_range_parameter_value(parameter):
    if not isinstance(parameter, Parameter):
        raise ValueError('Expected valid Parameter object')
    if parameter.type.name not in ['DateTime range', 'Numeric range']:
        raise ValueError('Expected valid Parameter object of range type')
    start = None
    stop = None
    for child in parameter.children:
        if child.name == 'start':
            start = child.float_value
        elif child.name == 'stop':
            stop = child.float_value
    if parameter.type.name == 'DateTime range':
        start = float_to_datetime(start)
        stop = float_to_datetime(stop)
    return start, stop
