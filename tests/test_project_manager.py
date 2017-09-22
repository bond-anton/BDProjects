from __future__ import division, print_function
import unittest

from BDProjects.Entities import Project
from BDProjects.Client import Connector, Installer, Client


class TestProjectManager(unittest.TestCase):

    def setUp(self):
        self.config_file_name = 'tests/config.ini'
        connector = Connector(config_file_name=self.config_file_name)
        Installer(connector=connector, overwrite=True)
        self.client = Client(connector=connector)
        self.client.user_manager.sign_in('administrator', 'admin')
        self.test_user = self.client.user_manager.create_user('jack', 'pass', 'jack@somesite.com', 'Jack', 'Black')
        self.test_user2 = self.client.user_manager.create_user('jessy', 'pass', 'jessy@somesite.com', 'Jessy', 'Kriek')
        self.client.user_manager.sign_out()

    def test_create_project(self):
        result = self.client.user_manager.project_manager.create_project(
            name='Super Project',
            description='My first ever really super project',
            data_dir='tests/data/files')
        self.assertFalse(result)
        self.client.user_manager.sign_in('jack', 'pass')
        result = self.client.user_manager.project_manager.create_project(
            name='Super Project',
            description='My first ever really super project',
            data_dir='tests/data/files_no_such_dir')
        self.assertFalse(result)
        prj1 = self.client.user_manager.project_manager.create_project(
            name='Super Project',
            description='My first ever really super project',
            data_dir='tests/data/files')
        prj2 = self.client.user_manager.project_manager.create_project(
            name='Super Project',
            description='My first ever really super project',
            data_dir='tests/data/files')
        self.assertEqual(prj1, prj2)
        self.client.user_manager.sign_out()

    def test_delete_project(self):
        self.client.user_manager.sign_in('jack', 'pass')
        prj1 = self.client.user_manager.project_manager.create_project(
            name='Super Project',
            description='My first ever really super project',
            data_dir='tests/data/files')
        self.client.user_manager.sign_out()
        result = self.client.user_manager.project_manager.delete_project(prj1)
        self.assertFalse(result)
        self.client.user_manager.sign_in('jack', 'pass')
        result = self.client.user_manager.project_manager.delete_project('prj1')
        self.assertFalse(result)
        result = self.client.user_manager.project_manager.delete_project(prj1)
        self.assertTrue(result)
        result = self.client.user_manager.project_manager.delete_project(prj1)
        self.assertFalse(result)
        self.client.user_manager.sign_out()

    def test_get_projects(self):
        self.client.user_manager.sign_in('jack', 'pass')
        prj1 = self.client.user_manager.project_manager.create_project(
            name='Super Project',
            description='My first ever really super project',
            data_dir='tests/data/files')
        prj2 = self.client.user_manager.project_manager.create_project(
            name='Su',
            description='My first ever really super project with short name',
            data_dir='tests/data/files')
        self.client.user_manager.sign_out()
        result = self.client.user_manager.project_manager.get_projects(prj1.name)
        self.assertFalse(result)
        self.client.user_manager.sign_in('jack', 'pass')
        result = self.client.user_manager.project_manager.get_projects(prj1.name, exact=True)
        self.assertEqual(prj1, result[0])
        result = self.client.user_manager.project_manager.get_projects(prj1.name, exact=False)
        self.assertEqual(prj1, result[0])
        result = self.client.user_manager.project_manager.get_projects(prj1.name[:2], exact=True)
        self.assertEqual(prj2, result[0])
        result = self.client.user_manager.project_manager.get_projects(prj1.name[:2], exact=False)
        self.assertFalse(result)

    def test_open_project(self):
        self.client.user_manager.sign_in('jack', 'pass')
        self.client.user_manager.project_manager.create_project(
            name='Super Project 1',
            description='My first ever really super project',
            data_dir='tests/data/files')
        self.client.user_manager.project_manager.create_project(
            name='Super Project 2',
            description='My first ever really super project',
            data_dir='tests/data/files')
        self.client.user_manager.sign_out()
        result = self.client.user_manager.project_manager.open_project('Super Project 1')
        self.assertFalse(result)
        self.client.user_manager.sign_in('jack', 'pass')
        result = self.client.user_manager.project_manager.open_project('Super Project 3')
        self.assertFalse(result)
        result1 = self.client.user_manager.project_manager.open_project('Super Project 1')
        result2 = self.client.user_manager.project_manager.open_project('Super Project 1')
        self.assertEqual(result1, result2)
        self.assertIsInstance(result1, Project)
        result = self.client.user_manager.project_manager.open_project('Super Project 2')
        self.assertFalse(result)
        self.client.user_manager.sign_out()

    def test_close_project(self):
        self.client.user_manager.sign_in('jack', 'pass')
        prj1 = self.client.user_manager.project_manager.create_project(
            name='Super Project 1',
            description='My first ever really super project',
            data_dir='tests/data/files')
        prj2 = self.client.user_manager.project_manager.create_project(
            name='Super Project 2',
            description='My first ever really super project',
            data_dir='tests/data/files')
        self.client.user_manager.sign_out()
        result = self.client.user_manager.project_manager.close_project()
        self.assertFalse(result)
        self.client.user_manager.sign_in('jack', 'pass')
        result = self.client.user_manager.project_manager.close_project()
        self.assertTrue(result)
        result = self.client.user_manager.project_manager.close_project(project=prj2)
        self.assertTrue(result)
        self.client.user_manager.project_manager.open_project(prj1.name)
        result = self.client.user_manager.project_manager.close_project()
        self.assertTrue(result)
        self.client.user_manager.project_manager.open_project(prj1.name)
        result = self.client.user_manager.project_manager.close_project(project=prj1)
        self.assertTrue(result)
        result = self.client.user_manager.project_manager.close_project(session='my session', project=prj1)
        self.assertFalse(result)
        result = self.client.user_manager.project_manager.close_project(project='prj1')
        self.assertFalse(result)
        self.client.user_manager.sign_out()

    def test_project_opened(self):
        self.client.user_manager.sign_in('jack', 'pass')
        prj1 = self.client.user_manager.project_manager.create_project(
            name='Super Project 1',
            description='My first ever really super project',
            data_dir='tests/data/files')
        prj2 = self.client.user_manager.project_manager.create_project(
            name='Super Project 2',
            description='My first ever really super project',
            data_dir='tests/data/files')
        self.client.user_manager.sign_out()
        result = self.client.user_manager.project_manager.project_opened()
        self.assertFalse(result)
        self.client.user_manager.sign_in('jack', 'pass')
        result = self.client.user_manager.project_manager.project_opened()
        self.assertFalse(result)
        result = self.client.user_manager.project_manager.project_opened(project=prj2)
        self.assertFalse(result)
        self.client.user_manager.project_manager.open_project(prj1.name)
        result = self.client.user_manager.project_manager.project_opened()
        self.assertTrue(result)
        result = self.client.user_manager.project_manager.project_opened(project=prj1)
        self.assertTrue(result)
        result = self.client.user_manager.project_manager.project_opened(project='prj1')
        self.assertFalse(result)
        result = self.client.user_manager.project_manager.project_opened(session='session')
        self.assertFalse(result)
        self.client.user_manager.sign_out()
