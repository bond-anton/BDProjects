from __future__ import division, print_function

from ScientificProjects import __version__
from ScientificProjects.Entities.Version import Version
from ScientificProjects.EntityManagers import EntityManager


class VersionManager(EntityManager):

    def __init__(self, engine, session_manager):
        version_string = __version__.split('.')
        self.current_version = Version(version_major=int(version_string[0]),
                                       version_minor=int(version_string[1]),
                                       version_patch=int(version_string[2]))
        self.database_version = None
        super(VersionManager, self).__init__(engine, session_manager)
        self.check_version()

    def check_version(self):
        if not self.session:
            self.open_session()
        self.database_version = self.session.query(Version).order_by(Version.id.desc()).first()
        if not self.database_version:
            self.session.add(self.current_version)
            self.session.commit()
        else:
            if self.database_version > self.current_version:
                log_record = 'Version of database %s > software version %s. Upgrade the software'
                log_record = log_record % (self.database_version, self.current_version)
                self.session_manager.log_manager.log_record(record=log_record,
                                                            category='Warning')
            elif self.database_version < self.current_version:
                self._upgrade_database()
        self.close_session()

    def _upgrade_database(self):
        if not self.session:
            self.open_session()
        log_record = 'Upgrading database version from %s to %s'
        log_record = log_record % (self.database_version, self.current_version)
        self.session_manager.log_manager.log_record(record=log_record,
                                                    category='Information')
        self.session.add(self.current_version)
        self.session.commit()
        self.close_session()
