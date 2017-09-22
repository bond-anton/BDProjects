from __future__ import division, print_function
import unittest

from BDProjects.Entities import MeasurementType
from BDProjects.Client import Connector, Installer, Client


class TestMeasurementTypeManager(unittest.TestCase):

    def setUp(self):
        self.config_file_name = 'tests/config.ini'
        connector = Connector(config_file_name=self.config_file_name)
        Installer(connector=connector, overwrite=True)
        self.client = Client(connector=connector)
        self.client.user_manager.sign_in('administrator', 'admin')
        self.test_user = self.client.user_manager.create_user('jack', 'pass', 'jack@somesite.com', 'Jack', 'Black')
        self.test_user2 = self.client.user_manager.create_user('jessy', 'pass', 'jessy@somesite.com', 'Jessy', 'Kriek')
        self.client.user_manager.sign_out()

    def test_create_measurement_type(self):
        result = self.client.user_manager.measurement_type_manager.create_measurement_type('Novel measurement type')
        self.assertFalse(result)
        self.client.user_manager.sign_in('jack', 'pass')
        result = self.client.user_manager.measurement_type_manager.create_measurement_type(
            name='Novel measurement type',
            description='Novel measurement type description text',
            parent=None)
        self.assertIsInstance(result, MeasurementType)
        result2 = self.client.user_manager.measurement_type_manager.create_measurement_type(
            name='Novel measurement type',
            description='Novel measurement type description text',
            parent=None)
        self.assertEqual(result, result2)
        result2 = self.client.user_manager.measurement_type_manager.create_measurement_type(
            name='Novel measurement sub-type 1',
            description='Novel measurement type description text',
            parent=result)
        self.assertIsInstance(result2, MeasurementType)
        self.assertEqual(result2.parent_id, result.id)
        result2 = self.client.user_manager.measurement_type_manager.create_measurement_type(
            name='Novel measurement sub-type 1',
            description='Novel measurement type description text',
            parent=result.name)
        self.assertIsInstance(result2, MeasurementType)
        self.assertEqual(result2.parent_id, result.id)
        result2 = self.client.user_manager.measurement_type_manager.create_measurement_type(
            name='Novel measurement sub-type 1',
            description='Novel measurement type description text',
            parent='Not existing type')
        self.assertFalse(result2)
        self.client.user_manager.sign_out()

    def test_delete_measurement_type(self):
        self.client.user_manager.sign_in('jack', 'pass')
        meas_type = self.client.user_manager.measurement_type_manager.create_measurement_type(
            name='Novel measurement type',
            description='Novel measurement type description text',
            parent=None)
        self.client.user_manager.sign_out()
        result = self.client.user_manager.measurement_type_manager.delete_measurement_type('Novel measurement type')
        self.assertFalse(result)
        self.client.user_manager.sign_in('jack', 'pass')
        result = self.client.user_manager.measurement_type_manager.delete_measurement_type('Novel measurement type')
        self.assertFalse(result)
        result = self.client.user_manager.measurement_type_manager.delete_measurement_type(meas_type)
        self.assertTrue(result)
        self.client.user_manager.sign_out()

    def test_get_measurement_types(self):
        self.client.user_manager.sign_in('jack', 'pass')
        meas_type = self.client.user_manager.measurement_type_manager.create_measurement_type(
            name='Novel measurement type',
            description='Novel measurement type description text',
            parent=None)
        meas_type2 = self.client.user_manager.measurement_type_manager.create_measurement_type(
            name='Novel measurement sub-type 1',
            description='Novel measurement type description text',
            parent=None)
        meas_type3 = self.client.user_manager.measurement_type_manager.create_measurement_type(
            name='No',
            description='Novel measurement type description text',
            parent=None)
        self.client.user_manager.sign_out()
        result = self.client.user_manager.measurement_type_manager.get_measurement_types('Novel measurement type')
        self.assertFalse(result)
        self.client.user_manager.sign_in('jack', 'pass')
        result = self.client.user_manager.measurement_type_manager.get_measurement_types('Novel measurement type',
                                                                                         exact=True)
        self.assertEqual(result[0], meas_type)
        result = self.client.user_manager.measurement_type_manager.get_measurement_types('Novel measurement',
                                                                                         exact=False)
        self.assertEqual(result[0], meas_type)
        self.assertEqual(result[1], meas_type2)
        result = self.client.user_manager.measurement_type_manager.get_measurement_types('No', exact=False)
        self.assertFalse(result)
        result = self.client.user_manager.measurement_type_manager.get_measurement_types('No', exact=True)
        self.assertEqual(result[0], meas_type3)
        self.client.user_manager.sign_out()

    def test_get_measurement_types_tree(self):
        self.client.user_manager.sign_in('jack', 'pass')
        meas_type = self.client.user_manager.measurement_type_manager.create_measurement_type(
            name='Novel measurement type',
            description='Novel measurement type description text',
            parent=None)
        meas_type2 = self.client.user_manager.measurement_type_manager.create_measurement_type(
            name='Novel measurement sub-type 1',
            description='Novel measurement type description text',
            parent=meas_type)
        self.client.user_manager.measurement_type_manager.create_measurement_type(
            name='No',
            description='Novel measurement type description text',
            parent=meas_type2)
        self.client.user_manager.sign_out()
        result = self.client.user_manager.measurement_type_manager.get_measurement_types_tree()
        self.assertFalse(result)
        self.client.user_manager.sign_in('jack', 'pass')
        self.client.user_manager.measurement_type_manager.get_measurement_types_tree()
        self.client.user_manager.measurement_type_manager.get_measurement_types_tree(
            root=meas_type2.name)
        result = self.client.user_manager.measurement_type_manager.get_measurement_types_tree(
            root=meas_type2.name + '_s')
        self.assertEqual(result, {})
        self.client.user_manager.sign_out()
