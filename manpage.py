#!/usr/bin/env python
# encoding: utf8
# Convert the restructured text version of the manpage to a nroff manpage file.

from actions import (
    actionsToUse as actions
  , Constant, documentIntegers, documentVerilogIntegers, documentComplexNumbers
)
from calculator import versionDate, versionNumber
from docutils.core import publish_string
from docutils.writers import manpage
from textwrap import dedent
import re

# Remove duplicates from action list
sansDups = []
for action in actions:
    if action not in sansDups:
        sansDups.append(action)
actions = sansDups


# Document {{{1
document = r"""{
    ====
     ec
    ====

    ----------------------
    engineering calculator
    ----------------------

    :Author: Ken Kundert <ec@nurdletech.com>
    :Date: {date}
    :Version: {version}
    :Manual section: 1

    .. :Copyright: public domain
    .. :Manual group: Utilities


    SYNOPSIS
    ========
    **ec** [*options*] [*scripts* ...]


    OPTIONS
    =======
    -i, --interactive    Open an interactive session.
    -s <file>, --startup <file>
                         Run commands from file to initialize calculator before
                         any script or interactive session is run, stack is
                         cleared after it is run.
    -c, --nocolor        Do not use colors in the output.
    -v, --verbose        Narrate the execution of any scripts.
    -V, --version        Print the ec version information.
    -h, --help           Print the usage and exit.


    DESCRIPTION
    ===========
    **ec** is a stack-based (RPN) engineering calculator with a text-based user 
    interface that is intended to be used interactively.

    If run with no arguments, an interactive session is started.  If arguments
    are present, they are tested to see if they are filenames, and if so, the
    files are opened and the contents are executed as a script.  If they are not
    file names, then the arguments themselves are treated as scripts and
    executed directly. The scripts are run in the order they are specified.  In
    this case an interactive session would not normally be started, but if the
    interactive option is specified, it would be started after all scripts have
    been run.

    The contents of *~/.ecrc*, *./.ecrc*, and the start up file will be run upon 
    start up if they exist, and then the stack is cleared.


    STACK
    =====

    As you enter numbers they are pushed onto a stack.  The most recent member
    of the stack is referred to as the *x* register and the second most recent
    is the *y* register.  All other members of the stack are unnamed.  Operators
    consume numbers off the stack to use as operands and then they push the
    results back on the stack.  The operations are performed immediately and
    there is no use of parentheses to group calculations.  Any intermediate
    results are stored on the stack until needed.  For example,

       |   4
       |   6
       |   +

    In this case 4 gets pushed on to the stack first to become *x*. Then 6 gets
    pushed on to the stack to become *x*, which makes 4 *y*. Finally, + pulls
    both off the stack, sums them, and then pushes the result of 10 back onto
    the stack.  The stack is left with only one number on it, 10.

    After each line **ec** responds by printing the value of the *x* register.  
    Thus the above example would actually look like this:

       |   **0**: 4
       |   **4**: 6
       |   **6**: +
       |   **10**:

    The benefit of the stack is that it allows you to easily store temporary
    results while you perform your calculation. For example, to evaluate (34 -
    61)*(23 - 56) you would use:

       |   **0**: 34
       |   **34**: 61
       |   **61**: -
       |   **-27**: 23
       |   **23**: 56
       |   **56**: -
       |   **-33**: *
       |   **891**:

    Notice that you entered the numbers as you saw them in the formula you were
    evaluating, and there was no need to enter parentheses, however the
    operators were rearranged in order to express the precedence of the
    operations.

    It is not necessary to type enter after each number or operator. You can
    combine them onto one line and just type enter when you would like to see
    the result:

       |   **0**: 34 61 - 23 56 - *
       |   **891**:

    Furthermore, it is not necessary to type a space between a number and most
    operators. For example, the above could be entered as:

       |   **0**: 34 61- 23 56- *
       |   **891**:

    You can print the entire stack using *stack*, and clear it using *clstack*.
    For example,

       |   **0**: 1 2 3 stack
       |         \  3
       |      *y*: 2
       |      *x*: 1
       |   **3**: clstack
       |   **0**: stack
       |   **0**:


    REAL NUMBERS
    ============

    Numbers can be entered using normal integer, floating point, and scientific
    notations. For example,

       |   42
       |   3.141592
       |   5,439,749.97
       |   2.998e8
       |   13.80651e-24

    In addition, you can also use the normal SI scale factors to represent
    either large or small numbers without using scientific notation.

       Y
            1e24 (yotta)
       Z
            1e21 (zetta)
       E
            1e18 (exa)
       P
            1e15 (peta)
       T
            1e12 (terra)
       G
            1e9 (giga)
       M
            1e6 (mega)
       k, K
            1e3 (kilo)
       \_
            unity (1)
       m
            1e-3 (milli)
       u
            1e-6 (micro)
       n
            1e-9 (nano)
       p
            1e-12 (pico)
       f
            1e-15 (fempto)
       a
            1e-18 (atto)
       z
            1e-21 (zepto)
       y
            1e-24 (yocto)

    For example, 10M represents 1e7 and 8.8p represents 8.8e-12.

    Optionally, numbers can be combined with simple units. For example,

       |   10KHz
       |   3.16pF
       |   2.5_V
       |   4.7e-10F

    Units are only allowed after a scale factor or an exponent, and the units 
    are optional. In this way, 1m represents 1e-3 rather than 1 meter. If you 
    wish to enter 1 meter, use 1_m. The underscore is the unity scale factor.

    In this case the units must be simple identifiers (must not contain special 
    characters). For complex units, such as "rads/s", or for numbers that do not 
    have scale factors, it is possible to attach units to a number in the *x* 
    register by entering a quoted string.

       |   **0**: 6.626e-34
       |   **662.6e-36**: "J-s"
       |   **662.6e-36 J-s**: 50k "V/V"
       |   **50 KV/V**:

    The dollar sign ($) is a special unit that is given before the number.

       |    $100K

    **ec** takes a conservative approach to units. You can enter them and it
    remembers them, but they do not survive any operation where the resulting
    units would be in doubt.  In this way it displays units when it can, but
    should never display incorrect or misleading units. For example:


       |   **0**: 100MHz
       |   **100 MHz**: 2pi*
       |   **628.32M**:

    You can display real numbers using one of three available formats, *fix*,
    *sci*, or *eng*. These display numbers using fixed point notation (a fixed
    number of digits to the right of the decimal point), scientific notation (a
    mantissa and an exponent), and engineering notation (a mantissa and an SI
    scale factor).  You can optionally give an integer immediately after the
    display mode to indicate the desired precision.  For example,

       |   **0**: 1000
       |   **1K**: fix2
       |   **1000.00**: sci3
       |   **1.000e+03**: eng4
       |   **1K**: 2pi*
       |   **6.2832K**:

    Notice that scientific notation always displays the specified number of
    digits whereas engineering notation suppresses zeros at the end of the
    number.

    When displaying numbers using engineering notation, **ec** does not use the
    full range of available scale factors under the assumption that the largest
    and smallest would be unfamiliar to most people. For this reason, **ec**
    only uses the most common scale factors when outputting numbers (T, G, M, K,
    m, u, n, p, f, a).

    {integers}

    {complexNumbers}


    CONSTANTS
    =========

    **ec** provides several useful mathematical and physical constants that are
    accessed by specifying them by name. Several of the constants have both MKS 
    and CGS forms (ec uses ESU-CGS). You can set which version you want by 
    setting the desired unit system as follows:

       |   **0**: mks
       |   **0**: h
       |   **662.61e-36 J-s**: k
       |   **13.806e-24 J/K**: cgs
       |   **13.806e-24 J/K**: h
       |   **6.6261e-27 erg-s**: k
       |   **138.06 aerg/K**:

    Notice that the unit-system is sticky, meaning that it remains in force 
    until explicitly changed. 'mks' is the default unit system.

    The physical constants are given in base units (meters, grams, seconds).  
    For example, the mass of an electron is given in grams rather than kilograms 
    as would be expected for MKS units.  Similarly, the speed of light is given 
    in meters per second rather than centimeters per second as would be expected 
    of CGS units.  This is necessary so that numbers are not displayed with two 
    scale factors (ex. 1 mkg).  Thus, it may be necessary for you to explicitly 
    convert to kg (MKS) or cm (CGS) before using values in formulas that are 
    tailored for one specific unit system.

    The 2014 NIST values are used.  The available constants include:

    {constantsTable}

    As an example of using the predefined constants, consider computing the
    thermal voltage, kT/q.

       |   **0**: k 27 0C + * q/ "V"
       |   **25.865 mV**:


    VARIABLES
    =========

    You can store the contents of the *x* register to a variable by using an
    equal sign followed immediately by the name of the variable. To recall it,
    simply use the name. For example,

       |   **0**: 100MHz =freq
       |   **100 MHz**: 2pi* "rads/s" =omega
       |   **628.32 Mrads/s**: 1pF =cin
       |   **1 pF**: 1 omega cin* /
       |   **1.5915K**:

    You can display all known variables using *vars*. If you did so immediately 
    after entering the lines above, you would see:

       |   **1.5915K**: vars
       |     *Rref*: 50 Ohms
       |     *cin*: 1 pF
       |     *freq*: 100 MHz
       |     *omega*: 628.32 Mrads/s

    Choosing a variable name that is the same as a one of a built-in command or
    constant causes the built-in name to be overridden. Be careful when doing
    this as once a built-in name is overridden it can no longer be accessed. 

    Notice that a variable *Rref* exists that you did not create. This is a
    predefined variable that is used in dBm calculations. You are free to change
    its value if you like.


    USER-DEFINED FUNCTIONS
    ======================

    You can define functions in the following way::

       ( ... )name

    Here '(' starts the function definition and ')name' ends it. The name must 
    be immediately adjacent to the name. The '...' represents a sequence of 
    calculator actions. For example:

        |   **0**: (2pi * "rads/s")to_omega
        |   **0**: (2pi / "Hz")to_freq
        |   **0**: 100MHz
        |   **100 MHz**: to_omega
        |   **628.32 Mrads/s**: to_freq
        |   **100 MHz**:

    The actions entered while defining the function are not evaluated until the 
    function itself is evaluated.

    Once defined, you can review your function with the *vars* command. It shows 
    both the variable and the function definitions:

        |     *Rref*: 50 Ohms
        |     *to_freq*: (2pi / "Hz")
        |     *to_omega*: (2pi * "rads/s")

    The value of the functions are delimited with parentheses.


    OPERATORS, FUNCTIONS, NUMBERS and COMMANDS
    ==========================================

    In the following descriptions, optional values are given in brackets ([])
    and values given in angle brackets (<>) are not to be taken literally (you
    are expected to choose a suitable value). For example "fix[<*N*>]" can
    represent "fix" or "fix4", but not "fixN".

    For each action that changes the stack a synopsis of those changes is given 
    in the form of two lists separated by ``=>``. The list on the left 
    represents the stack before the action is applied, and the list on the right 
    represents the stack after the action was applied. In both of these lists, 
    the *x* register is given first (on the left). Those registers that are 
    involved in the action are listed explicitly, and the rest are represented 
    by ``...``. In the before picture, the names of the registers involved in 
    the action are simply named. In the after picture, the new values of the 
    registers are described. Those values represented by ``...`` on the right 
    side of ``=>`` are the same as represented by ``...`` on the left, though 
    they may have moved. For example::

        x, y, ... => x+y, ...

    This represents addition. In this case the values in the *x* and *y* 
    registers are summed and placed into the *x* register. All other values move 
    to the left one place.

    {actions}


    HELP
    ====

    You can use help to get a summary of the various features available in EC
    along with a short summary of each feature. For more detailed information,
    you can use '?'.  If you use '?' you will get a list of all available help
    topics. If you use '?<*topic*>' where *topic* us either a symbol or a
    name, you will get a detailed description of that topic.


    INITIALIZATION
    ==============

    At start up **ec** reads and executes commands from files.  It first tries
    '~/.ecrc' and runs any commands it contains if it exists.  It then tries
    './.ecrc' if it exists.  Finally it runs the startup file specified on the
    command line (with the **-s** or **--startup** option).  It is common to put
    your generic preferences in '~/.exrc'.  For example, if your are an astronomer 
    with a desire for high precision results, you might use:

       |   eng6
       |   6.626070e-27 "erg-s" =h       # Planck's constant in CGS units
       |   1.054571800e-27 "erg-s" =hbar # Reduced Planck's constant in CGS units
       |   1.38064852e-16 "erg/K" =k     # Boltzmann's constant in CGS units

    This tells **ec** to use 6 digits of resolution and redefines *h* and *hbar* 
    so that they are given in CGS units. The redefining of the names *h*, 
    *hbar*, and *k* would normally cause **ec** to print a warning, but such 
    warnings are suppressed when reading initialization files and scripts.

    After all of the startup files have been processed, the stack is cleared.

    A typical initialization script (~/.ecrc) for a circuit designer might be:

       |   # Initialize Engineering Calculator
       |   27 "C" =T               # ambient temperature
       |   (k T 0C + * q/ "V")vt   # thermal voltage
       |   (2pi* "rads/s")tw       # to omega - converts Hertz to rads/s
       |   (2pi/ "Hz")tf           # to freq - converts rads/s to Hertz


    SCRIPTING
    =========

    Command line arguments are evaluated as if they were typed into an 
    interactive session with the exception of filename arguments.  If an 
    argument corresponds to an existing file, the file treated as a script, 
    meaning it is is opened its contents are evaluated.  Otherwise, the argument 
    itself is evaluate (often it needs to be quoted to protect its contents from 
    being interpreted by the shell). When arguments are given the calculator by 
    default does not start an interactive session. For example: to compute an RC 
    time constant you could use:

       | $ ec 22k 1pF*
       | 22n

    Notice that the \* in the above command is interpreted as glob character, 
    which is generally not what you want, so it is often best to quote the 
    script:

       | $ ec '22k 1pF*'
       | 22n

    Only the calculator commands would be quoted in this manner. If you included 
    a file name on the command line to run a script, it would have to be given 
    alone.  For example, assume that the file 'bw' exists and contains '* 2pi* 
    recip "Hz"'. This is a script that assumes that the value of R and C are 
    present in the *x* and *y* resisters, and then computes the 3dB bandwith of 
    the corresponding RC filter. You could run the script with:

       | $ ec '22k 1pF' bw
       | 7.2343 MHz

    Normally *ec* only prints the value of the *x* register and only as it 
    exits.  It is possible to get more control of the output using back-quoted 
    strings.  For example:

       | $  ec '\`Hello world!\`'
       | Hello world!
       | 0

    Whatever is found within back-quotes is printed to the output. Notice that 
    the value of the *x* register is also output, which may not be desired when 
    you are generating your own output. You can stop the value of the *x* 
    register from being printed by finishing with the *quit* command, which 
    tells *ec* to exit immediately:

       | $  ec '\`Hello world!\` quit'
       | Hello world!

    You can add the values of registers and variables to your print statements.
    *$N* prints out the value of register *N*, where 0 is the *x* register,
    1 is the *y* register, etc. *$name* will print the value of a variable
    with the given name. Alternatively, you can use *${{N*}} and *${{name*}} to
    disambiguate the name or number. To print a dollar sign, use *$$*.  To
    print a newline or a tab, use *\\n* and *\\t*. For example,

       |   **0**: 100MHz =freq
       |   **100 MHz**: 2pi* "rads/s"
       |   **628.32 Mrads/s**: \`$freq corresponds to $0.\`
       |   100 MHz corresponds to 628.32 Mrads/s.
       |   **628.32 Mrads/s**:

    To illustrate its use in a script, assume that a file named *lg* exists and
    contains a calculation for the loop gain of a PLL,

       |   # computes and displays loop gain of a frequency synthesizer
       |   # x register is taken to be frequency
       |   =freq
       |   88.3u "V/per" =Kdet  # gain of phase detector
       |   9.07G "Hz/V" =Kvco   # gain of voltage controlled oscillator
       |   2 =M                 # divide ratio of divider at output of VCO
       |   8 =N                 # divide ratio of main divider
       |   2 =F                 # divide ratio of prescalar
       |   freq 2pi* "rads/s" =omega
       |   Kdet Kvco* omega/ M/ =a
       |   N F* =f
       |   a f* =T
       |   \`Open loop gain = $a\\nFeedback factor = $f\\nLoop gain = $T\`
       |   quit

    When reading scripts from a file, the '#' character introduces a comment. It 
    and anything that follows is ignored until the end of the line.

    Notice that the script starts by saving the value in the *x* register to the
    variable *freq*. This script would be run as:

       |   $ ec 1KHz lg
       |   Open loop gain = 63.732
       |   Feedback factor = 16
       |   Loop gain = 1.0197K

    The first argument does not correspond to a file, so it is executed as a
    script.  It simply pushes 1KHz onto the stack. The second argument does
    correspond to a file, so its contents are executed. The script ends with a
    print command, so the results are printed to standard output as the script
    terminates.

    One issue with command line scripting that you need to be careful of is that 
    if an argument is a number with a leading minus sign it will be mistaken to 
    be a command line option. To avoid this issue, specify the number without 
    the minus sign and follow it with *chs*.  Alternatively, you can embed the 
    number in quotes but add a leading space.  For example,

       |   $ ec -30 dbmv
       |   ec: -30 dbmv: unknown option.
       |   $ ec 30 chs dbmv
       |   10 mV
       |   $ ec ' -30' dbmv
       |   10 mV


    INITIALIZATION SCRIPTS
    ======================

    You can use scripts to preload in a set of useful constants and function 
    that can then be used in interactive calculations. To do so, use the **-i** 
    or *--interactive* command line option. For example, replace the earlier 
    'lg' script with the following:

       |   88.3u "V/per" =Kdet
       |   9.07G "Hz/V" =Kvco
       |   2 =M
       |   8 =N
       |   2 =F
       |   (N F* recip)f
       |   (2pi * Kdet * Kvco* M*)a
       |   (a f*)T
       |   clstack

    Now run:

       |   $ ec -i lg
       |   0: 1kHz T
       |   629.01M:

    Doing so runs lg, which loads values into the various variables, and then 
    they can be accessed in further calculations.

    Notice that the script ends with *clstack* so that you start fresh in your 
    interactive session. It simply clears the stack so that the only effect of 
    the script is to initialize the variables.  Using **-s** or **--startup** 
    does this for you automatically.

    Alternatively, you can put the constants you wish to predeclare in 
    *./.ecrc*, in which case they are automatically loaded whenever you invoke 
    *ec* in the directory that contains the file.  Similarly, placing constants 
    in *~/.ecrc* causes them to be declared for every invocation of *ec*.


    DIAGNOSTICS
    ===========

    If an error occurs on a line, an error message is printed and the stack is
    restored to the values it had before the line was entered. So it is almost
    as if you never typed the line in at all.  The exception being that any
    variables or modes that are set on the line before the error occurred are
    retained.  For example,

        |   **0**: 1KOhms =r
        |   **1 KOhms**: 100MHz =freq 1pF = c
        |   =: unrecognized
        |   **1 KOhms**: stack
        |     *x*: 1 KOhms
        |   **1 KOhms**: vars
        |     *Rref*: 50 Ohms
        |     *freq*: 100MHz
        |     *r*: 1 KOhms

    The error occurred when trying to assign a value to *c* because a space was
    accidentally left between the equal sign and the variable name.  Notice that
    100MHz was saved to the variable *freq*, but the stack was restored to the
    state it had before the offending line was entered.


    SEE ALSO
    ========
    bc, dc
}"""

