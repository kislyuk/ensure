Changes for v1.0.0 (2019-10-30)
===============================

-  Add contains_key, an alias for has_key

-  Document PicklingError for ensure_annotations in multiprocessing
   (#32)

-  Package is stable

Changes for v0.8.2 (2019-01-14)
===============================

-  Fix version range compat error with collections.abc

Changes for v0.8.1 (2019-01-14)
===============================

-  Import ABCs from collections.abc. Fixes #27.

Changes for v0.8.0 (2019-01-14)
===============================

-  Return type of the incorrect value in EnsureError (#28)

-  Move implmentation into submodule to clean up namespace

Changes for v0.6.2 (2016-05-27)
===============================
Length assertion helpers

Changes for v0.6.1 (2016-05-26)
===============================
Remove unneeded dependency

Changes for v0.6.0 (2016-05-26)
===============================
- Pass format args directly to format in or_raise (may need further work to pass custom args to factory)
- Changes to test infrastructure: linter, etc.

Changes for v0.5.0 (2016-03-04)
===============================
- Add ``.satisfies(predicate, *args)`` (#16).

Changes for v0.4.0 (2016-02-04)
===============================
- Add .also and expand use of .which predicate chaining proxies (#15).

Changes for v0.3.3 (2015-11-06)
===============================
- Add Ensure.is_none_or (#13).

Changes for v0.3.2 (2015-05-27)
===============================
- Include requirements.txt.

Changes for v0.3.1 (2015-05-27)
===============================
- Build universal wheel.

Changes for v0.3.0 (2015-05-27)
===============================
- Add numeric string methods (#12).

Changes for v0.2.2 (2014-07-30)
===============================
- Refactor function annotation enforcement to accommodate extensions (#11).
- Improve handling of bound methods.

Changes for v0.2.1 (2014-06-28)
===============================
- Fix issue with function annotation enforcement in keyword-only arguments (#7).
- Further performance improvements to function annotation enforcement (ensure_annotations).

Changes for v0.2.0 (2014-06-16)
===============================
- Major performance improvements to function annotation enforcement (ensure_annotations). (#4, #5). Thanks to @harrisonmetz.

Changes for v0.1.9 (2014-06-14)
===============================
- Fix issue with keyword arguments used as positionals by the caller (#1). Thanks to @harrisonmetz.

Changes for v0.1.8 (2014-02-17)
===============================
- Speed up function annotation enforcement.

Changes for v0.1.7 (2014-02-15)
===============================
- Work around PyPI documentation rendering issue.

Changes for v0.1.6 (2014-02-15)
===============================
- Begin tracking changes in changelog.
- Add support for function annotation enforcement.
