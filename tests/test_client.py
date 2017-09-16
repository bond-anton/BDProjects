from __future__ import division, print_function
import unittest

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

    def test_installer(self):
        Installer(config_file_name=self.config_file_name, overwrite=True)

    def test_client(self):
        Client(config_file_name=self.config_file_name)