
Operator, Function, Number and Command Reference
================================================

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

Arithmetic Operators
---------------------

``+``: addition

    The values in the *x* and *y* registers are popped from the
    stack and the sum is placed back on the stack into the *x*
    register.

    ::

        x, y, ... → x+y, ...

``-``: subtraction

    The values in the *x* and *y* registers are popped from the
    stack and the difference is placed back on the stack into the *x*
    register.

    ::

        x, y, ... → x-y, ...

``*``: multiplication

    The values in the *x* and *y* registers are popped from the
    stack and the product is placed back on the stack into the *x*
    register.

    ::

        x, y, ... → x*y, ...

``/``: true division

    The values in the *x* and *y* registers are popped from the stack and
    the quotient is placed back on the stack into the *x* register.  Both
    values are treated as real numbers and the result is a real number. So

        |       **0**: 1 2/
        |       **500m**:


    ::

        x, y, ... → y/x, ...

``//``: floor division

    The values in the *x* and *y* registers are popped from the
    stack, the quotient is computed and then converted to an integer using
    the floor operation (it is replaced by the largest integer that is
    smaller than the quotient), and that is placed back on the stack into
    the *x* register.  So

        |       **0**: 1 2//
        |       **0**:


    ::

        x, y, ... → y//x, ...

``%``: modulus

    The values in the *x* and *y* registers are popped from the stack, the
    quotient is computed and the remainder is placed back on the stack into
    the *x* register.  So

        |       **0**: 14 3%
        |       **2**:

    In this case 2 is the remainder because 3 goes evenly into 14 three
    times, which leaves a remainder of 2.

    ::

        x, y, ... → y%x, ...

``chs``: change sign

    The value in the *x* register is replaced with its negative.

    ::

        x, ... → −x, ...

``recip``: reciprocal

    The value in the *x* register is replaced with its reciprocal.

    ::

        x, ... → 1/x, ...

``ceil``: round towards positive infinity

    The value in the *x* register is replaced with its value rounded
    towards infinity (replaced with the smallest integer greater than its
    value).

    ::

        x, ... → ceil(x), ...

``floor``: round towards negative infinity

    The value in the *x* register is replaced with its value rounded
    towards negative infinity (replaced with the largest integer smaller
    than its value).

    ::

        x, ... → floor(x), ...

``!``: factorial

    The value in the *x* register is replaced with the factorial of its
    value rounded to the nearest integer.

    ::

        x, ... → x!, ...

``%chg``: percent change

    The values in the *x* and *y* registers are popped from the stack and 
    the percent difference between *x* and *y* relative to *y* is pushed 
    back into the *x* register.

    ::

        x, y, ... → 100*(x-y)/y, ...

``||``: parallel combination

    The values in the *x* and *y* registers are popped from the stack and
    replaced with the reciprocal of the sum of their reciprocals.  If the
    values in the *x* and *y* registers are both resistances, both
    elastances, or both inductances, then the result is the resistance,
    elastance or inductance of the two in parallel. If the values are
    conductances, capacitances or susceptances, then the result is the
    conductance, capacitance or susceptance of the two in series.

    ::

        x, y, ... → 1/(1/x+1/y), ...

Powers, Roots, Exponentials and Logarithms
-------------------------------------------

``**``: raise y to the power of x

    The values in the *x* and *y* registers are popped from the
    stack and replaced with the value of *y* raised to the power of
    *x*.

    ::

        x, y, ... → y**x, ...

    aliases: pow,ytox

``exp``: natural exponential

    The value in the *x* register is replaced with its exponential. 
    Supports a complex argument.

    ::

        x, ... → exp(x), ...

    alias: powe

``ln``: natural logarithm

    The value in the *x* register is replaced with its natural logarithm. 
    Supports a complex argument.

    ::

        x, ... → ln(x), ...

    alias: loge

``pow10``: raise 10 to the power of x

    The value in the *x* register is replaced with 10 raised to *x*.

    ::

        x, ... → 10**x, ...

    alias: 10tox

``log``: base 10 logarithm

    The value in the *x* register is replaced with its common logarithm.

    ::

        x, ... → log(x), ...

    aliases: log10,lg

