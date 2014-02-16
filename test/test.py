#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import os, sys, unittest, collections, copy, re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ensure import *


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
                      'Ensure(x).has_length(10)',
                      'Ensure(x).is_nonempty()',
                      'Ensure(x).is_a(collections.Mapping)',
                      'Ensure(x).is_a_dict_of(int).to(int)',
                      'Ensure(x).is_a(collections.Mapping).of(int).to(int)',
                      'Ensure(6).is_greater_than(5)',
                      'Ensure(1.1).is_greater_than_or_equal_to(1.1)',
                      'Ensure(1.1).is_less_than_or_equal_to(1.1)',
                      'Ensure(1).is_less_than(1.1)',
                      'Ensure(1).is_positive()',
                      'Ensure(1.1).is_a_positive(float)',
                      'Ensure(-1).is_negative()',
                      'Ensure(-1).is_a_negative(int)',
                      'Ensure(0).is_nonnegative()',
                      'Ensure(0).is_a_nonnegative(int)',
                      'Ensure((collections.namedtuple("Thing", ["x"]))(x={})).has_attribute("x").which.is_a(dict)',
                      'Ensure({1:"a"}).has_key(1).whose_value.has_length(1)',
                      'Ensure({1: "a", 2: "b", 3: "c"}).has_keys((1, 2))',
                      'Ensure({1: "a", 2: "b", 3: "c"}).has_only_keys((1, 2, 3))',
                      'Ensure({}).is_empty()',
                      'Ensure(os.path.join).called_with("a", "b").returns(os.path.join("a", "b"))',
                      'Ensure(int).called_with("1100101", base=2).returns(101)',
                      'Ensure.each_of([1,2,3]).is_an(int)',
                      'Ensure.each_of([lambda x: x, lambda y: y]).called_with(1).returns(1)')
        
        for clause in ok_clauses:
            print("Testing OK clause", clause)
            eval(clause)
            if 'each_of' not in clause:
                for sub in r'Check\1.otherwise(Exception)', r'Check\1.or_raise(Exception)', r'Check\1.or_call(self.assertTrue, False)':
                    eval(re.sub(r'^Ensure(.+)', sub, clause))

        bad_clauses = ('Ensure(x).contains(-1)',
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
                       'Ensure(x).is_a(str)',
                       'Ensure(x).is_empty()',
                       'Ensure(6).is_greater_than(7)',
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
                       'Ensure.each_of([lambda x: x, lambda y: y]).called_with(2).returns(1)')

        for clause in bad_clauses:
            print("Testing bad clause", clause)
            with self.assertRaises(EnsureError):
                eval(clause)
            if 'each_of' not in clause:                
                for sub in r'Check\1.otherwise(Exception)', r'Check\1.or_raise(Exception)', r'Check\1.or_call(self.assertTrue, False)':
                    with self.assertRaises(Exception):
                        eval(re.sub(r'^Ensure(.+)', sub, clause))

        with self.assertRaises(EnsureError):
            Ensure(x).is_a_dict_of(int).to(str)
        with self.assertRaises(EnsureError):
            Ensure(x).is_a_dict_of(str).to(int)
        with self.assertRaises(EnsureError):
            Ensure(x).called_with().is_an(int)
        Ensure(lambda: True).is_callable()

    def test_called_with(self):
        for i in None, True, 1, {}, [], lambda: True:
            with self.assertRaises(EnsureError):
                Ensure(i).called_with(1, 2, x=3, y=4).equals(5)

        Ensure(lambda x: x).called_with(1).is_an(int)
        Ensure(lambda x: x).called_with(x=1).is_an(int)
        Ensure(lambda x: x).called_with().raises(TypeError)
        Ensure(lambda x: x).called_with(y=2).raises(TypeError)

    def test_annotations(self):
        if sys.version_info < (3, 0):
            return
        f_code = """
from ensure import ensure_annotations

global f

@ensure_annotations
def f(x: int, y: float) -> float:
    return x+y if x+y > 0 else int(x+y)
"""
        exec(f_code)
        self.assertEqual(f(1, 2.3), 3.3)
        with self.assertRaisesRegexp(EnsureError, "Argument y to <function f at .+> does not match annotation type <class 'float'>"):
            self.assertEqual(f(1, 2), 3.3)
        with self.assertRaisesRegexp(EnsureError, "Return value of <function f at .+> does not match annotation type <class 'float'>"):
            self.assertEqual(f(1, -2.3), 4)

if __name__ == '__main__':
    unittest.main()
