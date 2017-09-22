from __future__ import division, print_function

from BDProjects.Client import Connector, Installer


connector = Connector(config_file_name='config.ini')
installer = Installer(connector=connector, overwrite=True)

