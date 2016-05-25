from __future__ import division, print_function
import sys
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from ScientificProjects import default_connection_parameters


def read_config(file_name=None):
    if file_name is None:
        connection_parameters = default_connection_parameters
    else:
        config = configparser.ConfigParser()
        config.read('config.ini')
        if sys.version_info.major > 2:
            db_config = config['Database']
            db_name = db_config['name']
            backend = db_config['backend']
            hostname = db_config['host']
            port = db_config['port']
            user = db_config['user']
            password = db_config['password']
        else:
            db_name = config.get('Database', 'name')
            backend = config.get('Database', 'backend')
            hostname = config.get('Database', 'host')
            port = config.get('Database', 'port')
            user = config.get('Database', 'user')
            password = config.get('Database', 'password')
        connection_parameters = {'db_name': db_name,
                                 'backend': backend,
                                 'host': hostname,
                                 'port': port,
                                 'user': user,
                                 'password': password
                                 }
    return connection_parameters
