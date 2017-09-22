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

        cp = read_config(self.config_file_name)
        cp['user'] = 'test_user'
        if cp['backend'] == 'sqlite':
            try:
                Connector(config=cp)
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
        connector = Connector(config_file_name=self.config_file_name)
        Installer(connector=connector, overwrite=True)
        i = Installer(connector=connector, overwrite=False)
        i.user_manager.sign_in('administrator', 'admin')
        self.assertTrue(i.check_if_user_is_administrator())
        self.assertTrue(i.user_manager.check_if_user_is_administrator())
        self.assertTrue(i.signed_in())
        self.assertTrue(i.user_manager.signed_in())
        i.user_manager.sign_out()

    def test_client(self):
        connector = Connector(config_file_name=self.config_file_name)
        Installer(connector=connector, overwrite=True)
        cl = Client(connector=connector)
        cl.user_manager.user = None
        cl.user_manager._generate_session_data()
        with self.assertRaises(ValueError):
            cl.user = 'user'
        with self.assertRaises(ValueError):
            cl.session_data = 'session data'
        with self.assertRaises(ValueError):
            cl.project = 'project'
