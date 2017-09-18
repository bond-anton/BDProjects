from __future__ import division, print_function
import unittest

from BDProjects.Config import default_connection_parameters, read_config, write_config


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.config_file_name = 'tests/config.ini'
        self.broken_format_config_file_name = 'tests/config_broken_format.ini'
        self.no_section_config_file_name = 'tests/config_no_section.ini'
        self.temp_config_file_name = 'tests/config_tmp.ini'

    def test_default_config(self):
        cp = read_config(file_name=None)
        self.assertEqual(cp, default_connection_parameters)

    def test_read_config_file(self):
        cp = read_config(file_name=self.config_file_name)
        connection_parameters = {'db_name': 'tests/data/test.db',
                                 'backend': 'sqlite',
                                 'host': '',
                                 'port': '',
                                 'user': '',
                                 'password': ''
                                 }
        self.assertEqual(cp, connection_parameters)
        with self.assertRaises(IOError):
            read_config(file_name='xxx' + self.config_file_name)
        with self.assertRaises(ValueError):
            read_config(self.broken_format_config_file_name)
        with self.assertRaises(ValueError):
            read_config(self.no_section_config_file_name)

    def test_write_config_file(self):
        connection_parameters = {'db_name': 'data/test.db',
                                 'backend': 'sqlite',
                                 'host': 'localhos',
                                 'port': 0,
                                 'user': 'test_user',
                                 'password': 'secret_password'
                                 }
        write_config(connection_parameters, self.temp_config_file_name)
        connection_parameters['port'] = ''
        cp = read_config(self.temp_config_file_name)
        self.assertEqual(cp, connection_parameters)
        connection_parameters = {'db_name': 'data/test.db',
                                 'backend': 'sqlite',
                                 'host': 'localhos',
                                 'port': '',
                                 'user': 'test_user',
                                 'password': 'secret_password'
                                 }
        write_config(connection_parameters, self.temp_config_file_name)
        cp = read_config(self.temp_config_file_name)
        self.assertEqual(cp, connection_parameters)
        connection_parameters = {'db_name': 'data/test.db',
                                 'backend': 'sqlite',
                                 'host': 'localhos',
                                 'port': 9000,
                                 'user': 'test_user',
                                 'password': 'secret_password'
                                 }
        write_config(connection_parameters, self.temp_config_file_name)
        connection_parameters['port'] = str(connection_parameters['port'])
        cp = read_config(self.temp_config_file_name)
        self.assertEqual(cp, connection_parameters)