``pow2``: raise 2 to the power of x

    The value in the *x* register is replaced with 2 raised to *x*.

    ::

        x, ... → 2**x, ...

    alias: 2tox

``log2``: base 2 logarithm

    The value in the *x* register is replaced with its base 2 logarithm.

    ::

        x, ... → log2(x), ...

    alias: lb

``sqr``: square

    The value in the *x* register is replaced with its square.

    ::

        x, ... → x**2, ...

``sqrt``: square root

    The value in the *x* register is replaced with its square root.

    ::

        x, ... → sqrt(x), ...

    alias: rt

``cbrt``: cube root

    The value in the *x* register is replaced with its cube root.

    ::

        x, ... → cbrt(x), ...

Trigonometric Functions
------------------------

``sin``: trigonometric sine

    The value in the *x* register is replaced with its sine.

    ::

        x, ... → sin(x), ...

``cos``: trigonometric cosine

    The value in the *x* register is replaced with its cosine.

    ::

        x, ... → cos(x), ...

``tan``: trigonometric tangent

    The value in the *x* register is replaced with its tangent.

    ::

        x, ... → tan(x), ...

``asin``: trigonometric arc sine

    The value in the *x* register is replaced with its arc sine.

    ::

        x, ... → asin(x), ...

``acos``: trigonometric arc cosine

    The value in the *x* register is replaced with its arc cosine.

    ::

        x, ... → acos(x), ...

``atan``: trigonometric arc tangent

    The value in the *x* register is replaced with its arc tangent.

    ::

        x, ... → atan(x), ...

``rads``: use radians

    Switch the trigonometric mode to radians (functions such as *sin*,
    *cos*, *tan*, and *ptor* expect angles to be given in radians;
    functions such as *arg*, *asin*, *acos*, *atan*, *atan2*, and
    *rtop* should produce angles in radians).

``degs``: use degrees

    Switch the trigonometric mode to degrees (functions such as *sin*,
    *cos*, *tan*, and *ptor* expect angles to be given in degrees;
    functions such as *arg*, *asin*, *acos*, *atan*, *atan2*, and
    *rtop* should produce angles in degrees).

Complex and Vector Functions
-----------------------------

``abs``: magnitude of complex number

    The absolute value of the number in the *x* register is pushed onto the
    stack if it is real. If the value is complex, the magnitude is pushed
    onto the stack.

    ::

        x, ... → abs(x), x, ...

    alias: mag

``arg``: phase of complex number

    The argument of the number in the *x* register is pushed onto the
    stack if it is complex. If the value is real, zero is pushed
    onto the stack.

    ::

        x, ... → arg(x), x, ...

    alias: ph

``hypot``: hypotenuse

    The values in the *x* and *y* registers are popped from the stack and 
    replaced with the length of the vector from the origin to the point
    (*x*, *y*).

    ::

        x, y, ... → sqrt(x**2+y**2), ...

    alias: len

``atan2``: two-argument arc tangent

    The values in the *x* and *y* registers are popped from the stack and 
    replaced with the angle of the vector from the origin to the point.

    ::

        x, y, ... → atan2(y,x), ...

    alias: angle

``rtop``: convert rectangular to polar coordinates

    The values in the *x* and *y* registers are popped from the stack and 
    replaced with the length of the vector from the origin to the point 
    (*x*, *y*) and with the angle of the vector from the origin to the 
    point (*x*, *y*).

    ::

        x, y, ... → sqrt(x**2+y**2), atan2(y,x), ...

``ptor``: convert polar to rectangular coordinates

    The values in the *x* and *y* registers are popped from the stack and
    interpreted as the length and angle of a vector and are replaced with
    the coordinates of the end-point of that vector.

    ::

        x, y, ... → x*cos(y), x*sin(y), ...

Hyperbolic Functions
---------------------

``sinh``: hyperbolic sine

    The value in the *x* register is replaced with its hyperbolic sine.

    ::

        x, ... → sinh(x), ...

``cosh``: hyperbolic cosine

    The value in the *x* register is replaced with its hyperbolic cosine.

    ::

        x, ... → cosh(x), ...

``tanh``: hyperbolic tangent

    The value in the *x* register is replaced with its hyperbolic tangent.

    ::

        x, ... → tanh(x), ...

