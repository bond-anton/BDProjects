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

Base = declarative_base()
