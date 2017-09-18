from __future__ import division, print_function
import unittest

from BDProjects.Client import Installer, Client


class TestUserManager(unittest.TestCase):

    def setUp(self):
        self.config_file_name = 'tests/config.ini'
        Installer(config_file_name=self.config_file_name, administrator_password='admin', overwrite=True)
        self.client = Client(config_file_name=self.config_file_name)

    def test_administrator(self):
        result = self.client.user_manager.sign_in('administrator', 'admin')
        self.assertTrue(result)
        result = self.client.user_manager.sign_in('administrator', 'admin')
        self.assertFalse(result)
        self.assertTrue(self.client.user_manager.signed_in())
        self.assertTrue(self.client.signed_in())
        self.assertTrue(self.client.user_manager.check_if_user_is_administrator())
        self.assertTrue(self.client.check_if_user_is_administrator())
        roles = self.client.user_manager.user.roles
        match = True
        for role in roles:
            match = match and role.name in ['administrator', 'user']
        self.assertTrue(match)
        self.client.user_manager.sign_out()
        result = self.client.user_manager.sign_in('administrator', 'admin_wrong_password')
        self.assertFalse(result)
        result = self.client.user_manager.sign_in('administrator_wrong_login', 'admin')
        self.assertFalse(result)

    def test_system_user(self):
        result = self.client.user_manager.sign_in('bot', 'None')
        self.assertFalse(result)
        self.assertTrue(self.client.user.login == 'bot')
        self.assertTrue(self.client.user.roles[0].name == 'system')
