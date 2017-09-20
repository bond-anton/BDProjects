from __future__ import division, print_function

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from BDProjects.Entities import MeasurementType

from .EntityManager import EntityManager
from ._helpers import require_signed_in


class MeasurementTypeManager(EntityManager):

    def __init__(self, engine, session_manager):
        super(MeasurementTypeManager, self).__init__(engine, session_manager)

    @require_signed_in
    def create_measurement_type(self, name, description=None, parent=None):
        measurement_type = MeasurementType(name=str(name))
        measurement_type.session_id = self.session_manager.session_data.id
        if description is not None:
            measurement_type.description = str(description)
        if parent is not None:
            if isinstance(parent, MeasurementType):
                measurement_type.parent_id = parent.id
            else:
                parents = self.get_measurement_types(parent, exact=True)
                if parents:
                    measurement_type.parent_id = parents[0].id
                else:
                    record = 'No measurement type is found with keyword "%s"' % parent
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

    @require_signed_in
    def delete_measurement_type(self, measurement_type):
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

    @require_signed_in
    def get_measurement_types_tree(self, root=None):
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

    @require_signed_in
    def get_measurement_types(self, name=None, exact=False):
        q = self.session.query(MeasurementType)
        if name is not None:
            if exact:
                q = q.filter(MeasurementType.name == str(name))
            elif len(str(name)) > 2:
                template = '%' + str(name) + '%'
                q = q.filter(MeasurementType.name.ilike(template))
            else:
                record = 'Please use exact=True than searching measurement types with name shorter than 2 chars'
                self.session_manager.log_manager.log_record(record=record,
                                                            category='Warning')
                return None
        return q.all()