# Integers {{{1
integerSectionWithVerilog = r"""{
    INTEGERS
    ========

    You can enter integers in either hexadecimal (base 16), decimal (base 10),
    octal (base 8), or binary (base 2). You can use either programmers notation
    (leading 0) or Verilog notation (leading ') as shown in the examples below:

        0xFF
            hexadecimal
        99
            decimal
        0o77
            octal
        0b1101
            binary
        'hFF
            Verilog hexadecimal
        'd99
            Verilog decimal
        'o77
            Verilog octal
        'b1101
            Verilog binary

    Internally, **ec** represents all numbers as double-precision real numbers.
    To display them as decimal integers, use *fix0*. However, you can display
    the numbers in either base 16 (hexadecimal), base 10 (decimal), base 8
    (octal) or base 2 (binary)  by setting the display mode.  Use either *hex*,
    *fix0*, *oct*, *bin*, *vhex*, *vdec*, *voct*, or *vbin*. In each of
    these cases the number is rounded to the closest integer before it is
    displayed. Add an integer after the display mode to control the number of
    digits. For example:

       |   **0**: 1000
       |   **1K**: hex
       |   **0x3b8**: hex8
       |   **0x000003b8**: hex0
       |   **0x3b8**: voct
       |   **'o1750**:
}"""

