from __future__ import division, print_function

from ScientificProjects.Entities.Parameter import ParameterType, Parameter
from ScientificProjects.EntityManagers import EntityManager


class ParameterManager(EntityManager):

    def __init__(self, engine, session_manager):
        self.default_parameter_types = {'Numeric value': 'Single numeric value',
                                        'String value': 'String value',
                                        'Boolean value': 'Boolean value',
                                        'DateTime value': 'Single DateTime value',
                                        'Numeric range': 'Numeric values range',
                                        'Multiple numeric range': 'Tuple of numeric ranges',
                                        'DateTime range': 'DateTime values range',
                                        'Multiple DateTime range': 'Tuple of DateTime ranges',
                                        'Uniform numeric grid': 'Uniform numeric grid',
                                        'NonUniform numeric grid': 'NonUniform numeric grid',
                                        }
        super(ParameterManager, self).__init__(engine, session_manager)
        self._create_default_parameter_types()

    def create_parameter_type(self, parameter_type, description=None):
        parameter_type_object, parameter_type_exists = self._check_parameter_type_name(parameter_type, description)
        if isinstance(parameter_type_object, ParameterType):
            if self.session_manager.signed_in() or parameter_type_object.name in self.default_parameter_types:
                if not parameter_type_exists:
                    parameter_type_object.user_id = self.session_manager.user.id
                    self.session.add(parameter_type_object)
                    self.session.commit()
                    if parameter_type_object.name not in self.default_parameter_types:
                        self.session_manager.log_manager.log_record('Parameter type %s successfully created' %
                                                                    parameter_type_object.name, 'Information')
                    return parameter_type_object
                else:
                    self.session.rollback()
                    if parameter_type_object.name not in self.default_parameter_types:
                        self.session_manager.log_manager.log_record('Parameter type %s is already registered' %
                                                                    parameter_type_object.name, 'Warning')
                    return self.session.query(ParameterType).filter(ParameterType.name == parameter_type_object.name).one()
            else:
                self.session_manager.log_manager.log_record('Attempt to create Parameter Type before signing in',
                                                            'Warning')
        else:
            self.session_manager.log_manager.log_record('Wrong Parameter Type argument',
                                                        'Warning')

    def create_parameter(self, name, parameter_type, value, index=0, unit_name=None, description=None, parent=None):
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
                if isinstance(value, str):
                    parameter.string_value = value
                elif isinstance(value, (int, float)):
                    parameter.float_value = value
                else:
                    self.session_manager.log_manager.log_record('Wrong value of the parameter',
                                                                'Error')
                    raise ValueError('Wrong value of parameter')
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

    def _create_default_parameter_types(self):
        for parameter_type in self.default_parameter_types:
            self.create_parameter_type(parameter_type, self.default_parameter_types[parameter_type])

    def get_parameter_types(self):
        parameter_types = self.session.query(ParameterType).all()
        result = {}
        for parameter_type in parameter_types:
            result[parameter_type.name] = parameter_type.id
        return result
