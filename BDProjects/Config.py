from __future__ import division, print_function
import sys
from os.path import isfile
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from BDProjects import default_connection_parameters


def read_config(file_name=None):
    if file_name is None:
        connection_parameters = default_connection_parameters
    else:
        if not isfile(file_name):
            raise IOError('Config file not found')
        config = configparser.ConfigParser()
        try:
            config.read(file_name)
        except configparser.MissingSectionHeaderError:
            raise ValueError('Wrong format of config file')
        if sys.version_info.major > 2:
            try:
                db_config = config['Database']
                db_name = db_config['name']
                backend = db_config['backend']
                hostname = db_config['host']
                port = db_config['port']
                user = db_config['user']
                password = db_config['password']
            except KeyError:
                raise ValueError('Section or Option not found in config file')
        else:
            try:
                db_name = config.get('Database', 'name')
                backend = config.get('Database', 'backend')
                hostname = config.get('Database', 'host')
                port = config.get('Database', 'port')
                user = config.get('Database', 'user')
                password = config.get('Database', 'password')
            except(configparser.NoSectionError, configparser.NoOptionError):
                raise ValueError('Section or Option not found in config file')
        connection_parameters = {'db_name': db_name,
                                 'backend': backend,
                                 'host': hostname,
                                 'port': port,
                                 'user': user,
                                 'password': password
                                 }
    return connection_parameters


def write_config(connection_parameters, file_name):
    if isinstance(connection_parameters['port'], int):
        if connection_parameters['port'] == 0:
            port_string = ''
        else:
            port_string = '%d' % connection_parameters['port']
    else:
        port_string = ''
    config = configparser.ConfigParser()
    config.add_section('Database')
    if sys.version_info.major > 2:
        db_config = config['Database']
        db_config['name'] = connection_parameters['db_name']
        db_config['backend'] = connection_parameters['backend']
        db_config['host'] = connection_parameters['host']
        db_config['port'] = port_string
        db_config['user'] = connection_parameters['user']
        db_config['password'] = connection_parameters['password']
    else:
        config.set('Database', 'name', connection_parameters['db_name'])
        config.set('Database', 'backend', connection_parameters['backend'])
        config.set('Database', 'host', connection_parameters['host'])
        config.set('Database', 'port', port_string)
        config.set('Database', 'user', connection_parameters['user'])
        config.set('Database', 'password', connection_parameters['password'])
    with open(file_name, 'w') as configfile:
        config.write(configfile)