integerSectionWithoutVerilog = r"""{
    INTEGERS
    ========

    You can enter integers in either hexadecimal (base 16), decimal (base 10),
    octal (base 8), or binary (base 2) using programmers notation as shown in 
    the examples below:

        0xFF
            hexadecimal
        99
            decimal
        0o77
            octal
        0b1101
            binary

    Internally, **ec** represents all numbers as double-precision real numbers.
    To display them as decimal integers, use *fix0*. However, you can display
    the numbers in either base 16 (hexadecimal), base 10 (decimal), base 8
    (octal) or base 2 (binary)  by setting the display mode.  Use either *hex*,
    *fix0*, *oct*, or *bin*. In each of these cases the number is rounded to the 
    closest integer before it is displayed. Add an integer after the display 
    mode to control the number of digits. For example:

       |   **0**: 1000
       |   **1K**: hex
       |   **0x3b8**: hex8
       |   **0x000003b8**: hex0
       |   **0x3b8**: oct
       |   **0o1750**:
}"""

if documentIntegers:
    if documentVerilogIntegers:
        integerSection = integerSectionWithVerilog[1:-1]
    else:
        integerSection = integerSectionWithoutVerilog[1:-1]
else:
    integerSection = ''


# Complex Numbers {{{1
complexNumberSection = r"""{
    COMPLEX NUMBERS
    ===============

    **ec** provides limited support for complex numbers. Two imaginary constants
    are available that can be used to construct complex numbers, *j* and
    *j2pi*. In addition, two functions are available for converting complex
    numbers to real, *mag* returns the magnitude and *ph* returns the phase.
    They are unusual in that they do not replace the value in the *x* register
    with the result, instead they simply push either the magnitude of phase into
    the *x* register, which pushes the original complex number into the *y*
    register. For example,

       |   **0**: 1 j +
       |   **1 + j**: mag
       |   **1.4142**: pop
       |   **1 + j**: ph
       |   **45 degs**: stack
       |      *y*: 1 + j
       |      *x*: 45 degs
       |   **45 degs**:

    You can also add the imaginary unit to real number constants. For example,

       |   **0**: j10M
       |   **j10M**: -j1u *
       |   **10**:

    Only a small number of functions actually support complex numbers; currently
    only *exp* and *sqrt*. However, most of the basic arithmetic operators
    support complex numbers.
}"""

