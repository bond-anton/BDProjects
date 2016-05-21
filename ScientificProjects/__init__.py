from __future__ import division, print_function

from sqlalchemy.ext.declarative import declarative_base

default_date_format = '%Y-%m-%d'
default_time_format = '%H:%M:%S'
default_date_time_format = default_date_format + ' ' + default_time_format

Base = declarative_base()

from ScientificProjects._version import __version__
