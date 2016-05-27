from __future__ import division, print_function

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

    """
    def get_measurement_types(self, root=None):
        if self.session_manager.signed_in():
            measurement_types = {}
            if root is None:
                roots = self.session.query(MeasurementType.name).filter(MeasurementType.parent_id == None).all()
            else:
                roots = []
                try:
                    root_id = self.session.query(MeasurementType.id).filter(
                        MeasurementType.name == str(root)).one()
                    if root_id:
                        roots = self.session.query(MeasurementType.name).filter(
                            MeasurementType.parent_id == root_id[0]).all()
                except NoResultFound:
                    pass
            for root in roots:
                measurement_types[root[0]] = self.get_measurement_types(root[0])
            return measurement_types
        else:
            record = 'Attempt to get measurement types before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return {}
    """
