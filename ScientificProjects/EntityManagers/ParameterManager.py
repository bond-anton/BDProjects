from __future__ import division, print_function

import datetime as dt
import numpy as np
import numbers

from ScientificProjects import reference_time
from ScientificProjects.Entities.Parameter import ParameterType, Parameter
from ScientificProjects.EntityManagers import EntityManager

default_parameter_types = {'Numeric value': 'Single numeric value',
                           'String value': 'String value',
                           'Boolean value': 'Boolean value',
                           'DateTime value': 'Single DateTime value',
                           # ranges
                           'Numeric range': 'Numeric values range',
                           'Multiple numeric range': 'Tuple of numeric ranges',
                           'DateTime range': 'DateTime values range',
                           'Multiple DateTime range': 'Tuple of DateTime ranges',
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
                        self.session_manager.log_manager.log_record('Parameter type %s successfully created' %
                                                                    parameter_type_object.name, 'Information')
                    return parameter_type_object
                else:
                    self.session.rollback()
                    if parameter_type_object.name not in default_parameter_types:
                        self.session_manager.log_manager.log_record('Parameter type %s is already registered' %
                                                                    parameter_type_object.name, 'Warning')
                    return self.session.query(ParameterType).filter(
                        ParameterType.name == parameter_type_object.name).one()
            else:
                self.session_manager.log_manager.log_record('Attempt to create Parameter Type before signing in',
                                                            'Warning')
        else:
            self.session_manager.log_manager.log_record('Wrong Parameter Type argument',
                                                        'Warning')

    def _create_parameter(self, name, parameter_type, float_value=None, string_value=None,
                          index=0, unit_name=None, description=None, parent=None):
        if self.session_manager.signed_in():
            parameter_type_object, parameter_type_exists = self._check_parameter_type_name(parameter_type, description)
            if unit_name is None:
                unit_name = ''
            else:
                unit_name = str(unit_name)
            if not parameter_type_exists:
                self.session_manager.log_manager.log_record('Parameter type %s not exist' %
                                                            parameter_type_object.name, 'Warning')
            else:
                parameter_type_id = parameter_type_object.id
                parent_id = None
                if parent is not None:
                    if isinstance(parent, Parameter):
                        existing_parameter = self.session.query(Parameter).filter(Parameter.id == parent.id).all()
                        if existing_parameter:
                            parent_id = existing_parameter[0].id
                        else:
                            self.session_manager.log_manager.log_record('Parameter %s, id=%d not exist' %
                                                                        (parent.name, parent.id), 'Warning')
                    elif isinstance(parent, int):
                        existing_parameter = self.session.query(Parameter).filter(Parameter.id == parent).all()
                        if existing_parameter:
                            parent_id = existing_parameter[0].id
                        else:
                            self.session_manager.log_manager.log_record('Parameter with id=%d not exist' %
                                                                        parent, 'Warning')
                    else:
                        self.session_manager.log_manager.log_record('Parent must be valid Parameter or its ID',
                                                                    'Warning')
                parameter = Parameter(name=name, type_id=parameter_type_id, index=index,
                                      user_id=self.session_manager.user.id)
                parameter.unit_name = unit_name
                if parent_id:
                    parameter.parent_id = parent_id
                if string_value is not None:
                    parameter.string_value = string_value
                if float_value is not None:
                    parameter.float_value = float_value
                self.session.add(parameter)
                self.session.commit()
                self.session_manager.log_manager.log_record('Parameter %s created' % parameter.name,
                                                            'Information')
                return parameter
        else:
            self.session_manager.log_manager.log_record('Attempt to create Parameter before signing in',
                                                        'Warning')

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

    def get_parameter_types(self):
        parameter_types = self.session.query(ParameterType).all()
        result = {}
        for parameter_type in parameter_types:
            result[parameter_type.name] = parameter_type.id
        return result

    def create_numeric_parameter(self, name, value, unit_name=None, description=None, parent=None):
        if not isinstance(value, numbers.Number):
            raise ValueError('Expected numeric value for a parameter')
        return self._create_parameter(name, parameter_type=default_parameter_types['Numeric value'],
                                      float_value=np.float(value), unit_name=unit_name, description=description,
                                      parent=parent)

    def create_string_parameter(self, name, value, unit_name=None, description=None, parent=None):
        if not isinstance(value, str):
            raise ValueError('Expected string value for a parameter')
        return self._create_parameter(name, parameter_type=default_parameter_types['String value'],
                                      string_value=value, unit_name=unit_name, description=description,
                                      parent=parent)

    def create_boolean_parameter(self, name, value, description=None, parent=None):
        if not isinstance(value, numbers.Number):
            raise ValueError('Expected boolean or numeric value for a parameter')
        return self._create_parameter(name, parameter_type=default_parameter_types['Boolean value'],
                                      float_value=np.float(bool(value)), description=description, parent=parent)

    def create_datetime_parameter(self, name, value, description=None, parent=None):
        if not isinstance(value, dt.datetime):
            raise ValueError('Expected datetime value for a parameter')
        td = (value - reference_time).total_seconds()
        return self._create_parameter(name, parameter_type=default_parameter_types['Boolean value'],
                                      float_value=td, description=description, parent=parent)

