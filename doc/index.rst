Engineering Calculator
======================

| Author: Ken Kundert <ec@nurdletech.com>
| Date: 2024-08-06
| Version: 1.11


This calculator is noteworthy in that it employs a stack model of computation
(Reverse Polish Notation), it supports numbers with SI scale factors and units,
and uses a text-only user interface.


Installing
----------

Requires Python version 3.6 or later.

Install with::

    pip install --user engineering-calculator

This installs *ec* into ~/.local/bin, which should be added to your path.

Unusually, there is also a man page.  The Python install process no longer 
supports man pages, however you can download it from `its Github repository
<https://raw.githubusercontent.com/KenKundert/ec/master/doc/ec.1>`_.  Place it 
in ``~/.local/man/man1``.


Features
--------

- Text-based interactive interface.
- Stack-based calculation model
- Full scientific/engineering calculator.
- Support SI scale factors and units on inputs and outputs.
- Supports hexadecimal, octal, and binary formats in both programmers and
  Verilog notation.
- Provides special functionality for electrical engineers.


Examples
--------

Invoke engineering calculator and compute the value of a resistor by dividing
the voltage difference across the resistor by the current through it::

    > ec
    0: 2.5V 250mV - 1mA /
    2.25k:

Here a hexadecimal number is converted to and from decimal::

    > ec
    0: 'hFF
    255: vhex
    'h00ff:

In this example, a frequency is converted to radians and saved into the variable
*omega*, which is then used to compute the impedance of an inductor and
capacitor::

    > ec
    0: 1MHz 2pi * =omega
    6.2832M: 100nH *
    628.32m: 1 10nF omega * /
    15.915:


Issues
------

Please ask questions or report problems on `Github
<https://github.com/KenKundert/engineering_calculator/issues>`_.


Documentation
-------------

.. toctree::
   :maxdepth: 1

   user
   reference
   releases

*  :ref:`genindex`
