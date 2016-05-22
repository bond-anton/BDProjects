from __future__ import division, print_function
from ScientificProjects.Manager import Installer

db_name = 'data/test.db'
backend = 'sqlite'
hostname = ''
port = ''
user = ''
password = ''

installer = Installer(db_name=db_name, backend=backend, hostname=hostname, port=port,
                      user=user, password=password, overwrite=True)
