from __future__ import division, print_function
import unittest

from sqlalchemy.exc import ArgumentError

from BDProjects.Config import read_config
from BDProjects.Client import Connector, Installer, Client


class TestClient(unittest.TestCase):

    def setUp(self):
        self.config_file_name = 'tests/config.ini'

    def test_connector(self):
        cp = read_config(self.config_file_name)
        conn1 = Connector(config=cp)
        conn2 = Connector(config_file_name=self.config_file_name)
        self.assertEqual(conn1.engine.url, conn2.engine.url)
        self.assertIsNone(conn1.session)
        self.assertIsNone(conn2.session)
        with self.assertRaises(ValueError):
            conn2.session = 'Wrong type session'
        cp = read_config(self.config_file_name)
        cp['user'] = 'test_user'
        if cp['backend'] == 'sqlite':
            try:
                conn1 = Connector(config=cp)
            except Exception as e:
                self.assertIsInstance(e, ValueError)
        else:
            Connector(config=cp)
        try:
            cp = read_config(self.config_file_name)
            cp['db_name'] = '%^&@/' + cp['db_name']
            cp['host'] = 'myhost.com'
            cp['port'] = 9000
            Connector(config=cp)
        except Exception as e:
            self.assertIsInstance(e, ValueError)

    def test_installer(self):
        Installer(config_file_name=self.config_file_name, overwrite=True)

    def test_client(self):
        Client(config_file_name=self.config_file_name)