``asinh``: hyperbolic arc sine

    The value in the *x* register is replaced with its hyperbolic arc sine.

    ::

        x, ... → asinh(x), ...

``acosh``: hyperbolic arc cosine

    The value in the *x* register is replaced with its hyperbolic arc
    cosine.

    ::

        x, ... → acosh(x), ...

``atanh``: hyperbolic arc tangent

    The value in the *x* register is replaced with its hyperbolic arc
    tangent.

    ::

        x, ... → atanh(x), ...

Decibel Functions
------------------

``db``: convert voltage or current to dB

    The value in the *x* register is replaced with its value in 
    decibels. It is appropriate to apply this form when 
    converting voltage or current to decibels.

    ::

        x, ... → 20*log(x), ...

    aliases: db20,v2db,i2db

``adb``: convert dB to voltage or current

    The value in the *x* register is converted from decibels and that value
    is placed back into the *x* register.  It is appropriate to apply this
    form when converting decibels to voltage or current.

    ::

        x, ... → 10**(x/20), ...

    aliases: db2v,db2i

``db10``: convert power to dB

    The value in the *x* register is converted from decibels and that
    value is placed back into the *x* register.  It is appropriate to
    apply this form when converting power to decibels.

    ::

        x, ... → 10*log(x), ...

    alias: p2db

``adb10``: convert dB to power

    The value in the *x* register is converted from decibels and that value
    is placed back into the *x* register.  It is appropriate to apply this
    form when converting decibels to voltage or current.

    ::

        x, ... → 10**(x/10), ...

    alias: db2p

``vdbm``: convert peak voltage to dBm

    The value in the *x* register is expected to be the peak voltage of a
    sinusoid that is driving a load resistor equal to *Rref* (a predefined
    variable).  It is replaced with the power delivered to the resistor in
    decibels relative to 1 milliwatt.

    ::

        x, ... → 30+10*log10((x**2)/(2*Rref)), ...

    alias: v2dbm

``dbmv``: dBm to peak voltage

    The value in the *x* register is expected to be a power in decibels
    relative to one milliwatt. It is replaced with the peak voltage of a
    sinusoid that would be needed to deliver the same power to a load
    resistor equal to *Rref* (a predefined variable).

    ::

        x, ... → sqrt(2*10**(x - 30)/10)*Rref), ...

    alias: dbm2v

``idbm``: peak current to dBm

    The value in the *x* register is expected to be the peak current of a
    sinusoid that is driving a load resistor equal to *Rref* (a predefined
    variable).  It is replaced with the power delivered to the resistor in
    decibels relative to 1 milliwatt.

    ::

        x, ... → 30+10*log10(((x**2)*Rref/2), ...

    alias: i2dbm

``dbmi``: dBm to peak current

    The value in the *x* register is expected to be a power in decibels
    relative to one milliwatt. It is replaced with the peak current of a
    sinusoid that would be needed to deliver the same power to a load
    resistor equal to *Rref* (a predefined variable).

    ::

        x, ... → sqrt(2*10**(x - 30)/10)/Rref), ...

    alias: dbm2i

Constants
----------

``pi``: the ratio of a circle's circumference to its diameter

    The value of π (3.141592...) is pushed on the stack into the *x*
    register.

    ::

        ... → π, ...

    alias: π

``2pi``: the ratio of a circle's circumference to its radius

    2π (6.283185...) is pushed on the stack into the *x* register.

    ::

        ... → 2π, ...

    aliases: tau,τ,2π

``rt2``: square root of two

    √2 (1.4142...) is pushed on the stack into the *x* register.

    ::

        ... → √2, ...

``0C``: 0 Celsius in Kelvin

    Zero celsius in kelvin (273.15 K) is pushed on the stack into
    the *x* register.

    ::

        ... → 0C, ...

``j``: imaginary unit (square root of −1)

    The imaginary unit (square root of -1) is pushed on the stack into
    the *x* register.

    ::

        ... → j, ...

``j2pi``: j2π

    2π times the imaginary unit (j6.283185...) is pushed on the stack into
    the *x* register.

    ::

        ... → j*2*pi, ...

    aliases: jtau,jτ,j2π

