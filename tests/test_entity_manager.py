from __future__ import division, print_function
import unittest

from BDProjects.Client import Connector, Installer, Client
from BDProjects.EntityManagers.EntityManager import EntityManager


class TestEntityManager(unittest.TestCase):

    def setUp(self):
        self.config_file_name = 'tests/config.ini'
        connector = Connector(config_file_name=self.config_file_name)
        Installer(connector=connector, overwrite=True)
        self.client = Client(connector=connector)
        self.client.user_manager.sign_in('administrator', 'admin')
        self.test_user = self.client.user_manager.create_user('jack', 'pass', 'jack@somesite.com', 'Jack', 'Black')
        self.test_user2 = self.client.user_manager.create_user('jessy', 'pass', 'jessy@somesite.com', 'Jessy', 'Kriek')
        self.client.user_manager.sign_out()

    def test_entity_manager_properties(self):
        em = EntityManager(session_manager=self.client)
        with self.assertRaises(ValueError):
            em.session = 'session'
        with self.assertRaises(ValueError):
            em.session_data = 'session'
        with self.assertRaises(ValueError):
            em.user = 'user'
        with self.assertRaises(ValueError):
            em.project = 'project'
