ec: An Engineering Calculator
=============================

Ths calculator is noteworthy in that it employs a stack model of computation 
(Reverse Polish Notation), it supports numbers with SI scale factors and units, 
and uses a text-only user interface.


Installing
----------

| Version: 1.5.0
| Released: 2017-03-19

.. image:: https://img.shields.io/travis/KenKundert/ec/master.svg
    :target: https://travis-ci.org/KenKundert/ec

.. image:: https://img.shields.io/pypi/v/engineering_calculator.svg
    :target: https://pypi.python.org/pypi/engineering_calculator

.. image:: https://img.shields.io/pypi/pyversions/engineering_calculator.svg
    :target: https://pypi.python.org/pypi/engineering_calculator

.. image:: https://img.shields.io/pypi/dd/engineering_calculator.svg
    :target: https://pypi.python.org/pypi/engineering_calculator

Install with::

    pip3 install engineering-calculator --user

Requires Python version 3.3 or later. Also supports Python 2.7 with slightly 
reduced functionality.

Alternatively, you can use ec0, a slightly less capable version of ec that 
supports older versions of python.

More information on both ec and ec0 can be found at `NurdleTech 
<http://www.nurdletech.com/ec.html>`_ .


Installing from Source
----------------------

Installation of the manpage is not completely robust when using pip. If it is 
not working for you, you should install from source.  To get the source code::

   $ git clone https://github.com/KenKundert/ec.git

Once cloned, you can get the latest updates using::

   $ cd ec
   $ git pull

Alternatively, you can download a zip file from `github 
<https://github.com/KenKundert/ec/archive/master.zip>`_.  If you go this route, 
you will have to unzip the file using the unzip command. For example::

   $ wget https://github.com/KenKundert/ec/archive/master.zip
   $ unzip master.zip
   $ mv ec-master ec
   $ cd ec

To run the regression tests::

   $ ./test

To install::

   $ python setup.py install --user

To create and install the manpage, run::

   $ ./manpage.py
   $ mkdir -p ~/.local/man/man1
   $ cp ec.1 ~/.local/man/man1

To read the EC manual::

   $ man ec

To run EC::

   $ ec
   0:


A Brief Tour of Engineering Calculator
--------------------------------------

To perform operations in EC, you first enter the numbers, then the operators.  
In particular, as you enter the numbers they are pushed onto the stack. The 
operators then take numbers from the stack and replace them with the result.  
The operations are performed immediately and there is no use of parentheses to 
group calculations. Any intermediate results are stored on the stack until 
needed.

To add two numbers::

   0: 4 5 +
   9:

This command first pushes 4 onto the stack, then it pushes 5 on the stack, and 
finally runs the addition operator, which pulls 4 and 5 off the stack and then 
pushes the sum, 9, back onto the stack.  The prompt displays the value of the 
x-register, which is generally the final result from the previous command.

You can string together an arbitrarily long calculation on a single line::

   0: 4 5 + 6 7 + *
   117:

This command demonstrates the power of using a stack for calculations. It first 
computes the sum and places the results on the stack. That result stays on the 
stack while the sum of 6 and 7 is computed, and finally it is used, and 
consumed, in the final multiplication.

Alternately, you can string a calculation over multiple lines (this calculates 
the value of two parallel 100 ohm resistors)::

   0: 100
   100: 100
   100: ||
   50:

Effectively, you only need to type *enter* is when you want to see the result.

Select operators can be entered without preceding them with a space if they 
follow a number or a name. For example::

   0: 4 5* 6 5+ *
   220:

Use *stack* to see the contents of the stack::

   0: 1 2 3 4 5 stack
        1
        2
        3
     y: 4
     x: 5
   5: + stack
        1
        2
     y: 3
     x: 9
   9: + stack
        1
     y: 2
     x: 12
   12: + stack
     y: 1
     x: 14
   14: + stack
     x: 15
   14: -1 stack
     y: 15
     x: -1
   -1:

The stack grows without limit as needed. The bottom two values are the values 
that are generally involved in operations and they are labeled for *x* and *y* 
as an aid to help you understand and predict the basic operation of various 
commands. For example::

   0: 8 2 stack
     y: 8
     x: 2
   2: ytox
   64:

The command name *ytox* is short for 'raise value of *y* register to the value 
in the *x* register'.

You remove a value from the bottom of the stack with *pop*::

   0: 10 -3 stack
     y: 10
     x: -3
   -3: pop
   10: stack
     x: 10

To store a value into a variable, type an equal sign followed by a name. To
recall it, simply use the name::

   0: 100MHz =freq
   100MHz: 2pi* =omega
   628.32M: 1pF =Cin
   1pF: 1 omega/ Cin/
   1.5915K:

Display variables using::

   628.32M: vars
     Cin = 1pF
     Rref = 50 Ohms
     freq = 100MHz
     omega = 628.32M
   628.32M:

*Rref* is a special variable that is set by default to 50 Ohms, but you can 
change its value. It is used in *dBm* calculations.

From the above example you can see that EC supports SI scale factors and units.  
The support for units is relatively conservative.  You can enter them
and it remembers them, but they do not survive any operation other than a
copy. In this way it should never display incorrect or misleading units, however
it displays units when it can. For example::

   0: 100MHz =freq
   100 MHz: 2pi* "rads/s" =omega
   628.32 Mrads/s: vars
     Rref = 50 Ohms
     freq = 100 MHz
     omega = 628.32 Mrads/s
   628.32 Mrads/s: 2pi /
   100M:

Notice that EC captured units on 100MHz and stored them into the memory freq.
Also notice that the units of "rads/s" were explicitly specified, and they were
also captured. Finally, notice that dividing by *2pi* cleared the units.

This simple way of adding units to a number, ex. 100MHz, is somewhat restricted.

* You can only add units after a scale factor, but once you've given the scale 
  factor the units are optional. In this way, 1m represents 1e-3 rather than one 
  meter. If you want to specify one meter, you would use 1_m. The underscore is 
  a scale factor, like m or k. It represents the unity scale factor.

* Units added to the end of a number may consist only of letters and 
  underscores. Digits and special characters like /, ^, \*, -, ( or ) are not 
  allowed.

* You can only add units to number literals. So 100MHz is okay, but 'omega 2pi/ 
  Hz' is not.

You can overcome this limitation by entering a quoted string. Doing so 
interprets the contents of the string as units and applies them to whatever is 
in the *x* register. For example::

   0: 100MHz 2pi* "rads/s"
   628.32 Mrads/s: 2pi / "Hz"
   100 MHz:

   0: 9.8066 "m/s^2"
   9.8066 m/s^2:

Normally units are given after the number, however a dollar sign would be given
immediately before::

   0: $100M
   $100M:

You can enter hexadecimal, octal, or binary numbers, in either traditional
programmers notation or in Verilog notation. For example::

   0: 0xFF
   255: 0o77
   63: 0b1111
   15: 'hFF
   255: 'o77
   63: 'b1111
   15:

You can also display numbers in hexadecimal, octal, or binary in both
traditional or Verilog notation. To do so, use ``hex``, ``oct``, ``bin``, 
``vhex``, ``voct``, or ``vbin``::

   0: 255
   255: hex4
   0x00ff: vbin
   'b11111111:

You can convert voltages into *dBm* using::

   0: 10 vdbm
   30:

You can convert *dBm* into voltage using::

   0: -10 dbmv
   100 mV: 

Both of these assume a load resistance that is contained in memory *Rref*, which 
by default is 50 Ohms.

At start up EC reads and executes commands from files. It first tries '~/.ecrc'
and runs any commands it contains if it exists. It then tries './.ecrc' if it
exists. Finally it runs any files given on the command line. It is common to put
your generic preferences in '~/.exrc'. For example, if your are a physicist with
a desire for high precision results, you might use::

    eng6
    h 2pi / "J-s" =hbar

This tells EC to use 6 digits of resolution and predefines *hbar* as a constant.
The local start up file ('./.ecrc') or the file given as a command line argument
is generally used to give more project specific initializations. For example, in
a directory where you are working on a PLL design you might have an './.ecrc'
file with the following contents::

    88.3uSiemens =kdet
    9.1G "Hz/V" =kvco
    2 =m
    8 =n
    1.4pF =cs
    59.7pF =cp
    2.2kOhms =rz

EC also takes commands from the command line. For example::

   $ ec "125mV 67uV / db"
   65.417

EC prints back-quoted strings while interpolating the values of registers and 
variables when requested. For example::

   $ ec 'degs 500 1000 rtop "V/V" `Gain = $0 @ $1.` quit'
   Gain = 1.118 KV/V @ 26.565 degs.

Normally *ec* prints the value of the x register and exits when it runs out of 
things to do.  The *quit* at the end tells ec to exit immediately. In this way 
the value of the x register is not printed.  Without it you would see the 
magnitude printed twice.

You can define functions with the following syntax: *( ... )name*, where '(' 
starts the function definition, ')name' terminates it, and ... is simply 
a collection of calculator actions. For example::

   0: (2pi * "rads/s")to_omega
   0: (2pi / "Hz")to_freq
   0: 1.4GHz
   1.4 GHz: to_omega
   8.7965 Grads/s: to_freq
   1.4 GHz:

You can get a list of the actions available with::

   0: ?

You can get help on a specific topic, such as //, with::

   0: ?//

You can get a list of the help topics available with::

   0: help

There is much more available that what is described here. For more information,
run::

   $ man ec

You can quit the program using::

   0: quit

(or *:q* or *^D*).

| Enjoy,
|    -Ken
