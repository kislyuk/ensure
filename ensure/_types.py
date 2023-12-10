from six import add_metaclass


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


class NumericByteStringType(NumericStringType):
    _type = bytes


class IntegerStringType(NumericStringType):
    _cast = int


class IntegerByteStringType(IntegerStringType):
    _type = bytes


@add_metaclass(NumericStringType)
class NumericString(str):
    pass


@add_metaclass(NumericByteStringType)
class NumericByteString(bytes):
    pass


@add_metaclass(IntegerStringType)
class IntegerString(str):
    pass


@add_metaclass(IntegerByteStringType)
class IntegerByteString(bytes):
    pass
