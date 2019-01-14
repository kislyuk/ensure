#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import unittest
import collections
import copy
import re
from six import text_type as str

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ensure import ensure, check, Ensure, Check, EnsureError, ensure_annotations


class TestEnsure(unittest.TestCase):
    def test_basic_ensure_statements(self):
        ensure(range(10)).contains(5)
        with self.assertRaises(EnsureError):
            ensure(range(10)).contains(-1)

        ensure("abc").is_in("abcdef")
        with self.assertRaises(EnsureError):
            ensure(range(10)).is_in(-1)

        ensure("abc").matches("(abc|def)")
        with self.assertRaises(EnsureError):
            ensure(range(10)).is_in(-1)

        x = {x: x for x in range(10)}
        ok_clauses = ('Ensure(x).contains(0)',
                      'Ensure(x).contains_all_of(range(10))',
                      'Ensure(x).contains_no(str)',
                      'Ensure(x).contains_none_of(range(20, 30))',
                      'Ensure(x).contains_one_of(range(1))',
                      'Ensure(x).contains_some_of(range(2))',
                      'Ensure(x).contains_only(range(10))',
                      'Ensure(x).does_not_contain(-1)',
                      'Ensure(x).does_not_equal(range(10))',
                      'Ensure(x).has_attribute("__iter__")',
                      'Ensure(x).has_length(10).also.is_nonempty()',
                      'Ensure(x).has_length(length=10, min=9, max=10)',
                      'Ensure(x).has_length(max=99.9)',
                      'Ensure(x).is_nonempty().also.has_length(10)',
                      'Ensure(x).is_a(collections.Mapping)',
                      'Ensure(x).is_a_dict_of(int).to(int)',
                      'Ensure(x).is_a(collections.Mapping).of(int).to(int)',
                      'Ensure(6).is_greater_than(5)',
                      'Ensure(6).exceeds(5)',
                      'Ensure(1.1).is_greater_than_or_equal_to(1.1)',
                      'Ensure(1.1).is_less_than_or_equal_to(1.1)',
                      'Ensure(1).is_less_than(1.1)',
                      'Ensure(1).is_positive()',
                      'Ensure(1.1).is_a_positive(float)',
                      'Ensure(-1).is_negative()',
                      'Ensure(-1).is_a_negative(int)',
                      'Ensure(0).is_nonnegative()',
                      'Ensure(0).is_a_nonnegative(int)',
                      'Ensure(1).is_a_positive(int).which.equals(1.0)',
                      'Ensure((collections.namedtuple("Thing", ["x"]))(x={})).has_attribute("x").which.is_a(dict)',
                      'Ensure({1:"a"}).has_key(1).whose_value.has_length(1)',
                      'Ensure({1: "a", 2: "b", 3: "c"}).has_keys((1, 2))',
                      'Ensure({1: "a", 2: "b", 3: "c"}).has_only_keys((1, 2, 3))',
                      'Ensure({}).is_empty()',
                      'Ensure(os.path.join).called_with("a", "b").returns(os.path.join("a", "b"))',
                      'Ensure(int).called_with("1100101", base=2).returns(101)',
                      'Ensure.each_of([1,2,3]).is_an(int)',
                      'Ensure.each_of([lambda x: x, lambda y: y]).called_with(1).returns(1)',
                      'Ensure(True).is_none_or.is_an(int)',  # See https://www.python.org/dev/peps/pep-0285/ (section 6)
                      'Ensure(None).is_none_or.is_a_negative(int)',
                      'Ensure(-5).is_none_or.is_a_negative(int)',
                      'Ensure({"a": "b"}).is_none_or.has_key("a")',
                      'Ensure([1,2,3]).is_sorted()',
                      'Ensure([3,2,1]).is_sorted(key=lambda x: -x)',
                      'Ensure("A").satisfies(str.isupper)',
                      'Ensure("A").satisfies(".isupper")',
                      'Ensure("ABC").satisfies(str.startswith, "AB")',
                      'Ensure("ABC").satisfies(".startswith", "AB")',
                      'Ensure(3).satisfies(lambda x, y: x < y, y=4)')

        for clause in ok_clauses:
            print("Testing OK clause", clause)
            eval(clause)
            if 'each_of' not in clause:
                for sub in r'Check\1.otherwise(Exception)', r'Check\1.or_raise(Exception)', r'Check\1.or_call(self.assertTrue, False)':
                    print("Testing OK clause", re.sub(r'^Ensure(.+)', sub, clause))
                    eval(re.sub(r'^Ensure(.+)', sub, clause))

                print("Testing OK clause", re.sub(r'Ensure(.+)', r'bool(Check\1)', clause))
                self.assertEqual(eval(re.sub(r'Ensure(.+)', r'bool(Check\1)', clause)), True)


        bad_clauses = ('Ensure(x).contains(-1)',
                       'Ensure(x).has_length(10).also.is_empty()',
                       'Ensure(x).contains_all_of(range(20))',
                       'Ensure(x).contains_no(int)',
                       'Ensure(x).contains_none_of(range(0, 30))',
                       'Ensure(x).contains_one_of(range(2))',
                       'Ensure(x).contains_some_of(range(20, 30))',
                       'Ensure(x).contains_only(range(11))',
                       'Ensure(x).does_not_contain(1)',
                       'Ensure(x).does_not_equal(x)',
                       'Ensure(x).does_not_equal(copy.deepcopy(x))',
                       'Ensure(x).has_attribute("y")',
                       'Ensure(x).has_length(1)',
                       'Ensure(x).has_length(length=1, min=9, max=10)',
                       'Ensure(x).has_length(min=11)',
                       'Ensure(x).has_length(max=1.1)',
                       'Ensure(x).is_a(str)',
                       'Ensure(x).is_empty()',
                       'Ensure(6).is_greater_than(7)',
                       'Ensure(6).exceeds(7)',
                       'Ensure(1).is_greater_than_or_equal_to(1.1)',
                       'Ensure(None).is_greater_than_or_equal_to(1.1)',
                       'Ensure(5).is_less_than_or_equal_to(1)',
                       'Ensure(1).is_less_than(None)',
                       'Ensure(0).is_positive()',
                       'Ensure(1).is_a_positive(float)',
                       'Ensure(1).is_negative()',
                       'Ensure(-0).is_a_negative(int)',
                       'Ensure(-0.1).is_nonnegative()',
                       'Ensure(None).is_a_nonnegative(int)',
                       'Ensure({1: "a"}).has_key(1).whose_value.has_length(2)',
                       'Ensure({1: "a"}).has_keys((1, 2))',
                       'Ensure({1: "a", 2: "b"}).has_only_keys([1])',
                       'Ensure({1: "a", 2: "b"}).has_only_keys([1, 2, 3])',
                       'Ensure([1, 2, 3]).has_only_keys([1, 2, 3])',
                       'Ensure(os.path.join).called_with("a", "b").returns(None)',
                       'Ensure(1).is_a_positive(int).which.equals(1.2)',
                       'Ensure.each_of([lambda x: x, lambda y: y]).called_with(2).returns(1)',
                       'Ensure(5).is_none_or.is_a_negative(int)',
                       'Ensure(None).is_a_negative(int)',
                       'Ensure([1,2,1]).is_sorted()',
                       'Ensure([1,2,1]).is_sorted(key=lambda x: -x)',
                       'Ensure(None).is_sorted()',
                       'Ensure("a").satisfies(str.isupper)',
                       'Ensure("a").satisfies(".isupper")',
                       'Ensure("ABC").satisfies(str.startswith, "Z")',
                       'Ensure("ABC").satisfies(".startswith", "Z")',
                       'Ensure(5).satisfies(str.isupper)',
                       'Ensure(5).satisfies(".isupper")')

        for clause in bad_clauses:
            print("Testing bad clause", clause)
            with self.assertRaises(EnsureError):
                eval(clause)
            if 'each_of' not in clause:
                for sub in r'Check\1.otherwise(Exception)', r'Check\1.or_raise(Exception)', r'Check\1.or_call(self.assertTrue, False)':
                    with self.assertRaises(Exception):
                        print("Testing bad clause", re.sub(r'^Ensure(.+)', sub, clause))
                        eval(re.sub(r'^Ensure(.+)', sub, clause))

                print("Testing bad clause", re.sub(r'^Ensure(.+)', r'bool(Check\1)', clause))
                self.assertEqual(eval(re.sub(r'^Ensure(.+)', r'bool(Check\1)', clause)), False)

        with self.assertRaises(EnsureError):
            Ensure(x).is_a_dict_of(int).to(str)
        with self.assertRaises(EnsureError):
            Ensure(x).is_a_dict_of(str).to(int)
        with self.assertRaises(EnsureError):
            Ensure(x).called_with().is_an(int)
        Ensure(lambda: True).is_callable()

        Ensure("1.1").is_a_numeric_string()
        with self.assertRaises(EnsureError):
            Ensure(b"1").is_a_numeric_string()
        with self.assertRaises(EnsureError):
            Ensure("").is_a_numeric_string()
        with self.assertRaises(EnsureError):
            Ensure(None).is_a_numeric_string()

        Ensure(b"1").is_a_numeric_bytestring()
        Ensure(b"1.1").is_a_numeric_bytestring()
        with self.assertRaises(EnsureError):
            Ensure("1").is_a_numeric_bytestring()
        with self.assertRaises(EnsureError):
            Ensure(b"").is_a_numeric_bytestring()
        with self.assertRaises(EnsureError):
            Ensure(None).is_a_numeric_bytestring()

        Ensure("1").is_an_integer_string()
        with self.assertRaises(EnsureError):
            Ensure("1.1").is_an_integer_string()

        Ensure(b"1").is_an_integer_bytestring()
        with self.assertRaises(EnsureError):
            Ensure(b"1.1").is_an_integer_bytestring()
        with self.assertRaises(EnsureError):
            Ensure("1").is_an_integer_bytestring()
        with self.assertRaises(EnsureError):
            Ensure(b"").is_an_integer_bytestring()
        with self.assertRaises(EnsureError):
            Ensure(None).is_an_integer_bytestring()

    def test_called_with(self):
        for i in None, True, 1, {}, [], lambda: True:
            with self.assertRaises(EnsureError):
                Ensure(i).called_with(1, 2, x=3, y=4).equals(5)

        Ensure(lambda x: x).called_with(1).is_an(int)
        Ensure(lambda x: x).called_with(x=1).is_an(int)
        Ensure(lambda x: x).called_with().raises(TypeError)
        Ensure(lambda x: x).called_with(y=2).raises(TypeError)

    @unittest.skipIf(sys.version_info < (3, 0), "Skipping test that requires Python 3 features")
    def test_annotations(self):
        f_code = """
from ensure import ensure_annotations

global f, g, h

@ensure_annotations
def f(x: int, y: float) -> float:
    t = x+y
    r = t > 0
    return t if r else int(t)

@ensure_annotations
def g(x: str, y: str="default") -> str:
    '''Simply add numbers together'''
    t = x+y
    return t

@ensure_annotations
def h(x: str, y: int):
    '''Does some work'''
    return x * y
"""
        exec(f_code)
        self.assertEqual(f(1, 2.3), 3.3)
        self.assertEqual(f(1, y=2.3), 3.3)
        self.assertEqual(f(y=1.2, x=3), 4.2)
        with self.assertRaisesRegex(
                EnsureError, "Argument y of type <class 'int'> to <function f at .+> does not match annotation type <class 'float'>"):
            self.assertEqual(f(1, 2), 3.3)
        with self.assertRaisesRegex(EnsureError, "Argument y of type <class 'int'> to <function f at .+> does not match annotation type <class 'float'>"):
            self.assertEqual(f(y=2, x=1), 3.3)
        with self.assertRaisesRegex(EnsureError, "Return value of <function f at .+> does not match annotation type <class 'float'>"):
            self.assertEqual(f(1, -2.3), 4)
        with self.assertRaisesRegex(EnsureError, "Return value of <function f at .+> does not match annotation type <class 'float'>"):
            self.assertEqual(f(x=1, y=-2.3), 4)

        # Test with mixtures of keyword and positional args
        self.assertEqual(g("the "), "the default")
        self.assertEqual(g("the ", "bomb"), "the bomb")
        self.assertEqual(g(y=g("the ", y="bomb"), x="somebody set up us "), "somebody set up us the bomb")

        self.assertEqual('g', g.__name__)
        self.assertEqual('Simply add numbers together', g.__doc__)
        self.assertRegex(repr(g), '<function g at 0x[0-9a-fA-F]+>')
        self.assertEqual('h', h.__name__)
        self.assertEqual('Does some work', h.__doc__)
        self.assertRegex(repr(h), '<function h at 0x[0-9a-fA-F]+>')

    @unittest.skipIf(sys.version_info < (3, 0), "Skipping test that requires Python 3 features")
    def test_annotations_with_bad_default(self):
        f_code = """
from ensure import ensure_annotations

global f, g

@ensure_annotations
def f(x: int, y: float=None) -> float:
    return x+y if x+y > 0 else int(x+y)

@ensure_annotations
def g(x: str, y: str=5, z='untyped with default') -> str:
    return x+y+str(z)
"""
        with self.assertRaisesRegex(EnsureError, "Default argument y of type <class 'int'> to <function g at .+> does not match annotation type <class 'str'>"):
            exec(f_code)
        # Make sure f still works as None should be excluded from default test
        self.assertEqual(f(1, 2.3), 3.3)
        self.assertEqual(f(1, y=2.3), 3.3)
        self.assertEqual(f(y=1.2, x=3), 4.2)

    @unittest.skipIf(sys.version_info < (3, 0), "Skipping test that requires Python 3 features")
    def test_annotations_after_varargs(self):
        f_code = """
from ensure import ensure_annotations

global f

@ensure_annotations
def f(x: int, y: float, *args, z: int=5) -> float:
    t = x + y
    s = sum(args)

    return t + s - z

"""
        exec(f_code)
        # Make sure f still works as None should be excluded from default test
        self.assertEqual(2.0, f(3, 4.0))
        self.assertEqual(62.0, f(3, 4.0, 10, 20, 30))
        self.assertEqual(66.0, f(3, 4.0, 10, 20, 30, z=1))
        with self.assertRaisesRegex(EnsureError, "Argument z of type <class 'str'> to <function f at .+> does not match annotation type <class 'int'>"):
            self.assertEqual(66.0, f(3, 4.0, 10, 20, 30, z='hello world'))

    @unittest.skipIf(sys.version_info < (3, 0), "Skipping test that requires Python 3 features")
    def test_annotations_with_varargs(self):
        f_code = """
from ensure import ensure_annotations

global f

@ensure_annotations
def f(x: int, y: float, *args, z: int=5) -> str:
    t = x + y
    r = ''
    for s in args:
        r = r + str(t - z) + s

    return r

"""
        exec(f_code)
        # Make sure f still works as None should be excluded from default test
        self.assertEqual('', f(3, 4.0))
        self.assertEqual('2.0abc', f(3, 4.0, 'abc'))
        self.assertEqual('2.0abc2.0def', f(3, 4.0, 'abc', 'def'))
        self.assertEqual('3.0abc3.0def', f(3, 4.0, 'abc', 'def', z=4))
        with self.assertRaisesRegex(EnsureError, "Argument z of type <class 'str'> to <function f at .+> does not match annotation type <class 'int'>"):
            self.assertEqual('3.0abc3.0def', f(3, 4.0, 'abc', 'def', z='school'))

    @unittest.skipIf(sys.version_info < (3, 0), "Skipping test that requires Python 3 features")
    def test_annotations_with_vararg_bad_default(self):
        f_code = """
from ensure import ensure_annotations

global f

@ensure_annotations
def f(x: int, y: float, *args, z: int='not an int') -> str:
    t = x + y
    r = ''
    for s in args:
        r = r + str(t - z) + s

    return r
"""
        with self.assertRaisesRegex(EnsureError, "Default argument z of type <class 'str'> to <function f at .+> does not match annotation type <class 'int'>"):
            exec(f_code)

    @unittest.skipIf(sys.version_info < (3, 0), "Skipping test that requires Python 3 features")
    def test_annotations_on_bound_methods(self):
        f_code = """
from ensure import ensure_annotations

global C

class C(object):
    @ensure_annotations
    def f(self, x: int, y: float) -> str:
        return str(x+y)

    @ensure_annotations
    def g(self, x: int, y: float):
        return str(x+y)

"""
        exec(f_code)
        c = C()
        self.assertEqual('3.3', c.f(1, 2.3))
        self.assertRegex(repr(c.f), '<bound method C.f of <.+.C object at 0x[0-9a-fA-F]+>>')
        with self.assertRaisesRegex(EnsureError, "Argument x of type <class 'float'> to <function (C.f|f) at .+> does not match annotation type <class 'int'>"):
            g = C().f(3.2, 1)

        self.assertEqual('3.3', c.g(1, 2.3))
        self.assertRegex(repr(c.g), '<bound method C.g of <.+.C object at 0x[0-9a-fA-F]+>>')
        with self.assertRaisesRegex(EnsureError, "Argument x of type <class 'float'> to <function (C.g|g) at .+> does not match annotation type <class 'int'>"):
            g = C().g(3.2, 1)

    def test_error_formatting(self):
        with self.assertRaisesRegexp(Exception, "Major fail detected"):
            check(False).is_true().or_raise(KeyError, "{} {error} detected", "Major", error="fail")

if __name__ == '__main__':
    unittest.main()
