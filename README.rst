ensure: Literate assertions in Python
=====================================

*ensure* is a set of simple assertion helpers that let you write more expressive, literate, concise, and readable
Pythonic code for validating conditions. It's inspired by `should.js <https://github.com/visionmedia/should.js>`_,
`expect.js <https://github.com/LearnBoost/expect.js>`_, and builds on top of the
`unittest/JUnit assert helpers <http://docs.python.org/2/library/unittest.html#assert-methods>`_.

Because *ensure* is a standalone library (not part of a test framework), doesn't monkey-patch anything or use DSLs, and
doesn't use the assert statement (which is liable to be turned off with the ``-O`` flag), it can be used to validate
conditions in production code, not just for testing.

Aside from better looking code, a big reason to use *ensure* is that it provides more readable and informative error
messages when things go wrong. Going forward, this will be a major development focus. You will be in control of how much
information is presented in each error, which context it's thrown from, and what introspection capabilities the
exception object will have.

Installation
------------
::

    pip install ensure

Synopsis
--------

.. code-block:: python

    from ensure import ensure

    ensure({1: {2: 3}}).equals({1: {2: 3}})
    ensure({1: {2: 3}}).is_not_equal_to({1: {2: 4}})
    ensure(True).does_not_equal(False)
    ensure(1).is_an(int)
    ensure(1).is_in(range(10))
    ensure(True).is_a(bool)
    ensure(True).is_(True)
    ensure(True).is_not(False)

    ensure(range(10)).contains(5)
    ensure(["spam"]).contains_none_of(["eggs", "ham"])
    ensure(["train", "boat"]).contains_one_of(["train"])
    ensure("abcdef").contains_some_of("abcxyz")
    ensure("abcdef").contains_one_or_more_of("abcxyz")
    ensure("abcdef").contains_all_of("acf")
    ensure("abcd").contains_only("dcba")
    ensure("abc").does_not_contain("xyz")
    ensure([1, 2, 3]).contains_no(float)
    ensure(1).is_in(range(10))
    ensure("z").is_not_in("abc")
    ensure(None).is_not_in([])
    ensure(dict).has_attribute('__contains__')

    ensure(1).is_true()
    ensure(0).is_false()
    ensure(None).is_none()
    ensure(1).is_not_none()
    ensure("").is_empty()
    ensure([1, 2]).is_nonempty()
    ensure(1.1).is_a(float)
    ensure(KeyError()).is_an(Exception)
    ensure({x: str(x) for x in range(5)}).is_a_nonempty(dict).of(int).to(str)
    ensure({}).is_an_empty(dict)
    ensure(None).is_not_a(list)

    import re; ensure("abc").matches("A", flags=re.IGNORECASE)
    ensure([1, 2, 3]).is_an_iterable_of(int)
    ensure([1, 2, 3]).is_a_list_of(int)
    ensure({1, 2, 3}).is_a_set_of(int)
    ensure({1: 2, 3: 4}).is_a_mapping_of(int).to(int)
    ensure({1: 2, 3: 4}).is_a_dict_of(int).to(int)
    ensure({1: 2, 3: 4}).is_a(dict).of(int).to(int)
    ensure(10**100).is_numeric()
    ensure(lambda: 1).is_callable()
    ensure("abc").has_length(3)
    ensure(1).is_greater_than(0)
    ensure(0).is_less_than(1)
    ensure(1).is_greater_than_or_equal_to(1)
    ensure(0).is_less_than_or_equal_to(0)

    ensure("{x} {y}".format).called_with(x=1, y=2).equals("1 2")
    ensure("{x} {y}".format).with_args(x=1, y=2).is_a(str)
    ensure(dict).called_with(1, 2).raises(TypeError)
    with ensure().raises(ZeroDivisionError):
        1/0
    with ensure().raises_regex(NameError, "'w00t' is not defined"):
        w00t

Raising custom exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ensure import Ensure

    class MyException(Exception):
        def __init__(self, e):
            pass

    ensure = Ensure(error_factory=MyException)
    ensure("w00t").is_an(int)

    def build_fancy_exception(original_exception):
        return MyException(original_exception)

    ensure = Ensure(error_factory=build_fancy_exception)
    ensure("w00t").is_an(int)

Links
-----
* `Project home page (GitHub) <https://github.com/kislyuk/ensure>`_
* `Documentation (Read the Docs) <https://ensure.readthedocs.org/en/latest/>`_
* `Package distribution (Crate) <https://crate.io/packages/ensure>`_ `(PyPI) <http://pypi.python.org/pypi/ensure>`_

Bugs
~~~~
Please report bugs, issues, feature requests, etc. on `GitHub <https://github.com/kislyuk/ensure/issues>`_.

License
-------
Licensed under the terms of the `Apache License, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_.

.. image:: https://travis-ci.org/kislyuk/ensure.png
        :target: https://travis-ci.org/kislyuk/ensure
.. image:: https://pypip.in/v/ensure/badge.png
        :target: https://crate.io/packages/ensure
.. image:: https://pypip.in/d/ensure/badge.png
        :target: https://crate.io/packages/ensure
