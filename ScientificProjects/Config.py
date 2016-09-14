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
        config.read(file_name)
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


def write_config(connection_parameters, file_name):
    config = configparser.ConfigParser()
    config.add_section('Database')
    if sys.version_info.major > 2:
        db_config = config['Database']
        db_config['name'] = connection_parameters['db_name']
        db_config['backend'] = connection_parameters['backend']
        db_config['host'] = connection_parameters['host']
        db_config['port'] = connection_parameters['port']
        db_config['user'] = connection_parameters['user']
        db_config['password'] = connection_parameters['password']
    else:
        config.set('Database', 'name', connection_parameters['db_name'])
        config.set('Database', 'backend', connection_parameters['backend'])
        config.set('Database', 'host', connection_parameters['host'])
        config.set('Database', 'port', str(connection_parameters['port']))
        config.set('Database', 'user', connection_parameters['user'])
        config.set('Database', 'password', connection_parameters['password'])
    with open(file_name, 'w') as configfile:
        config.write(configfile)

