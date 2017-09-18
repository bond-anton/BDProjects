from __future__ import division, print_function

from BDProjects import __version__
from BDProjects.Entities import Version
from BDProjects.EntityManagers import EntityManager


class VersionManager(EntityManager):

    def __init__(self, engine, session_manager):
        version_string = __version__.split('.')
        self.__current_version = Version(version_major=int(version_string[0]),
                                         version_minor=int(version_string[1]),
                                         version_patch=int(version_string[2]))
        self.__database_version = None
        super(VersionManager, self).__init__(engine, session_manager)
        self.check_version()

    @property
    def current_version(self):
        return self.__current_version

    @property
    def database_version(self):
        return self.__database_version

    @database_version.setter
    def database_version(self, version):
        if isinstance(version, Version) or version is None:
            self.__database_version = version
        else:
            raise ValueError('Can not set database version')

    def check_version(self):
        self.database_version = self.session.query(Version).order_by(Version.id.desc()).first()
        if not self.database_version:
            self.session.add(self.current_version)
            self.session.commit()
        else:
            if self.database_version > self.current_version:
                record = 'Version of database %s > software version %s. Upgrade the software'
                record = record % (self.database_version, self.current_version)
                self.session_manager.log_manager.log_record(record=record, category='Warning')
            elif self.database_version < self.current_version:
                self._upgrade_database()

    def _upgrade_database(self):
        record = 'Upgrading database version from %s to %s'
        record = record % (self.database_version, self.current_version)
        self.session_manager.log_manager.log_record(record=record, category='Information')
        self.session.add(self.current_version)
        self.session.commit()