if documentComplexNumbers:
    complexNumberSection = complexNumberSection[1:-1]
else:
    complexNumberSection = ""

# Constants Table {{{1
constants = []
keyWidth = descWidth = 0
for action in actions:
    if isinstance(action, Constant):
        # value = action.action()
        # strip off the key or pattern
        description = action.description.split(':', 1)[1].strip()
        # add the value to the description
        # actually, do not add the value, it makes text too wide and in the case
        # of rand is misleading, also value can be a number, a tuple, a dict, or 
        # a function, would need to accommodate all of these.
        #if value and action.units:
        #    desc = '%s (%s %s)' % (description, value, action.units)
        #elif value:
        #    desc = '%s (%s)' % (description, value)
        #elif action.units:
        #    desc = '%s (%s)' % (description, action.units)
        #else:
        #    desc = description
        if action.units:
            description = '%s (%s)' % (description, action.units)
        pair = (action.key, description)
        if pair not in constants:
            constants += [pair]
        keyWidth = max(keyWidth, len(action.key))
        descWidth = max(descWidth, len(description))

# convert the constants into a restructured text table
#delimiter = '%s %s' % (keyWidth*'=', descWidth*'=')
#constants = [delimiter] + [
#    "{const[0]:{kw}} {const[1]:{dw}}".format(
#        const=constant, kw=keyWidth, dw=descWidth
#    ) for constant in constants
#] + [delimiter]
# convert the constants into a restructured text definition list
constants = [
    "    %s\n        %s" % constant for constant in constants
]
constantsTable = '\n'.join(constants)

