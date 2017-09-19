from __future__ import division, print_function
import unittest

from BDProjects.Client import Installer, Client
from BDProjects.EntityManagers import EntityManager


class TestEntityManager(unittest.TestCase):

    def setUp(self):
        self.config_file_name = 'tests/config.ini'
        Installer(config_file_name=self.config_file_name, administrator_password='admin', overwrite=True)
        self.client = Client(config_file_name=self.config_file_name)
        self.client.user_manager.sign_in('administrator', 'admin')
        self.test_user = self.client.user_manager.create_user('jack', 'pass', 'jack@somesite.com', 'Jack', 'Black')
        self.test_user2 = self.client.user_manager.create_user('jessy', 'pass', 'jessy@somesite.com', 'Jessy', 'Kriek')
        self.client.user_manager.sign_out()

    def test_entity_manager_properties(self):
        em = EntityManager(engine=self.client.engine, session_manager=self.client)
        with self.assertRaises(ValueError):
            em.session = 'session'
        with self.assertRaises(ValueError):
            em.session_data = 'session'
        with self.assertRaises(ValueError):
            em.user = 'user'
        with self.assertRaises(ValueError):
            em.project = 'project'