``k``: Boltzmann constant

    The Boltzmann constant (R/NA or 1.38064852×10⁻²³ J/K [mks] or
    1.38064852×10⁻¹⁶ erg/K [cgs]) is pushed on the stack into the *x*
    register.

    ::

        ... → k, ...

``h``: Planck constant

    The Planck constant *h* (6.626070×10⁻³⁴ J-s [mks] or 6.626070×10⁻²⁷ erg-s [cgs])
    is pushed on the stack into the *x* register.

    ::

        ... → h, ...

``q``: elementary charge (the charge of an electron)

    The elementary charge (the charge of an electron or 1.6021766208×10⁻¹⁹ C
    [mks] or 4.80320425×10⁻¹⁰ statC [cgs]) is pushed on the stack into the
    *x* register.

    ::

        ... → q, ...

``c``: speed of light in a vacuum

    The speed of light in a vacuum (2.99792458×10⁸ m/s) is pushed on the stack
    into the *x* register.

    ::

        ... → c, ...

``eps0``: permittivity of free space

    The permittivity of free space (8.854187817×10⁻¹² F/m [mks] or 1/4π [cgs])
    is pushed on the stack into the *x* register.

    ::

        ... → eps0, ...

``mu0``: permeability of free space

    The permeability of free space (4π×10⁻⁷ H/m [mks] or 4π/c² s²/m²
    [cgs]) is pushed on the stack into the *x* register.

    ::

        ... → mu0, ...

``Z0``: Characteristic impedance of free space

    The characteristic impedance of free space (376.730313461 Ω) is
    pushed on the stack into the *x* register.

    ::

        ... → Z0, ...

``hbar``: Reduced Planck constant

    The reduced Planck constant *ħ* (1.054571800×10⁻³⁴ J-s [mks] or
    1.054571800×10⁻²⁷ erg-s [cgs]) is pushed on the stack into the *x*
    register.

    ::

        ... → ħ, ...

    alias: ħ

``me``: rest mass of an electron

    The rest mass of an electron (9.10938356×10⁻²⁸ g) is pushed on the stack
    into the *x* register.

    ::

        ... → me, ...

``mp``: mass of a proton

    The mass of a proton (1.672621898×10⁻²⁴ g) is pushed on the stack into
    the *x* register.

    ::

        ... → mp, ...

``mn``: mass of a neutron

    The mass of a neutron (1.674927471×10⁻²⁴ g) is pushed on the stack into
    the *x* register.

    ::

        ... → mn, ...

``mh``: mass of a hydrogen atom

    The mass of a hydrogen atom (1.6735328115×10⁻²⁴ g) is pushed on the stack into
    the *x* register.

    ::

        ... → mh, ...

``amu``: unified atomic mass unit

    The unified atomic mass unit (1.660539040×10⁻²⁴ g) is pushed on the stack
    into the *x* register.

    ::

        ... → amu, ...

``G``: universal gravitational constant

    The universal gravitational constant (6.6746×10⁻¹⁴ m³/g-s²) is pushed
    on the stack into the *x* register.

    ::

        ... → G, ...

``g``: earth gravity

    The standard acceleration at sea level due to gravity on earth (9.80665
    m/s²)) is pushed on the stack into the *x* register.

    ::

        ... → g, ...

``Rinf``: Rydberg constant

    The Rydberg constant (10973731 m⁻¹) is pushed on the stack into the
    *x* register.

    ::

        ... → Ry, ...

``sigma``: Stefan-Boltzmann constant

    The Stefan-Boltzmann constant (5.670367×10⁻⁸ W/m²K⁴) is pushed on
    the stack into the *x* register.

    ::

        ... → sigma, ...

``alpha``: Fine structure constant

    The fine structure  constant (7.2973525664e-3) is pushed on
    the stack into the *x* register.

    ::

        ... → alpha, ...

``R``: molar gas constant

    The molar gas constant (8.3144598 J/mol-K [mks] or 83.145 Merg/deg-mol
    [cgs]) is pushed on the stack into the *x* register.

    ::

        ... → R, ...

