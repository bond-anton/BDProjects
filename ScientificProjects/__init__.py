from __future__ import division, print_function
import datetime as dt

from sqlalchemy.ext.declarative import declarative_base

from ScientificProjects._version import __version__


reference_time = dt.datetime(1970, 1, 1)
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


def datetime_to_float(dt_value):
    return (dt_value - reference_time).total_seconds()


def float_to_datetime(float_value):
    return reference_time + dt.timedelta(seconds=float_value)
