from __future__ import division, print_function
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from ScientificProjects.Entities.Equipment import Manufacturer, EquipmentCategory, EquipmentAssembly, Equipment
from ScientificProjects.EntityManagers import EntityManager


class EquipmentManager(EntityManager):

    def __init__(self, engine, session_manager):
        super(EquipmentManager, self).__init__(engine, session_manager)

    def create_manufacturer(self, name, name_short, description=None):
        if self.session_manager.signed_in():
            manufacturer = Manufacturer(name=str(name), name_short=str(name_short))
            manufacturer.session_id = self.session_manager.session_data.id
            if description is not None:
                manufacturer.description = str(description)
            try:
                self.session.add(manufacturer)
                self.session.commit()
                record = 'Manufacturer "%s" created' % manufacturer.name
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return True
            except IntegrityError:
                self.session.rollback()
                record = 'Manufacturer "%s" already exists' % manufacturer.name
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to create manufacturer before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def create_equipment_category(self, name, description=None, parent=None):
        if self.session_manager.signed_in():
            equipment_category = EquipmentCategory(name=str(name))
            equipment_category.session_id = self.session_manager.session_data.id
            if description is not None:
                equipment_category.description = str(description)
            if parent is not None:
                try:
                    parent_id = self.session.query(EquipmentCategory.id).filter(
                        EquipmentCategory.name == str(parent)).one()
                    if parent_id:
                        equipment_category.parent_id = parent_id[0]
                except NoResultFound:
                    pass
            try:
                self.session.add(equipment_category)
                self.session.commit()
                record = 'Equipment category "%s" created' % equipment_category.name
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return True
            except IntegrityError:
                self.session.rollback()
                record = 'Equipment category "%s" already exists' % equipment_category.name
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return True
        else:
            record = 'Attempt to create equipment category before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def get_equipment_categories(self, root=None):
        if self.session_manager.signed_in():
            measurement_types = {}
            if root is None:
                roots = self.session.query(EquipmentCategory.name).filter(
                    EquipmentCategory.parent_id == None).all()
            else:
                roots = []
                try:
                    root_id = self.session.query(EquipmentCategory.id).filter(
                        EquipmentCategory.name == str(root)).one()
                    if root_id:
                        roots = self.session.query(EquipmentCategory.name).filter(
                            EquipmentCategory.parent_id == root_id[0]).all()
                except NoResultFound:
                    pass
            for root in roots:
                measurement_types[root[0]] = self.get_equipment_categories(root[0])
            return measurement_types
        else:
            record = 'Attempt to get equipment categories list before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return {}

    def create_equipment(self, name, category, serial_number=None, assembly=None, description=None):
        if self.session_manager.signed_in():
            equipment = Equipment(name=str(name))
            equipment.session_id = self.session_manager.session_data.id
            if serial_number is None:
                equipment.serial_number = str(uuid.uuid4())
            else:
                equipment.serial_number = str(serial_number)
            if description is not None:
                equipment.description = str(description)
            if category is not None:
                try:
                    category_id = self.session.query(EquipmentCategory.id).filter(
                        EquipmentCategory.name == str(category)).one()
                    if category_id:
                        equipment.category_id = category_id[0]
                except NoResultFound:
                    pass
            if assembly is not None:
                try:
                    assembly_id = self.session.query(EquipmentAssembly.id).filter(
                        EquipmentAssembly.name == str(assembly)).one()
                    if assembly_id:
                        equipment.assembly_id = assembly_id[0]
                except NoResultFound:
                    pass
            try:
                self.session.add(equipment)
                self.session.commit()
                record = 'Equipment "%s" created' % equipment.name
                self.session_manager.log_manager.log_record(record=record, category='Information')
            except IntegrityError:
                self.session.rollback()
                record = 'Equipment "%s (s/n: %s)" already exist' % (equipment.name, equipment.serial_number)
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return True
            return True
        else:
            record = 'Attempt to create equipment before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def create_equipment_assembly(self, name, description=None):
        if self.session_manager.signed_in():
            assembly = EquipmentAssembly(name=str(name))
            assembly.session_id = self.session_manager.session_data.id
            if description is not None:
                assembly.description = str(description)
            self.session.add(assembly)
            self.session.commit()
            record = 'Equipment assembly "%s" created' % assembly.name
            self.session_manager.log_manager.log_record(record=record, category='Information')
            return True
        else:
            record = 'Attempt to create equipment assembly before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def add_equipment_to_assembly(self, assembly, equipment):
        if self.session_manager.signed_in():
            if isinstance(assembly, EquipmentAssembly) and isinstance(equipment, Equipment):
                return True
            else:
                record = 'Wrong argument type for adding equipment to assembly'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to create equipment assembly before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False
