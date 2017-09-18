from __future__ import division, print_function
import unittest

from BDProjects.Client import Installer, Client


class TestUserManager(unittest.TestCase):

    def setUp(self):
        self.config_file_name = 'tests/config.ini'
        Installer(config_file_name=self.config_file_name, administrator_password='admin', overwrite=True)
        self.client = Client(config_file_name=self.config_file_name)
        self.client.user_manager.sign_in('administrator', 'admin')
        self.test_user = self.client.user_manager.create_user('jack', 'pass', 'jack@somesite.com', 'Jack', 'Black')
        self.test_user2 = self.client.user_manager.create_user('jessy', 'pass', 'jessy@somesite.com', 'Jessy', 'Kriek')
        self.client.user_manager.sign_out()

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

    def test_create_user(self):
        result = self.client.user_manager.create_user('john', 'pass', 'john@somesite.com', 'John', 'Smith')
        self.assertFalse(result)
        result = self.client.user_manager.sign_in('administrator', 'admin')
        result = self.client.user_manager.create_user('bot', 'pass', 'bot@bot.net')
        self.assertFalse(result)
        result = self.client.user_manager.create_user('john', 'pass', 'john@somesite.com', 'John', 'Smith')
        self.assertTrue(result)
        result2 = self.client.user_manager.create_user('john', 'pass', 'john@somesite.com', 'John', 'Smith')
        self.assertEqual(result, result2)
        self.client.user_manager.sign_out()

    def test_sign_in_sign_out(self):
        result = self.client.user_manager.sign_in('bot', 'None')
        self.assertFalse(result)
        result = self.client.user_manager.sign_in('jack', 'pass')
        self.assertTrue(result)
        self.assertEqual(self.client.user_manager.user.login, 'jack')
        self.client.user_manager.sign_out()
        result = self.client.user_manager.sign_in('jack', 'pass_wrong')
        self.assertFalse(result)
        result = self.client.user_manager.sign_in('jack_wrong', 'pass')
        self.assertFalse(result)
        self.assertEqual(self.client.user_manager.user.login, 'bot')

    def test_delete_user(self):
        result = self.client.user_manager.delete_user(self.test_user)
        self.assertFalse(result)
        self.client.user_manager.sign_in('jack', 'pass')
        result = self.client.user_manager.delete_user(self.test_user2)
        self.assertFalse(result)
        result = self.client.user_manager.delete_user(self.test_user)
        self.assertTrue(result)
        result = self.client.user_manager.delete_user(self.test_user)
        self.assertFalse(result)
        self.client.user_manager.sign_in('administrator', 'admin')
        result = self.client.user_manager.delete_user(self.test_user2)
        self.assertTrue(result)
        result = self.client.user_manager.delete_user(self.test_user2)
        self.assertFalse(result)
        self.client.user_manager.sign_out()

    def test_delete_session_data(self):
        self.client.user_manager.sign_in('jack', 'pass')
        result = self.client.user_manager.delete_session_data('jack',
                                                              self.client.user_manager.session_data)
        self.assertFalse(result)
        result = self.client.user_manager.delete_session_data(self.test_user2,
                                                              self.client.user_manager.session_data)
        self.assertFalse(result)
        result = self.client.user_manager.delete_session_data(self.client.user_manager.user,
                                                              self.client.user_manager.session_data)
        self.assertTrue(result)

    def test_close_session(self):
        self.client.user_manager.sign_in('jack', 'pass')
        session = self.client.user_manager.session_data
        self.client.user_manager.sign_out()
        self.client.user_manager.sign_in('jessy', 'pass')
        result = self.client.user_manager.close_session(session)
        self.assertFalse(result)
        result = self.client.user_manager.close_session('jessy')
        self.assertFalse(result)
        self.client.user_manager.sign_out()

    def test_kick_off(self):
        self.client.user_manager.sign_in('administrator', 'admin')
        client = Client(config_file_name=self.config_file_name)
        client.user_manager.sign_in('jessy', 'pass')
        self.client.user_manager.logoff_all()

    def test_log_user_info(self):
        self.client.user_manager.sign_in('administrator', 'admin')
        client = Client(config_file_name=self.config_file_name)
        client.user_manager.sign_in('jessy', 'pass')
        self.client.user_manager.log_user_info(self.test_user, True)
        self.client.user_manager.log_user_info(self.test_user2, True)
        client.user_manager.sign_out()
        client.user_manager.sign_in('jack', 'pass')
        self.client.user_manager.log_user_info(self.test_user2, True)
        self.client.user_manager.log_signed_in_users(True)
        self.client.user_manager.logoff_all()