``NA``: Avogadro Number

    Avogadro constant (6.022140857×10²³ mol⁻¹) is pushed on the stack into
    the *x* register.

    ::

        ... → NA, ...

``mks``: use MKS units for constants

    Switch the unit system for constants to MKS or SI.

``cgs``: use ESU CGS units for constants

    Switch the unit system for constants to ESU CGS.

Numbers
--------

``«N[.M][S][U]»``: a real number

    The number is pushed on the stack into the *x* register.  *N* is the
    integer portion of the mantissa and *M* is an optional fractional part.
    *S* is a letter that represents an SI scale factor. *U* the optional
    units (must not contain special characters).  For example, 10MHz
    represents 10⁷ Hz.

    ::

        ... → num, ...

``«N[.M]»e«E[U]»``: a real number in scientific notation

    The number is pushed on the stack into the *x* register.  *N* is the
    integer portion of the mantissa and *M* is an optional fractional part.
    *E* is an integer exponent. *U* the optional units (must not contain
    special characters).  For example, 2.2e-8F represents 22nF.

    ::

        ... → num, ...

``0x«N»``: a hexadecimal number

    The number is pushed on the stack into the *x* register.  *N* is an
    integer in base 16 (use a-f to represent digits greater than 9).  For
    example, 0xFF represents the hexadecimal number FF or the decimal number
    255.

    ::

        ... → num, ...

``0o«N»``: a number in octal

    The number is pushed on the stack into the *x* register.  *N* is an
    integer in base 8 (it must not contain the digits 8 or 9).  For example,
    0o77 represents the octal number 77 or the decimal number 63.

    ::

        ... → num, ...

``0b«N»``: a number in binary

    The number is pushed on the stack into the *x* register.  *N* is an
    integer in base 2 (it may contain only the digits 0 or 1).  For example,
    0b1111 represents the octal number 1111 or the decimal number 15.

    ::

        ... → num, ...

``'h«N»``: a number in Verilog hexadecimal notation

    The number is pushed on the stack into the *x* register.  *N* is an
    integer in base 16 (use a-f to represent digits greater than 9).  For
    example, 'hFF represents the hexadecimal number FF or the decimal number
    255.

    ::

        ... → num, ...

``'d«N»``: a number in Verilog decimal

    The number is pushed on the stack into the *x* register.  *N* is an
    integer in base 10.  For example, 'd99 represents the decimal number 99.

    ::

        ... → num, ...

``'o«N»``: a number in Verilog octal

    The number is pushed on the stack into the *x* register.  *N* is an
    integer in base 8 (it must not contain the digits 8 or 9).  For example,
    'o77 represents the octal number 77 or the decimal number 63.

    ::

        ... → num, ...

``'b«N»``: a number in Verilog binary

    The number is pushed on the stack into the *x* register.  *N* is an
    integer in base 2 (it may contain only the digits 0 or 1).  For example,
    'b1111 represents the binary number 1111 or the decimal number 15.

    ::

        ... → num, ...

Number Formats
---------------

``si[«N»]``: use SI notation

    Numbers are displayed with a fixed number of digits of precision and the
    SI scale factors are used to convey the exponent when possible.  If an
    optional whole number *N* immediately follows *si*, the precision is
    set to *N* digits.

``eng[«N»]``: use engineering notation

    Numbers are displayed with a fixed number of digits of precision and the
    exponent is given explicitly as an integer.  If an optional whole number
    *N* immediately follows *sci*, the precision is set to *N* digits.
    
    Engineering notation differs from scientific notation in that it allows 
    1, 2 or 3 digits to precede the decimal point in the mantissa and the
    exponent is always a multiple of 3.

``sci[«N»]``: use scientific notation

    Numbers are displayed with a fixed number of digits of precision and the
    exponent is given explicitly as an integer.  If an optional whole number
    *N* immediately follows *sci*, the precision is set to *N* digits. 
    
    Scientific notation differs from engineering notation in that it allows 
    only 1 digit to precede the decimal point in the mantissa and the
    exponent is not constrained to be a multiple of 3.

``fix[«N»]``: use fixed notation

    Numbers are displayed with a fixed number of digits to the right of the
    decimal point. If an optional whole number *N* immediately follows
    *fix*, the number of digits to the right of the decimal point is set to
    *N*.

