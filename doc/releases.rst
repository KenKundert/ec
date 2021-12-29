Releases
========

Latest development release
--------------------------

    | Version: 1.8.0
    | Released: 2021-11-10

    - rename *eng* to *si*
    - add new *eng* that uses exponential notation with exponent constrained to 
      be a multiple of 3.
    - drop support for Python 2
    - Make more extensive use of unicode


1.8 (2021-11-10)
----------------

    - nits


1.7 (2020-08-18)
----------------

    - mag and ph now consume *x* register rather than duplicate it.
    - implement *lastx*.
    - loosen regular expression that matches numbers to allow scale factor to be optional.
    - Allow typical unicode characters in units °ÅΩƱΩ℧.
    - Add support for comments.
