from __future__ import division, print_function

from sqlalchemy import Column, Integer, DateTime, func

from ScientificProjects import Base


class Version(Base):
    __tablename__ = 'version'
    id = Column(Integer, primary_key=True)
    version_major = Column(Integer)
    version_minor = Column(Integer)
    version_patch = Column(Integer)
    registered = Column(DateTime, default=func.now())

    def __str__(self):
        return '%d.%d.%d' % (self.version_major, self.version_minor, self.version_patch)

    def __eq__(self, other):
        if isinstance(other, Version):
            return self.version_major == other.version_major \
                    and self.version_minor == other.version_minor \
                    and self.version_patch == other.version_patch
        return False

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        if isinstance(other, Version):
            if self.version_major > other.version_major:
                return True
            elif self.version_major == other.version_major:
                if self.version_minor > other.version_minor:
                    return True
                elif self.version_minor == other.version_minor:
                    return self.version_patch > other.version_patch
                else:
                    return False
            else:
                return False
        else:
            raise ValueError('Version can be compared only to other Version')

    def __lt__(self, other):
        if isinstance(other, Version):
            return other > self
        else:
            raise ValueError('Version can be compared only to other Version')

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other