``hex[«N»]``: use hexadecimal notation

    Numbers are displayed in base 16 (a-f are used to represent digits
    greater than 9) with a fixed number of digits.  If an optional whole
    number *N* immediately follows *hex*, the number of digits displayed
    is set to *N*.

``oct[«N»]``: use octal notation

    Numbers are displayed in base 8 with a fixed number of digits.  If an
    optional whole number *N* immediately follows *oct*, the number of
    digits displayed is set to *N*.

``bin[«N»]``: use binary notation

    Numbers are displayed in base 2 with a fixed number of digits.  If an
    optional whole number *N* immediately follows *bin*, the number of
    digits displayed is set to *N*.

``vhex[«N»]``: use Verilog hexadecimal notation

    Numbers are displayed in base 16 in Verilog format (a-f are used to
    represent digits greater than 9) with a fixed number of digits.  If an
    optional whole number *N* immediately follows *vhex*, the number of
    digits displayed is set to *N*.

``vdec[«N»]``: use Verilog decimal notation

    Numbers are displayed in base 10 in Verilog format with a fixed number
    of digits.  If an optional whole number *N* immediately follows
    *vdec*, the number of digits displayed is set to *N*.

``voct[«N»]``: use Verilog octal notation

    Numbers are displayed in base 8 in Verilog format with a fixed number of
    digits.  If an optional whole number *N* immediately follows *voct*,
    the number of digits displayed is set to *N*.

``vbin[«N»]``: use Verilog binary notation

    Numbers are displayed in base 2 in Verilog format with a fixed number of
    digits.  If an optional whole number *N* immediately follows *vbin*,
    the number of digits displayed is set to *N*.

Variable Commands
------------------

``=«name»``: store value into a variable

    Store the value in the *x* register into a variable with the given
    name.

    ::

        ... → ...

``«name»``: recall value of a variable

    Place the value of the variable with the given name into the *x*
    register.

    ::

        ... → value of «name», ...

``vars``: print variables

    List all defined variables and their values.

Stack Commands
---------------

``swap``: swap x and y

    The values in the *x* and *y* registers are swapped.

    ::

        x, y, ... → y, x, ...

``dup``: duplicate *x*

    The value in the *x* register is pushed onto the stack again.

    ::

        x, ... → x, x, ...

    alias: enter

``pop``: discard x

    The value in the *x* register is pulled from the stack and discarded.

    ::

        x, ... → ...

    alias: clrx

``lastx``: recall previous value of x

    The previous value of the *x* register is pushed onto the stack.

    ::

        ... → lastx, ...

``stack``: print stack

    Print all the values stored on the stack.

``clstack``: clear stack

    Remove all values from the stack.

    ::

        ... →

Miscellaneous Commands
-----------------------

``rand``: random number between 0 and 1

    A number between 0 and 1 is chosen at random and its value is pushed on
    the stack into *x* register.

    ::

        ... → rand, ...

```«text»```: print text

    Print "text" (the contents of the back-quotes) to the terminal.
    Generally used in scripts to report and annotate results.  Any instances
    of $N or ${N} are replaced by the value of register N, where 0
    represents the *x* register, 1 represents the *y* register, etc.  Any
    instances of $Var or ${Var} are replaced by the value of the variable
    *Var*.

``"«units»"``: set the units of the x register

    The units given are applied to the value in the *x* register.
    The actual value is unchanged.

    ::

        x, ... → x "units", ...

``>«units»``: convert value to given units

    The value in the *x* is popped from the stack, converted to the desired
    units, and pushed back on to the stack.

    ::

        x, ... → x converted to new desired units, ...

``(…)«name»``: a user-defined function or macro.

    A function is defined with the name «name» where … is a list of commands.
    When «name» is entered as a command, it is replaced by the list of
    commands.

``quit``: quit (:q or ^D also works)



    alias: :q

``help``: print a summary of the available features



``?[«topic»]``: detailed help on a particular topic

    A topic, in the form of a symbol or name, may follow the question mark,
    in which case a detailed description will be printed for that topic.
    If no topic is given, a list of available topics is listed.

``about``: print information about this calculator