# Actions {{{1
italicsRegex = re.compile(r'#\{([^}]+)\}')
boldRegex = re.compile(r'@\{([^}]+)\}')
def formatText(text, indent=''):
    '''
    Process the simple in-line macros that are allowed in the text:
    #{text}: italics
    @{text}: bold
    \verb{
        text
    }: do not fill
    '''
    # get rid of leading indentation and break into individual lines
    lines = dedent(text).strip().splitlines()
    gatheredLines = []
    fill = True
    for line in lines:
        if line.strip() == r'\verb{':
            # start of no-fill region
            gatheredLines += ['']
            fill = False
        elif line.strip() == '}':
            # end of no-fill region
            gatheredLines += ['']
            fill = True
        else:
            line = italicsRegex.sub(r'*\1*', line)
            line = boldRegex.sub(r'**\1**', line)
            if fill:
                gatheredLines += [indent+line]
            else:
                gatheredLines += [indent+'    |   '+line]
    return '\n'.join(gatheredLines) + '\n'

def formatDescription(desc):
    '''
    Separate the key/name from the description, quote the key/name, format the 
    description, rejoin them, and return the results.
    '''
    components = desc.split(':', 1)
    if len(components) == 1:
        return formatText(components[0])
    name, description = components
    name = italicsRegex.sub(r'\1', name)
    name = boldRegex.sub(r'\1', name)
    name = '``%s``' % name.strip()
    description = formatText(description.strip())
    return "%s: %s" % (name, description)

