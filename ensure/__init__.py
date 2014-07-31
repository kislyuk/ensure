from __future__ import print_function, unicode_literals

import sys
import collections
import types
import re
import functools
from unittest.case import TestCase
from collections import namedtuple, Mapping, Iterable

USING_PYTHON2 = True if sys.version_info < (3, 0) else False

__all__ = ['EnsureError', 'Ensure', 'Check', 'ensure', 'check', 'ensure_raises', 'ensure_raises_regex', 'ensure_annotations']

if USING_PYTHON2:
    __all__ = map(bytes, __all__)

try:
    from repr import Repr
except ImportError:
    from reprlib import Repr

_repr = Repr().repr

unittest_case = TestCase(methodName='__init__')


def _format(message, *args):
    return message.format(*map(_repr, args))


class EnsureError(AssertionError):
    # TODO: preserve original error type, define API for introspecting EnsureError
    pass


class Inspector(object):
    def __init__(self, subject=None, error_factory=EnsureError, catch=Exception):
        self._orig_subject = subject
        self._error_factory = error_factory
        self._catch = catch
        self._args = []
        self._kwargs = {}
        self._call_subject = False

    def __call__(self, subject=None):
        self._orig_subject = subject
        self._args = []
        self._kwargs = {}
        self._call_subject = False
        return self

    def __repr__(self):
        desc = "<{module}.{classname} object at 0x{mem_loc:x} inspecting {subject}>"
        return desc.format(module=self.__module__,
                           classname=self.__class__.__name__,
                           mem_loc=id(self),
                           subject=_repr(self._orig_subject))

    @property
    def _subject(self):
        if self._call_subject:
            return self._run(self._orig_subject, self._args, self._kwargs)
        else:
            return self._orig_subject

    def _run(self, func, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        try:
            return func(*args, **kwargs)
        except self._catch as err:
            new_err = self._error_factory(err)
            raise new_err


class IterableInspector(Inspector):
    def of(self, prototype):
        for item in self._subject:
            self._run(unittest_case.assertIsInstance, (item, prototype))
        if isinstance(self._subject, Mapping):
            return MappingInspector(self._subject)

    def of_nonempty(self, prototype):
        for item in self._subject:
            if len(item) == 0:
                raise self._error_factory(_format("Expected {} to be non-empty", item))
        return self.of(prototype)


class MappingInspector(Inspector):
    def to(self, prototype):
        for value in self._subject.values():
            self._run(unittest_case.assertIsInstance, (value, prototype))

    def to_nonempty(self, prototype):
        for value in self._subject.values():
            if len(value) == 0:
                raise self._error_factory(_format("Expected {} to be non-empty", value))
        return self.to(prototype)


class AttributeInspector(Inspector):
    @property
    def which(self):
        return Ensure(self._subject)


class KeyInspector(Inspector):
    @property
    def whose_value(self):
        return Ensure(self._subject)


class CallableInspector(Inspector):
    def returns(self, value):
        """
        returns is a synonym for equals only for called_with()
        """
        return self._subject.equals(value)

    def __getattr__(self, item):
        return getattr(self._subject, item)


class MultiInspector(Inspector):
    """
    Calls a list of inspector objects on a single subject.
    """
    def _get_inspector(self, subject):
        return subject

    def __getattr__(self, item):
        # @functools.wraps(getattr(self._subject[0], item))
        def inspect(*args, **kwargs):
            sub_inspectors = []
            for subject in self._subject:
                inspector = self._get_inspector(subject)
                inspect_method = getattr(inspector, item)
                sub_inspectors.append(inspect_method(*args, **kwargs))
            if not all(i is None for i in sub_inspectors):
                return MultiInspector(sub_inspectors)
        return inspect


class MultiEnsure(MultiInspector):
    """
    Maps a single Ensure object to an iterable of subjects.
    """
    def __init__(self, iterable, inspector):
        Inspector.__init__(self, iterable)
        self._inspector = inspector
        self._inspector(iterable).is_an(Iterable)

    def _get_inspector(self, subject):
        return self._inspector(subject)


class Ensure(Inspector):
    ''' Constructs a root-level inspector, which can perform a variety of checks (*predicates*) on subjects passed to
    it. If the checks do not pass, by default :class:`EnsureError` is raised. This can be configured by passing the
    ``error_factory`` keyword to the constructor.

    Subjects can be passed to the inspector at construction time or by calling the resulting object (each call resets
    the subject):

    .. code-block:: python

        Ensure(1).is_an(int)

        e = Ensure()
        e(1).is_an(int)

    Some predicates return child inspectors which can be chained into a series of predicates, for example:

    .. code-block:: python

        ensure({1: {2: "a"}}).has_key(1).whose_value.is_a(dict).of(int).to(str)

    '''
    @classmethod
    def each_of(cls, iterable):
        """
        Applies subsequent predicate(s) to all items in *iterable*.
        """
        return MultiEnsure(iterable, cls())

    def equals(self, other):
        """
        Ensures :attr:`subject` is equal to *other*.
        """
        self._run(unittest_case.assertEqual, (self._subject, other))

    def is_not_equal_to(self, other):
        """
        Ensures :attr:`subject` is not equal to *other*.
        """
        self._run(unittest_case.assertNotEqual, (self._subject, other))

    does_not_equal = is_not_equal_to

    def is_(self, other):
        """
        Ensures :attr:`subject` is *other* (object identity check).
        """
        self._run(unittest_case.assertIs, (self._subject, other))

    def is_not(self, other):
        """
        Ensures :attr:`subject` is not *other* (object identity check).
        """
        self._run(unittest_case.assertIsNot, (self._subject, other))

    def contains(self, element):
        """
        Ensures :attr:`subject` contains *other*.
        """
        self._run(unittest_case.assertIn, (element, self._subject))

    def contains_none_of(self, elements):
        """
        Ensures :attr:`subject` contains none of *elements*, which must be an iterable.
        """
        for element in elements:
            self._run(unittest_case.assertNotIn, (element, self._subject))

    def contains_one_of(self, elements):
        """
        Ensures :attr:`subject` contains exactly one of *elements*, which must be an iterable.
        """
        if sum(e in self._subject for e in elements) != 1:
            raise self._error_factory(_format("Expected {} to have exactly one of {}", self._subject, elements))

    def contains_only(self, elements):
        """
        Ensures :attr:`subject` contains all of *elements*, which must be an iterable, and no other items.
        """
        for element in self._subject:
            if element not in elements:
                raise self._error_factory(_format("Expected {} to have only {}, but it contains {}",
                                                 self._subject, elements, element))
        self.contains_all_of(elements)

    def contains_some_of(self, elements):
        """
        Ensures :attr:`subject` contains at least one of *elements*, which must be an iterable.
        """
        if all(e not in self._subject for e in elements):
            raise self._error_factory(_format("Expected {} to have some of {}", self._subject, elements))

    contains_one_or_more_of = contains_some_of

    def contains_all_of(self, elements):
        """
        Ensures :attr:`subject` contains all of *elements*, which must be an iterable.
        """
        for element in elements:
            if element not in self._subject:
                raise self._error_factory(_format("Expected {} to have all of {}, but it does not contain {}",
                                                 self._subject, elements, element))

    def does_not_contain(self, element):
        """
        Ensures :attr:`subject` does not contain *element*.
        """
        self._run(unittest_case.assertNotIn, (element, self._subject))

    def contains_no(self, prototype):
        """
        Ensures no item of :attr:`subject` is of class *prototype*.
        """
        for element in self._subject:
            self._run(unittest_case.assertNotIsInstance, (element, prototype))

    def has_key(self, key):
        """
        Ensures :attr:`subject` is a :class:`collections.Mapping` and contains *key*.
        """
        self.is_a(Mapping)
        self.contains(key)
        return KeyInspector(self._subject[key])

    def has_keys(self, keys):
        """
        Ensures :attr:`subject` is a :class:`collections.Mapping` and contains *keys*, which must be an iterable.
        """
        self.is_a(Mapping)
        self.contains_all_of(keys)

    def has_only_keys(self, keys):
        """
        Ensures :attr:`subject` is a :class:`collections.Mapping` and contains *keys*, and no other keys.
        """
        self.is_a(Mapping)
        self.contains_only(keys)

    def has_attribute(self, attr):
        """
        Ensures :attr:`subject` has an attribute *attr*.
        """
        if not hasattr(self._subject, attr):
            raise self._error_factory(_format("Expected {} to have attribute {}", self._subject, attr))
        return AttributeInspector(getattr(self._subject, attr))

    hasattr = has_attribute

    def is_in(self, iterable):
        """
        Ensures :attr:`subject` is contained in *iterable*.
        """
        self._run(unittest_case.assertIn, (self._subject, iterable))

    def is_not_in(self, iterable):
        """
        Ensures :attr:`subject` is not contained in *iterable*.
        """
        self._run(unittest_case.assertNotIn, (self._subject, iterable))

    not_in = is_not_in

    def is_true(self):
        """
        Ensures :attr:`subject` is ``True``.
        """
        self._run(unittest_case.assertTrue, (self._subject,))

    def is_false(self):
        """
        Ensures :attr:`subject` is ``False``.
        """
        self._run(unittest_case.assertFalse, (self._subject,))

    def is_none(self):
        """
        Ensures :attr:`subject` is ``None``.
        """
        self._run(unittest_case.assertIsNone, (self._subject,))

    def is_not_none(self):
        """
        Ensures :attr:`subject` is not ``None``.
        """
        self._run(unittest_case.assertIsNotNone, (self._subject,))

    def is_empty(self):
        """
        Ensures :attr:`subject` has length zero.
        """
        if len(self._subject) > 0:
            raise self._error_factory(_format("Expected {} to be empty", self._subject))

    def is_nonempty(self):
        """
        Ensures :attr:`subject` has non-zero length.
        """
        if len(self._subject) == 0:
            raise self._error_factory(_format("Expected {} to be non-empty", self._subject))

    def is_a(self, prototype):
        """
        Ensures :attr:`subject` is an object of class *prototype*.
        """
        self._run(unittest_case.assertIsInstance, (self._subject, prototype))
        if hasattr(self._subject, '__iter__'):
            return IterableInspector(self._subject)

    is_an = is_a
    is_an_instance_of = is_a

    def is_a_nonempty(self, prototype):
        """
        Ensures :attr:`subject` is an object of class *prototype* and has non-zero length.
        """
        self.is_nonempty()
        return self.is_a(prototype)

    def is_an_empty(self, prototype):
        """
        Ensures :attr:`subject` is an object of class *prototype* and has zero length.
        """
        self.is_empty()
        return self.is_a(prototype)

    def is_positive(self):
        """
        Ensures :attr:`subject` is greater than 0.
        """
        self._run(unittest_case.assertGreater, (self._subject, 0))

    def is_a_positive(self, prototype):
        """
        Ensures :attr:`subject` is greater than 0 and is an object of class *prototype*.
        """
        self.is_positive()
        return self.is_a(prototype)

    def is_negative(self):
        """
        Ensures :attr:`subject` is less than 0.
        """
        self._run(unittest_case.assertLess, (self._subject, 0))

    def is_a_negative(self, prototype):
        """
        Ensures :attr:`subject` is less than 0 and is an object of class *prototype*.
        """
        self.is_negative()
        return self.is_a(prototype)

    def is_nonnegative(self):
        """
        Ensures :attr:`subject` is greater than or equal to 0.
        """
        self._run(unittest_case.assertGreaterEqual, (self._subject, 0))

    def is_a_nonnegative(self, prototype):
        """
        Ensures :attr:`subject` is greater than or equal to 0 and is an object of class *prototype*.
        """
        self.is_nonnegative()
        return self.is_a(prototype)

    def is_not_a(self, prototype):
        """
        Ensures :attr:`subject` is not an object of class *prototype*.
        """
        self._run(unittest_case.assertNotIsInstance, (self._subject, prototype))

    not_a = is_not_a

    def matches(self, pattern, flags=0):
        """
        Ensures :attr:`subject` matches regular expression *pattern*.
        """
        if not re.match(pattern, self._subject, flags):
            raise self._error_factory(_format("Expected {} to match {}", self._subject, pattern))

    def is_an_iterable_of(self, prototype):
        """
        Ensures :attr:`subject` is an iterable containing only objects of class *prototype*.
        """
        for element in self._subject:
            self._run(unittest_case.assertIsInstance, (element, prototype))
        if isinstance(self._subject, Mapping):
            return MappingInspector(self._subject)

    def is_a_list_of(self, prototype):
        """
        Ensures :attr:`subject` is a :class:`list` containing only objects of class *prototype*.
        """
        self.is_a(list)
        return self.is_an_iterable_of(prototype)

    def is_a_set_of(self, prototype):
        """
        Ensures :attr:`subject` is a :class:`set` containing only objects of class *prototype*.
        """
        self.is_a(set)
        return self.is_an_iterable_of(prototype)

    def is_a_mapping_of(self, prototype):
        """
        Ensures :attr:`subject` is a :class:`collections.Mapping` containing only objects of class *prototype*.
        """
        self.is_a(Mapping)
        return self.is_an_iterable_of(prototype)

    def is_a_dict_of(self, prototype):
        """
        Ensures :attr:`subject` is a :class:`dict` containing only objects of class *prototype*.
        """
        self.is_a(dict)
        return self.is_an_iterable_of(prototype)

    def is_numeric(self):
        """
        Ensures :attr:`subject` is an int, float, or long.
        """
        if not isinstance(self._subject, (int, float, long)):
            raise self._error_factory(_format("Expected {} to be numeric (int, float, or long)", self._subject))

    def is_callable(self):
        """
        Ensures :attr:`subject` is a callable.
        """
        if not callable(self._subject):
            raise self._error_factory(_format("Expected {} to be callable", self._subject))

    def has_length(self, length):
        """
        Ensures :attr:`subject` has length *length*.
        """
        try:
            unittest_case.assertTrue(len(self._subject) == length)
        except self._catch as err:
            raise self._error_factory(_format("Expected {} to have length {}", self._subject, length))

    def is_greater_than(self, other):
        """
        Ensures :attr:`subject` is greater than *other*.
        """
        try:
            unittest_case.assertTrue(self._subject > other)
        except self._catch as err:
            raise self._error_factory(_format("Expected {} to be greater than {}", self._subject, other))

    exceeds = is_greater_than

    def is_less_than(self, other):
        """
        Ensures :attr:`subject` is less than *other*.
        """
        try:
            unittest_case.assertTrue(self._subject < other)
        except self._catch as err:
            raise self._error_factory(_format("Expected {} to be less than {}", self._subject, other))

    def is_greater_than_or_equal_to(self, other):
        """
        Ensures :attr:`subject` is greater than or equal to *other*.
        """
        try:
            unittest_case.assertTrue(self._subject >= other)
        except self._catch as err:
            raise self._error_factory(_format("Expected {} to be greater than or equal to {}", self._subject, other))

    def is_less_than_or_equal_to(self, other):
        """
        Ensures :attr:`subject` is less than or equal to *other*.
        """
        try:
            unittest_case.assertTrue(self._subject <= other)
        except self._catch as err:
            raise self._error_factory(_format("Expected {} to be less than or equal to {}", self._subject, other))

    def called_with(self, *args, **kwargs):
        """
        Before evaluating subsequent predicates, calls :attr:`subject` with given arguments (but unlike a direct call,
        catches and transforms any exceptions that arise during the call).
        """
        self._args = args
        self._kwargs = kwargs
        self._call_subject = True
        return CallableInspector(self)

    with_args = called_with

    def raises(self, expected_exception):
        """
        Ensures preceding predicates (specifically, :meth:`called_with()`) result in *expected_exception* being raised.
        """
        return unittest_case.assertRaises(expected_exception, self._orig_subject, *self._args, **self._kwargs)

    def raises_regex(self, expected_exception, expected_regexp):
        """
        Ensures preceding predicates (specifically, :meth:`called_with()`) result in *expected_exception* being raised,
        and the string representation of *expected_exception* must match regular expression *expected_regexp*.
        """
        return unittest_case.assertRaisesRegexp(expected_exception, expected_regexp, self._orig_subject,
                                                  *self._args, **self._kwargs)

    #def has_schema(self, schema):
    #    import jsonschema
    #    self._run(jsonschema.validate, (self._subject, schema))


class Check(object):
    """
    Like Ensure, but if a check fails, saves the error instead of raising it immediately. The error can then be acted
    upon using :meth:`or_raise()` or :meth:`or_call()`.

    ``.each_of()`` is not supported by the **Check** inspector; all other methods are supported.
    """
    def __init__(self, *args, **kwargs):
        self._inspector = Ensure(*args, **kwargs)
        self._exception = None

    def __call__(self, *args, **kwargs):
        self.__init__(*args, **kwargs)
        return self

    def __getattr__(self, item):
        inspect_method = getattr(self._inspector, item)
        if isinstance(inspect_method, Inspector):
            self._inspector = inspect_method
            return self

        def inspect(*args, **kwargs):
            if self._exception is None:
                try:
                    self._inspector = inspect_method(*args, **kwargs)
                except self._inspector._catch as e:
                    self._exception = e
            return self
        return inspect

    def or_raise(self, error_factory, message=None, *args, **kwargs):
        """
        Raises an exception produced by **error_factory** if a predicate fails.

        :param error_factory: Class or callable (e.g. :class:`Exception`) which will be invoked to produce the resulting exception.
        :param message: String to be formatted and passed as the first argument to *error_factory*. The following substrings are replaced by formatting: "{type}" by the exception type, "{msg}" by the exception's string representation, and "{}" by both. If *message* is ``None``, the original exception is passed.
        """
        if self._exception:
            if message is None:
                raise error_factory(self._exception, *args, **kwargs)
            else:
                raise error_factory(message.format('{}: {}'.format(type(self._exception).__name__, self._exception),
                                                   msg=self._exception, type=type(self._exception).__name__),
                                    *args, **kwargs)

    otherwise = or_raise

    def or_call(self, _callable, *args, **kwargs):
        """
        Calls **_callable** with supplied args and kwargs if a predicate fails.
        """
        if self._exception:
            _callable(*args, **kwargs)


def _check_default_argument(f, arg, value):
    if value is not None and arg in f.__annotations__:
        templ = f.__annotations__[arg]
        if not isinstance(value, templ):
            msg = "Default argument {arg} to {f} does not match annotation type {t}"
            raise EnsureError(msg.format(arg=arg, f=f, t=templ))


class WrappedFunction:
    """
    Wrapper for functions to check argument annotations
    """

    def __init__(self, arg_properties, f):
        self.arg_properties = arg_properties
        self.f = f
        self.__doc__ = f.__doc__

    def __call__(self, *args, **kwargs):
        for arg, templ, pos in self.arg_properties:
            if pos is not None and len(args) > pos:
                value = args[pos]
            elif arg in kwargs:
                value = kwargs[arg]
            else:
                continue

            if not isinstance(value, templ):
                msg = "Argument {arg} to {f} does not match annotation type {t}"
                raise EnsureError(msg.format(arg=arg, f=self.f, t=templ))

        return self.f(*args, **kwargs)

    def __getattr__(self, attr_name):
        return getattr(self.f, attr_name)

    def __repr__(self):
        return repr(self.f)

    def __str__(self):
        return str(self.f)

    def __get__(self, obj, type=None):
        return types.MethodType(self, obj)


class WrappedFunctionReturn(WrappedFunction):
    """
    Wrapper for functions to check argument annotations with return checking
    """

    def __init__(self, arg_properties, f, return_templ):
        super().__init__(arg_properties, f)
        self.return_templ = return_templ

    def __call__(self, *args, **kwargs):
        for arg, templ, pos in self.arg_properties:
            if pos is not None and len(args) > pos:
                value = args[pos]
            elif arg in kwargs:
                value = kwargs[arg]
            else:
                continue

            if not isinstance(value, templ):
                msg = "Argument {arg} to {f} does not match annotation type {t}"
                raise EnsureError(msg.format(arg=arg, f=self.f, t=templ))

        return_val = self.f(*args, **kwargs)
        if not isinstance(return_val, self.return_templ):
                msg = "Return value of {f} does not match annotation type {t}"
                raise EnsureError(msg.format(f=self.f, t=self.return_templ))
        return return_val


def ensure_annotations(f):
    """
    Decorator to be used on functions with annotations. Runs type checks to enforce annotations. Raises
    :class:`EnsureError` if any argument passed to *f* is not of the type specified by the annotation. Also raises
    :class:`EnsureError` if the return value of *f* is not of the type specified by the annotation. Examples:

    .. code-block:: python

        from ensure import ensure_annotations

        @ensure_annotations
        def f(x: int, y: float) -> float:
            return x+y

        print(f(1, y=2.2))

        >>> 3.2

        print(f(1, y=2))

        >>> ensure.EnsureError: Argument y to <function f at 0x109b7c710> does not match annotation type <class 'float'>
    """

    if f.__defaults__:
        for rpos, value in enumerate(f.__defaults__):
            pos = f.__code__.co_argcount - len(f.__defaults__) + rpos
            arg = f.__code__.co_varnames[pos]
            _check_default_argument(f, arg, value)
    if f.__kwdefaults__:
        for arg, value in f.__kwdefaults__.items():
            _check_default_argument(f, arg, value)

    arg_properties = []
    for pos, arg in enumerate(f.__code__.co_varnames):
        if pos >= f.__code__.co_argcount + f.__code__.co_kwonlyargcount:
            break
        elif arg in f.__annotations__:
            templ = f.__annotations__[arg]
            if pos >= f.__code__.co_argcount:
                arg_properties.append((arg, templ, None))
            else:
                arg_properties.append((arg, templ, pos))

    if 'return' in f.__annotations__:
        return_templ = f.__annotations__['return']
        return WrappedFunctionReturn(arg_properties, f, return_templ)
    else:
        return WrappedFunction(arg_properties, f)


ensure = Ensure()
check = Check()

ensure_raises = unittest_case.assertRaises
ensure_raises_regex = unittest_case.assertRaisesRegexp
