import collections, re
from unittest.case import TestCase
from collections import namedtuple, Mapping

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

class ElementInspector(Inspector):
    @property
    def which(self):
        return Ensure(self._subject)

class Ensure(Inspector):
    def equals(self, other):
        self._run(unittest_case.assertEqual, (self._subject, other))

    def is_not_equal_to(self, other):
        self._run(unittest_case.assertNotEqual, (self._subject, other))

    does_not_equal = is_not_equal_to

    def is_(self, other):
        self._run(unittest_case.assertIs, (self._subject, other))

    def is_not(self, other):
        self._run(unittest_case.assertIsNot, (self._subject, other))

    def contains(self, element):
        self._run(unittest_case.assertIn, (element, self._subject))
        return ElementInspector(element)

    def contains_none_of(self, elements):
        for element in elements:
            self._run(unittest_case.assertNotIn, (element, self._subject))

    def contains_one_of(self, elements):
        if sum(e in self._subject for e in elements) != 1:
            raise self._error_factory(_format("Expected {} to have exactly one of {}", self._subject, elements))

    def contains_only(self, elements):
        for element in self._subject:
            if element not in elements:
                raise self._error_factory(_format("Expected {} to have only {}, but it contains {}",
                                                 self._subject, elements, element))
        self.contains_all_of(elements)

    def contains_some_of(self, elements):
        if all(e not in self._subject for e in elements):
            raise self._error_factory(_format("Expected {} to have some of {}", self._subject, elements))

    contains_one_or_more_of = contains_some_of

    def contains_all_of(self, elements):
        for element in elements:
            if element not in self._subject:
                raise self._error_factory(_format("Expected {} to have all of {}, but it does not contain {}",
                                                 self._subject, elements, element))

    def does_not_contain(self, element):
        self._run(unittest_case.assertNotIn, (element, self._subject))

    def contains_no(self, prototype):
        for element in self._subject:
            self._run(unittest_case.assertNotIsInstance, (element, prototype))

    def has_attribute(self, attr):
        if not hasattr(self._subject, attr):
            raise self._error_factory(_format("Expected {} to have attribute {}", self._subject, attr))

    hasattr = has_attribute

    def is_in(self, iterable):
        self._run(unittest_case.assertIn, (self._subject, iterable))

    def is_not_in(self, iterable):
        self._run(unittest_case.assertNotIn, (self._subject, iterable))

    not_in = is_not_in

    def is_true(self):
        self._run(unittest_case.assertTrue, (self._subject,))

    def is_false(self):
        self._run(unittest_case.assertFalse, (self._subject,))

    def is_none(self):
        self._run(unittest_case.assertIsNone, (self._subject,))

    def is_not_none(self):
        self._run(unittest_case.assertIsNotNone, (self._subject,))

    def is_empty(self):
        if len(self._subject) > 0:
            raise self._error_factory(_format("Expected {} to be empty", self._subject))

    def is_nonempty(self):
        if len(self._subject) == 0:
            raise self._error_factory(_format("Expected {} to be non-empty", self._subject))

    def is_a(self, prototype):
        self._run(unittest_case.assertIsInstance, (self._subject, prototype))
        if hasattr(self._subject, '__iter__'):
            return IterableInspector(self._subject)

    is_an = is_a
    is_an_instance_of = is_a

    def is_a_nonempty(self, prototype):
        self.is_nonempty()
        return self.is_a(prototype)

    def is_an_empty(self, prototype):
        self.is_empty()
        return self.is_a(prototype)

    def is_positive(self):
        self._run(unittest_case.assertGreater, (self._subject, 0))

    def is_a_positive(self, prototype):
        self.is_positive()
        return self.is_a(prototype)

    def is_negative(self):
        self._run(unittest_case.assertLess, (self._subject, 0))

    def is_a_negative(self, prototype):
        self.is_negative()
        return self.is_a(prototype)

    def is_nonnegative(self):
        self._run(unittest_case.assertGreaterEqual, (self._subject, 0))

    def is_a_nonnegative(self, prototype):
        self.is_nonnegative()
        return self.is_a(prototype)

    def is_not_a(self, prototype):
        self._run(unittest_case.assertNotIsInstance, (self._subject, prototype))

    not_a = is_not_a

    def matches(self, pattern, flags=0):
        if not re.match(pattern, self._subject, flags):
            raise self._error_factory(_format("Expected {} to match {}", self._subject, pattern))

    def is_an_iterable_of(self, prototype):
        for element in self._subject:
            self._run(unittest_case.assertIsInstance, (element, prototype))
        if isinstance(self._subject, Mapping):
            return MappingInspector(self._subject)

    def is_a_list_of(self, prototype):
        self.is_a(list)
        return self.is_an_iterable_of(prototype)

    def is_a_set_of(self, prototype):
        self.is_a(set)
        return self.is_an_iterable_of(prototype)

    def is_a_mapping_of(self, prototype):
        self.is_a(Mapping)
        return self.is_an_iterable_of(prototype)

    def is_a_dict_of(self, prototype):
        self.is_a(dict)
        return self.is_an_iterable_of(prototype)

    def is_numeric(self):
        if not isinstance(self._subject, (int, float, long)):
            raise self._error_factory(_format("Expected {} to be numeric (int, float, or long)", self._subject))

    def is_callable(self):
        if not callable(self._subject):
            raise self._error_factory(_format("Expected {} to be callable", self._subject))

    def has_length(self, length):
        try:
            unittest_case.assertTrue(len(self._subject) == length)
        except self._catch as err:
            raise self._error_factory(_format("Expected {} to have length {}", self._subject, length))

    def is_greater_than(self, other):
        try:
            unittest_case.assertTrue(self._subject > other)
        except self._catch as err:
            raise self._error_factory(_format("Expected {} to be greater than {}", self._subject, other))

    def is_less_than(self, other):
        try:
            unittest_case.assertTrue(self._subject < other)
        except self._catch as err:
            raise self._error_factory(_format("Expected {} to be less than {}", self._subject, other))

    def is_greater_than_or_equal_to(self, other):
        try:
            unittest_case.assertTrue(self._subject >= other)
        except self._catch as err:
            raise self._error_factory(_format("Expected {} to be greater than or equal to {}", self._subject, other))

    def is_less_than_or_equal_to(self, other):
        try:
            unittest_case.assertTrue(self._subject <= other)
        except self._catch as err:
            raise self._error_factory(_format("Expected {} to be less than or equal to {}", self._subject, other))

    def called_with(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._call_subject = True
        return self

    with_args = called_with

    def raises(self, expected_exception):
        return unittest_case.assertRaises(expected_exception, self._orig_subject, *self._args, **self._kwargs)

    def raises_regex(self, expected_exception, expected_regexp):
        return unittest_case.assertRaisesRegexp(expected_exception, expected_regexp, self._orig_subject,
                                                  *self._args, **self._kwargs)

    #def has_schema(self, schema):
    #    import jsonschema
    #    self._run(jsonschema.validate, (self._subject, schema))

ensure = Ensure()
ensure_raises = unittest_case.assertRaises
ensure_raises_regex = unittest_case.assertRaisesRegexp
