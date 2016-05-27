from __future__ import division, print_function

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from ScientificProjects.Entities.MeasurementType import MeasurementType
from ScientificProjects.EntityManagers import EntityManager


class MeasurementTypeManager(EntityManager):

    def __init__(self, engine, session_manager):
        super(MeasurementTypeManager, self).__init__(engine, session_manager)

    def create_measurement_type(self, name, description=None, parent=None):
        if self.session_manager.signed_in():
            measurement_type = MeasurementType(name=str(name))
            measurement_type.session_id = self.session_manager.session_data.id
            if description is not None:
                measurement_type.description = str(description)
            if parent is not None:
                try:
                    parent_id = self.session.query(MeasurementType.id).filter(MeasurementType.name == str(parent)).one()
                    if parent_id:
                        measurement_type.parent_id = parent_id[0]
                except NoResultFound:
                    pass
            try:
                self.session.add(measurement_type)
                self.session.commit()
                record = 'Measurement type "%s" created' % measurement_type.name
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return True
            except IntegrityError:
                self.session.rollback()
                record = 'Measurement type "%s" already exists' % measurement_type.name
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to create measurement type before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

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
