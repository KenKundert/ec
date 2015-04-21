ec: An Engineering Calculator
=============================

This calculator is noteworthy in that it employs a stack model of computation 
(Reverse Polish Notation), it supports numbers with SI scale factors and units, 
and uses a text-only user interface.

Requires Python version 2.6 or later or version of Python 3.3 or later, 
including the docutils package.  On Redhat systems, you can get these 
dependencies by running as root::

   # yum install python python-setuptools python-docutils

or

   # yum install python3 python3-setuptools python3-docutils

Use ``pacman -S`` rather than ``yum install`` on Arch Linux or ``apt-get`` 
rather than ``yum`` on Ubuntu.

If you do not have root access or Python is not available through yum, you
can install it (not as hard as it sounds, see INSTALLING), or you can use ec0, a
slightly less capable version of ec.

More information on both ec and ec0 can be found at `NurdleTech 
<http://www.nurdletech.com/ec.html>`_ .

To get the source code::

   $ git clone git://github.com/KenKundert/ec.git

Once cloned, you can get the latest updates using::

   $ git pull

Alternatively, you can download a zip file from::

   https://github.com/KenKundert/ec/archive/master.zip

If you go this route, you will have to unzip the file using the unzip command.

To run the regression tests::

   $ ./test

To install::

   $ ./install

This installs *ec* in ``~/.local``. Be sure to add ``~/.local/bin`` to your 
PATH.  

To read the EC manual::

   $ man ec

To run EC::

   $ ec
   0:

What follows is a brief tour of EC:

To perform operations in EC, you first enter the numbers, then the operators.  
In particular, as you enter the numbers they are pushed onto the stack. The 
operators then take numbers from the stack and replace them with the result.  
The operations are performed immediately and there is no use of parentheses to 
group calculations. Any intermediate results are stored on the stack until 
needed.

To add two numbers::

   0: 4 5 +
   9:

The prompt displays the value of the x-register.

You can string together an arbitrarily long calculation on a single line::

   0: 4 5 + 6 7 + *
   117:

Or, you can string a long calculation over multiple lines (this calculates the 
value of two parallel 100 ohm resistors)::

   0: 100
   100: 100
   100: ||
   50:

Select operators can be entered without preceding them with a space if they 
follow a number or a name. For example::

   0: 4 5* 6 5+ *
   220:

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

EC supports units, but in a relatively conservative way. You can enter them
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
    h 2pi / 'J-s' =hbar

This tells EC to use 6 digits of resolution and predefines *hbar* as a constant.
The local start up file ('./.ecrc') or the file given as a command line argument
is generally used to give more project specific initializations. For example, in
a directory where you are working on a PLL design you might have an './.ecrc'
file with the following contents::

    88.3uSiemens =kdet
    9.1G 'Hz/V' =kvco
    2 =m
    8 =n
    1.4pF =cs
    59.7pF =cp
    2.2kOhms =rz

EC also takes commands from the command line. For example::

   $ ec -x "125mV 67uV / db"
   65.417

The ``-x`` tells ec to print out the value of the *x* register when it 
terminates. Without it you would not see the result.

EC prints back-quoted strings while interpolating the values of registers and 
variables when requested. For example::

   $ ec 'degs 500 1000 rtop "V/V" `Gain = $0 @ $1.`'
   Gain = 1.118 KV/V @ 26.565 degs.

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
