Releases
========

Latest development release
--------------------------
| Version: 1.11
| Released: 2024-08-06


1.11 (2024-08-06)
-----------------
- add readline support (thanks to Jason Wang [wang-borong])


1.10 (2022-12-27)
-----------------
- add caching for bitcoin prices


1.9 (2022-01-04)
----------------
- add :ref:`unit conversions <unit conversions>`.
- add bitcoin quotes via :ref:`unit conversions <unit conversions>`.
- allow Bitcoin Unicode characters (Ƀ and ș) in units.
- rename *eng* to *si*.
- add new *eng* that uses exponential notation with exponent constrained to be 
  a multiple of 3.
- drop support for Python 2.
- make more extensive use of Unicode.


1.8 (2021-11-10)
----------------

- nits


1.7 (2020-08-18)
----------------

- mag and ph now consume *x* register rather than duplicate it.
- implement *lastx*.
- loosen regular expression that matches numbers to allow scale factor to be optional.
- allow typical Unicode characters in (°, Å, Ω, Ʊ, Ω, and ℧) in units.
- add support for comments.
