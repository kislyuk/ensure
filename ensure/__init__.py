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
        self.orig_subject = subject
        self.error_factory = error_factory
        self.catch = catch
        self.args = []
        self.kwargs = {}
        self.call_subject = False

    def __call__(self, subject=None):
        self.orig_subject = subject
        self.args = []
        self.kwargs = {}
        self.call_subject = False
        return self

    def __repr__(self):
        desc = "<{module}.{classname} object at 0x{mem_loc:x} inspecting {subject}>"
        return desc.format(module=self.__module__,
                           classname=self.__class__.__name__,
                           mem_loc=id(self),
                           subject=_repr(self.orig_subject))

    @property
    def subject(self):
        if self.call_subject:
            return self._run(self.orig_subject, self.args, self.kwargs)
        else:
            return self.orig_subject

    def _run(self, func, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        try:
            return func(*args, **kwargs)
        except self.catch as err:
            new_err = self.error_factory(err)
            raise new_err

class IterableInspector(Inspector):
    def of(self, prototype):
        for item in self.subject:
            self._run(unittest_case.assertIsInstance, (item, prototype))
        if isinstance(self.subject, Mapping):
            return MappingInspector(self.subject)

    def of_nonempty(self, prototype):
        for item in self.subject:
            if len(item) == 0:
                raise self.error_factory(_format("Expected {} to be non-empty", item))
        return self.of(prototype)

class MappingInspector(Inspector):
    def to(self, prototype):
        for value in self.subject.values():
            self._run(unittest_case.assertIsInstance, (value, prototype))

    def to_nonempty(self, prototype):
        for value in self.subject.values():
            if len(value) == 0:
                raise self.error_factory(_format("Expected {} to be non-empty", value))
        return self.to(prototype)

class Ensure(Inspector):
    def equals(self, other):
        self._run(unittest_case.assertEqual, (self.subject, other))

    def is_not_equal_to(self, other):
        self._run(unittest_case.assertNotEqual, (self.subject, other))

    does_not_equal = is_not_equal_to

    def is_(self, other):
        self._run(unittest_case.assertIs, (self.subject, other))

    def is_not(self, other):
        self._run(unittest_case.assertIsNot, (self.subject, other))

    def contains(self, element):
        self._run(unittest_case.assertIn, (element, self.subject))

    def contains_none_of(self, elements):
        for element in elements:
            self._run(unittest_case.assertNotIn, (element, self.subject))

    def contains_one_of(self, elements):
        if sum(e in self.subject for e in elements) != 1:
            raise self.error_factory(_format("Expected {} to have exactly one of {}", self.subject, elements))

    def contains_only(self, elements):
        for element in self.subject:
            if element not in elements:
                raise self.error_factory(_format("Expected {} to have only {}, but it contains {}",
                                                 self.subject, elements, element))
        self.contains_all_of(elements)

    def contains_some_of(self, elements):
        if all(e not in self.subject for e in elements):
            raise self.error_factory(_format("Expected {} to have some of {}", self.subject, elements))

    contains_one_or_more_of = contains_some_of

    def contains_all_of(self, elements):
        for element in elements:
            if element not in self.subject:
                raise self.error_factory(_format("Expected {} to have all of {}, but it does not contain {}",
                                                 self.subject, elements, element))

    def does_not_contain(self, element):
        self._run(unittest_case.assertNotIn, (element, self.subject))

    def contains_no(self, prototype):
        for element in self.subject:
            self._run(unittest_case.assertNotIsInstance, (element, prototype))

    def has_attribute(self, attr):
        if not hasattr(self.subject, attr):
            raise self.error_factory(_format("Expected {} to have attribute {}", self.subject, attr))

    hasattr = has_attribute

    def is_in(self, iterable):
        self._run(unittest_case.assertIn, (self.subject, iterable))

    def is_not_in(self, iterable):
        self._run(unittest_case.assertNotIn, (self.subject, iterable))

    not_in = is_not_in

    def is_true(self):
        self._run(unittest_case.assertTrue, (self.subject,))

    def is_false(self):
        self._run(unittest_case.assertFalse, (self.subject,))

    def is_none(self):
        self._run(unittest_case.assertIsNone, (self.subject,))

    def is_not_none(self):
        self._run(unittest_case.assertIsNotNone, (self.subject,))

    def is_empty(self):
        if len(self.subject) > 0:
            raise self.error_factory(_format("Expected {} to be empty", self.subject))

    def is_nonempty(self):
        if len(self.subject) == 0:
            raise self.error_factory(_format("Expected {} to be non-empty", self.subject))

    def is_a(self, prototype):
        self._run(unittest_case.assertIsInstance, (self.subject, prototype))
        if hasattr(self.subject, '__iter__'):
            return IterableInspector(self.subject)

    is_an = is_a
    is_an_instance_of = is_a

    def is_a_nonempty(self, prototype):
        self.is_nonempty()
        return self.is_a(prototype)

    def is_an_empty(self, prototype):
        self.is_empty()
        return self.is_a(prototype)

    def is_positive(self):
        self._run(unittest_case.assertGreater, (self.subject, 0))

    def is_a_positive(self, prototype):
        self.is_positive()
        return self.is_a(prototype)

    def is_negative(self):
        self._run(unittest_case.assertLess, (self.subject, 0))

    def is_a_negative(self, prototype):
        self.is_negative()
        return self.is_a(prototype)

    def is_nonnegative(self):
        self._run(unittest_case.assertGreaterEqual, (self.subject, 0))

    def is_a_nonnegative(self, prototype):
        self.is_nonnegative()
        return self.is_a(prototype)

    def is_not_a(self, prototype):
        self._run(unittest_case.assertNotIsInstance, (self.subject, prototype))

    not_a = is_not_a

    def matches(self, pattern, flags=0):
        if not re.match(pattern, self.subject, flags):
            raise self.error_factory(_format("Expected {} to match {}", self.subject, pattern))

    def is_an_iterable_of(self, prototype):
        for element in self.subject:
            self._run(unittest_case.assertIsInstance, (element, prototype))
        if isinstance(self.subject, Mapping):
            return MappingInspector(self.subject)

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
        if not isinstance(self.subject, (int, float, long)):
            raise self.error_factory(_format("Expected {} to be numeric (int, float, or long)", self.subject))

    def is_callable(self):
        if not callable(self.subject):
            raise self.error_factory(_format("Expected {} to be callable", self.subject))

    def has_length(self, length):
        try:
            unittest_case.assertTrue(len(self.subject) == length)
        except self.catch as err:
            raise self.error_factory(_format("Expected {} to have length {}", self.subject, length))

    def is_greater_than(self, other):
        try:
            unittest_case.assertTrue(self.subject > other)
        except self.catch as err:
            raise self.error_factory(_format("Expected {} to be greater than {}", self.subject, other))

    def is_less_than(self, other):
        try:
            unittest_case.assertTrue(self.subject < other)
        except self.catch as err:
            raise self.error_factory(_format("Expected {} to be less than {}", self.subject, other))

    def is_greater_than_or_equal_to(self, other):
        try:
            unittest_case.assertTrue(self.subject >= other)
        except self.catch as err:
            raise self.error_factory(_format("Expected {} to be greater than or equal to {}", self.subject, other))

    def is_less_than_or_equal_to(self, other):
        try:
            unittest_case.assertTrue(self.subject <= other)
        except self.catch as err:
            raise self.error_factory(_format("Expected {} to be less than or equal to {}", self.subject, other))

    def called_with(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.call_subject = True
        return self

    with_args = called_with

    def raises(self, expected_exception):
        return unittest_case.assertRaises(expected_exception, self.orig_subject, *self.args, **self.kwargs)

    def raises_regex(self, expected_exception, expected_regexp):
        return unittest_case.assertRaisesRegexp(expected_exception, expected_regexp, self.orig_subject,
                                                  *self.args, **self.kwargs)

    #def has_schema(self, schema):
    #    import jsonschema
    #    self._run(jsonschema.validate, (self.subject, schema))

ensure = Ensure()
ensure_raises = unittest_case.assertRaises
ensure_raises_regex = unittest_case.assertRaisesRegexp
