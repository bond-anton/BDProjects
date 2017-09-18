from __future__ import division, print_function
import datetime as dt
import numbers

from sqlalchemy.ext.declarative import declarative_base

from ._version import __version__


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
    if not isinstance(dt_value, dt.datetime):
        raise ValueError('Expected valid datetime object')
    return (dt_value - reference_time).total_seconds()


def float_to_datetime(float_value):
    if float_value is None:
        return None
    elif not isinstance(float_value, numbers.Number):
        raise ValueError('Expected number')
    return reference_time + dt.timedelta(seconds=float_value)
