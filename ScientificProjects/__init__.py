from __future__ import division, print_function

from sqlalchemy.ext.declarative import declarative_base

from ScientificProjects._version import __version__


default_date_format = '%Y-%m-%d'
default_time_format = '%H:%M:%S'
default_date_time_format = default_date_format + ' ' + default_time_format

default_connection_parameters = {'db_name': '/:memory:',
                                 'backend': 'sqlite',
                                 'hostname': '',
                                 'port': '',
                                 'user': '',
                                 'password': ''}

default_log_categories = {'Information': 'Informational messages',
                          'Warning': 'Warning messages',
                          'Error': 'Error messages'}

default_users = {'bot': [None, None, None, 'bot', None]}

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

Base = declarative_base()
