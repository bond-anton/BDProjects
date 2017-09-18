from __future__ import division, print_function

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from BDProjects.Entities import Sample
from BDProjects.Entities import Parameter
from BDProjects.EntityManagers import EntityManager
from ._helpers import require_signed_in, require_project_opened


class SampleManager(EntityManager):

    def __init__(self, engine, session_manager):
        super(SampleManager, self).__init__(engine, session_manager)

    @require_signed_in
    @require_project_opened
    def create_sample(self, name, description=None):
        project = self.session_manager.project_manager.project
        sample = Sample(name=str(name))
        sample.project_id = project.id
        sample.session_id = self.session_manager.session_data.id
        if description is not None:
            sample.description = str(description)
        try:
            self.session.add(sample)
            self.session.commit()
            record = 'Sample "%s" created' % sample.name
            self.session_manager.log_manager.log_record(record=record, category='Information')
        except IntegrityError:
            self.session.rollback()
            sample = self.session.query(Sample).filter(and_(Sample.name == name,
                                                            Sample.project_id == project.id)).all()[0]
            record = 'Sample "%s" already exists' % sample.name
            self.session_manager.log_manager.log_record(record=record, category='Warning')
        return sample

    @require_signed_in
    @require_project_opened
    def delete_sample(self, sample):
        project = self.session_manager.project_manager.project
        check_sample = isinstance(sample, Sample) and sample.project_id == project.id
        if check_sample:
            self.session.delete(sample)
            self.session.commit()
            record = 'Sample "%s" successfully deleted' % sample.name
            self.session_manager.log_manager.log_record(record=record, category='Information')
            return True
        else:
            record = 'Wrong argument for sample delete operation'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    @require_signed_in
    @require_project_opened
    def get_samples(self, name=None, exact=False):
        project = self.session_manager.project_manager.project
        q = self.session.query(Sample).filter(Sample.project_id == project.id)
        if name is not None and len(str(name)) > 2:
            if exact:
                q = q.filter(Sample.name == str(name))
            else:
                template = '%' + str(name) + '%'
                q = q.filter(Sample.name.ilike(template))
        return q.all()

    @require_signed_in
    @require_project_opened
    def add_parameter_to_sample(self, sample, parameter):
        if isinstance(sample, Sample) and isinstance(parameter, Parameter):
            try:
                sample.parameters.append(parameter)
                self.session.commit()
                record = 'parameter "%s" added to sample "%s"' % (str(parameter.name),
                                                                  str(sample.name))
                self.session_manager.log_manager.log_record(record=record, category='Information')
            except IntegrityError:
                self.session.rollback()
                record = 'parameter "%s" is already added to sample "%s"' % (str(parameter.name),
                                                                             str(sample.name))
                self.session_manager.log_manager.log_record(record=record, category='Information')
            return True
        else:
            record = 'Wrong argument type for adding parameter to sample'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    @require_signed_in
    @require_project_opened
    def remove_parameter_from_sample(self, sample, parameter):
        if isinstance(sample, Sample) and isinstance(parameter, Parameter):
            if parameter in sample.parameters:
                sample.parameters.remove(parameter)
                self.session.commit()
                record = 'Parameter "%s" removed from sample "%s"' % (parameter.name, sample.name)
                self.session_manager.log_manager.log_record(record=record, category='Information')
            else:
                record = 'Parameter "%s" not found in sample "%s"' % (parameter.name, sample.name)
                self.session_manager.log_manager.log_record(record=record, category='Warning')
            return True
        else:
            record = 'Wrong argument for removing parameter from sample'
            self.session_manager.log_manager.log_record(record=record, category='Warning')
            return False

    @require_signed_in
    def get_sample_parameters(self, sample, parameter_name=None):
        if isinstance(sample, Sample):
            q = self.session.query(Parameter).join((Sample, Parameter.samples))
            q = q.filter(Sample.id == sample.id)
            if parameter_name is not None and len(str(parameter_name)) > 2:
                template = '%' + str(parameter_name) + '%'
                q = q.filter(Parameter.name.ilike(template))
            return q.all()
        else:
            raise ValueError('Wrong argument value')