def formatSynopsis(synopsis):
    '''
    Quote the synopsis while pulling out the variables and italicize them.
    '''
    return '    ::\n\n        ' + italicsRegex.sub(r'\1', synopsis) + '\n'

actionText = []
for action in actions:
    if action.description:
        if hasattr(action, 'category'):
            text = formatDescription(action.description % (action.__dict__))
            text = [text + '-'*len(text) + '\n']
        else:
            summary = action.getSummary()
            synopsis = action.getSynopsis()
            aliases = action.getAliases()
            if aliases:
                if len(aliases) > 1:
                    aliases = 'aliases: %s' % ', '.join(aliases)
                else:
                    aliases = 'alias: %s' % ', '.join(aliases)
            else:
                aliases = ''
            text = [formatDescription(action.description % (action.__dict__))]
            text += [formatText(summary, '    ')]
            if synopsis:
                text += [formatSynopsis(synopsis)]
            if aliases:
                text += [formatText(aliases, '    ')]
        actionText += text

# Generate restructured text {{{1
def write(manFileName, rstFileName=None):
    rst = dedent(document[1:-1]).format(
        date=versionDate
      , version=versionNumber
      , integers=dedent(integerSection)
      , complexNumbers=dedent(complexNumberSection)
      , constantsTable=constantsTable
      , actions='\n'.join(actionText)
    )
    # generate reStructuredText file (only used for debugging)
    if rstFileName:
        with open(rstFileName, 'w') as outputFile:
            outputFile.write(rst)

    # Generate man page
    with open(manFileName, 'wb') as outputFile:
        text = publish_string(rst, writer=manpage.Writer())
        outputFile.write(text)

if __name__ == '__main__':
    write('ec.1', 'ec.rst')

# vim: set sw=4 sts=4 tw=80 formatoptions=ntcqwa12 et spell: 
