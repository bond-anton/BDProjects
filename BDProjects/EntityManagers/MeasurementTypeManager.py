from __future__ import division, print_function

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from BDProjects.Entities.MeasurementType import MeasurementType
from BDProjects.EntityManagers import EntityManager


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
                if isinstance(parent, MeasurementType):
                    measurement_type.parent_id = parent.id
                else:
                    parents = self.get_measurement_types(parent)
                    if len(parents) == 1:
                        measurement_type.parent_id = parents[0].id
                    elif len(parents) == 0:
                        record = 'No measurement type is found with keyword "%s"' % parent
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                        return None
                    else:
                        record = 'More than one measurement type found with keyword "%s"' % parent
                        self.session_manager.log_manager.log_record(record=record, category='Warning')
                        return None
            try:
                self.session.add(measurement_type)
                self.session.commit()
                record = 'Measurement type "%s" created' % measurement_type.name
                self.session_manager.log_manager.log_record(record=record, category='Information')
            except IntegrityError:
                self.session.rollback()
                q = self.session.query(MeasurementType).filter(MeasurementType.name == str(name))
                measurement_type = q.all()[0]
                record = 'Measurement type "%s" already exists' % measurement_type.name
                self.session_manager.log_manager.log_record(record=record, category='Warning')
            return measurement_type
        else:
            record = 'Attempt to create measurement type before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return None

    def delete_measurement_type(self, measurement_type):
        if self.session_manager.signed_in():
            if isinstance(measurement_type, MeasurementType):
                self.session.delete(measurement_type)
                self.session.commit()
                record = 'Measurement type "%s" deleted' % measurement_type.name
                self.session_manager.log_manager.log_record(record=record, category='Information')
                return True
            else:
                record = 'Wrong argument for measurement type delete operation'
                self.session_manager.log_manager.log_record(record=record, category='Warning')
                return False
        else:
            record = 'Attempt to delete measurement type before signing in'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    def get_measurement_types_tree(self, root=None):
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

    def get_measurement_types(self, name=None):
        q = self.session.query(MeasurementType)
        if name is not None and len(str(name)) > 2:
            template = '%' + str(name) + '%'
            q = q.filter(MeasurementType.name.ilike(template))
        return q.all()
