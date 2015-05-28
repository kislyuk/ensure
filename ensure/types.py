from __future__ import absolute_import, division, print_function, unicode_literals

import sys

USING_PYTHON2 = True if sys.version_info < (3, 0) else False

if USING_PYTHON2:
    str = unicode

class NumericStringType(type):
    _type = str
    _cast = float
    def __instancecheck__(self, other):
        try:
            if not isinstance(other, self._type):
                raise TypeError()
            self._cast(other)
            return True
        except (TypeError, ValueError):
            return False

class NumericString(str):
    __metaclass__ = NumericStringType


class NumericByteStringType(NumericStringType):
    _type = bytes

class NumericByteString(bytes):
    __metaclass__ = NumericByteStringType


class IntegerStringType(NumericStringType):
    _cast = int

class IntegerString(str):
    __metaclass__ = IntegerStringType


class IntegerByteStringType(IntegerStringType):
    _type = bytes

class IntegerByteString(bytes):
    __metaclass__ = IntegerByteStringType
