from __future__ import division, print_function
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from ScientificProjects.Manager import Installer

config = configparser.ConfigParser()
config.read('config.ini')
db_config = config['Database']

db_name = db_config['name']
backend = db_config['backend']
hostname = db_config['host']
port = db_config['port']
user = db_config['user']
password = db_config['password']

installer = Installer(db_name=db_name, backend=backend, hostname=hostname, port=port,
                      user=user, password=password, overwrite=True)
