#!/usr/bin/env python
#
# Engineering Calculator Actions
#
# An RPN calculator that supports numbers with SI scale factors and units.

# Imports {{{1
from __future__ import division, print_function
import sys
import operator
import math
import cmath
import random
from calculator import (
    Command, Constant, UnaryOp, BinaryOp, BinaryIoOp, Number,
    SetFormat, Help, Store, Recall, SetUnits, Print, Dup, Category,
    Calculator
)
from engfmt import from_eng_fmt, to_eng_fmt, set_preferences
from inform import warn
set_preferences(spacer=' ')


# Actions {{{1
# Create actions here, they will be registered into availableActions
# automatically. That will be used to build the list of actions to make
# available to the user based on calculator personality later.

# Arithmetic Operators {{{2
arithmeticOperators = Category("Arithmetic Operators")

# addition {{{3
addition = BinaryOp(
    '+'
  , operator.add
  , description="%(key)s: addition"
  # keep units of x if they are the same as units of y
  , units=lambda calc, units: units[0] if units[0] == units[1] else ''
  , synopsis='#{x}, #{y}, ... => #{x}+#{y}, ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the
        stack and the sum is placed back on the stack into the #{x}
        register.
    """
)
addition.addTest(
    stimulus='1 1 +'
  , result=1 + 1
  , units=''
  , text='2'
)
addition.addTest(
    stimulus='100mV 25mV+'
  , result=100e-3 + 25e-3
  , units='V'
  , text='125 mV'
)
addition.addTest(
    stimulus='$100M $25M+'
  , result=100e6 + 25e6
  , units='$'
  , text='$125M'
)
addition.addTest(
    stimulus='200mV 100m+'
  , result=0.2 + 0.1
  , units=''
  , text='300m'
)
addition.addTest(
    stimulus='1 j +'
  , result=1 + 1j
  , units=''
  , text='1 + j'
)

# subtraction {{{3
subtraction = BinaryOp(
    '-'
  , operator.sub
  , description="%(key)s: subtraction"
  # keep units of x if they are the same as units of y
  , units=lambda calc, units: units[0] if units[0] == units[1] else ''
  , synopsis='#{x}, #{y}, ... => #{x}-#{y}, ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the
        stack and the difference is placed back on the stack into the #{x}
        register.
    """
)
subtraction.addTest(
    stimulus='1 1 -'
  , result=0
  , units=''
  , text='0'
)
subtraction.addTest(
    stimulus='100mV 25mV-'
  , result=100e-3 - 25e-3
  , units='V'
  , text='75 mV'
)
subtraction.addTest(
    stimulus='$100M $25M-'
  , result=100e6 - 25e6
  , units='$'
  , text='$75M'
)
subtraction.addTest(
    stimulus='200mV 100m-'
  , result=0.2 - 0.1
  , units=''
  , text='100m'
)
subtraction.addTest(
    stimulus='1 j -'
  , result=1 - 1j
  , units=''
  , text='1 - j'
)

# multiplication {{{3
multiplication = BinaryOp(
    '*'
  , operator.mul
  , description="%(key)s: multiplication"
  , synopsis='#{x}, #{y}, ... => #{x}*#{y}, ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the
        stack and the product is placed back on the stack into the #{x}
        register.
    """
)
multiplication.addTest(
    stimulus='2 2 *'
  , result=2 * 2
  , units=''
  , text='4'
)
multiplication.addTest(
    stimulus='25MHz 2pi * "rads/s"'
  , result=2 * math.pi * 25e6
  , units='rads/s'
  , text='157.08 Mrads/s'
)
multiplication.addTest(
    stimulus='1 j *'
  , result=1j
  , units=''
  , text='j'
)
multiplication.addTest(
    stimulus='j j *'
  , result=-1
  , units=''
  , text='-1'
)

# true division {{{3
trueDivision = BinaryOp(
    '/'
  , operator.truediv
  , description="%(key)s: true division"
  , synopsis='#{x}, #{y}, ... => #{y}/#{x}, ...'
  , summary=r"""
        The values in the #{x} and #{y} registers are popped from the stack and
        the quotient is placed back on the stack into the #{x} register.  Both
        values are treated as real numbers and the result is a real number. So
        \verb{
            @{0}: 1 2/
            @{500m}:
        }
    """
)
trueDivision.addTest(
    stimulus='1 2/'
  , result=1/2
  , units=''
  , text='500m'
)
trueDivision.addTest(
    stimulus='1 j /'
  , result=-1j
  , units=''
  , text='-j'
)

# floor division {{{3
floorDivision = BinaryOp(
    '//'
  , operator.floordiv
  , description="%(key)s: floor division"
  , synopsis='#{x}, #{y}, ... => #{y}//#{x}, ...'
  , summary=r"""
        The values in the #{x} and #{y} registers are popped from the
        stack, the quotient is computed and then converted to an integer using
        the floor operation (it is replaced by the largest integer that is
        smaller than the quotient), and that is placed back on the stack into
        the #{x} register.  So
        \verb{
            @{0}: 1 2//
            @{0}:
        }
    """
)
floorDivision.addTest(
    stimulus='5 2//'
  , result=5//2
  , units=''
  , text='2'
)

# modulus {{{3
modulus = BinaryOp(
    '%'
  , operator.mod
  , description="%(key)s: modulus"
  , synopsis='#{x}, #{y}, ... => #{y}%#{x}, ...'
  , summary=r"""
        The values in the #{x} and #{y} registers are popped from the stack, the
        quotient is computed and the remainder is placed back on the stack into
        the #{x} register.  So
        \verb{
            @{0}: 14 3%
            @{2}:
        }
        In this case 2 is the remainder because 3 goes evenly into 14 three
        times, which leaves a remainder of 2.
    """
)
modulus.addTest(
    stimulus='5 2%'
  , result=5%2
  , units=''
  , text='1'
)

# percent change {{{3
percentChange = BinaryOp(
    '%chg'
  , lambda y, x: 100*(x-y)/y
  , description="%(key)s: percent change"
  , synopsis='#{x}, #{y}, ... => 100*(#{x}-#{y})/#{y}, ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and 
        the percent difference between #{x} and #{y} relative to #{y} is pushed 
        back into the #{x} register.
    """
)
percentChange.addTest(
    stimulus='10 10.5 %chg'
  , result=100*(10.5 - 10)/10
  , units=''
  , text='5'
)

# parallel combination {{{3
parallel = BinaryOp(
    '||'
  , lambda y, x: (x/(x+y))*y
  # keep units of x if they are the same as units of y
  , units=lambda calc, units: units[0] if units[0] == units[1] else ''
  , description="%(key)s: parallel combination"
  , synopsis='#{x}, #{y}, ... => 1/(1/#{x}+1/#{y}), ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and
        replaced with the reciprocal of the sum of their reciprocals.  If the
        values in the #{x} and #{y} registers are both resistances, both
        elastances, or both inductances, then the result is the resistance,
        elastance or inductance of the two in parallel. If the values are
        conductances, capacitances or susceptances, then the result is the
        conductance, capacitance or susceptance of the two in series.
    """
)
parallel.addTest(
    stimulus='100 100 ||'
  , result=(100/(100+100))*100
  , units=''
  , text='50'
)
parallel.addTest(
    stimulus='10kOhm 10kOhm ||'
  , result=(1e4/(1e4+1e4))*1e4
  , units='Ohm'
  , text='5 kOhm'
)
parallel.addTest(
    stimulus='50_Ohm 50 ||'
  , result=(50/(50+50))*50
  , units=''
  , text='25'
)

# negation {{{3
negation = UnaryOp(
    'chs'
  , operator.neg
  , units=lambda calc, units: units[0]
  , description="%(key)s: change sign"
  , synopsis='#{x}, ... => -#{x}, ...'
  , summary="""
        The value in the #{x} register is replaced with its negative. 
    """
)
negation.addTest(
    stimulus='-3 chs'
  , result=3
  , units=''
  , text='3'
)
negation.addTest(
    stimulus='330pF chs'
  , result=-330e-12
  , units='F'
  , text='-330 pF'
)

# reciprocal {{{3
reciprocal = UnaryOp(
    'recip'
  , lambda x: 1/x
  , description="%(key)s: reciprocal"
  , synopsis='#{x}, ... => 1/#{x}, ...'
  , summary="""
        The value in the #{x} register is replaced with its reciprocal. 
    """
)
reciprocal.addTest(
    stimulus='4 recip'
  , result=1/4
  , units=''
  , text='250m'
)
reciprocal.addTest(
    stimulus='1kOhm recip'
  , result=1/1000
  , units=''
  , text='1m'
)
reciprocal.addTest(
    stimulus='0 recip'
  , error='division by zero.'
)
reciprocal.addTest(
    stimulus='j recip'
  , result=-1j
  , units=''
  , text='-j'
)

# ceiling {{{3
ceiling = UnaryOp(
    'ceil'
  , math.ceil
  , units=lambda calc, units: units[0]
  , description="%(key)s: round towards positive infinity"
  , synopsis='#{x}, ... => ceil(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its value rounded
        towards infinity (replaced with the smallest integer greater than its
        value).
    """
)
ceiling.addTest(
    stimulus='1.5 ceil'
  , result=math.ceil(1.5)
  , units=''
  , text='2'
)
ceiling.addTest(
    stimulus='-1.5 ceil'
  , result=math.ceil(-1.5)
  , units=''
  , text='-1'
)
ceiling.addTest(
    stimulus='7.5_Hz ceil'
  , result=math.ceil(7.5)
  , units='Hz'
  , text='8 Hz'
)
ceiling.addTest(
    stimulus='j ceil'
  , error='Function does not support a complex argument.'
)

# floor {{{3
floor = UnaryOp(
    'floor'
  , math.floor
  , units=lambda calc, units: units[0]
  , description="%(key)s: round towards negative infinity"
  , synopsis='#{x}, ... => floor(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its value rounded
        towards negative infinity (replaced with the largest integer smaller
        than its value).
    """
)
floor.addTest(
    stimulus='1.5 floor'
  , result=math.floor(1.5)
  , units=''
  , text='1'
)
floor.addTest(
    stimulus='-1.5 floor'
  , result=math.floor(-1.5)
  , units=''
  , text='-2'
)
floor.addTest(
    stimulus='7.5_Hz floor'
  , result=math.floor(7.5)
  , units='Hz'
  , text='7 Hz'
)
floor.addTest(
    stimulus='j floor'
  , error='Function does not support a complex argument.'
)


# factorial {{{3
try:
    factorial = UnaryOp(
        '!'
      , math.factorial
      , description="%(key)s: factorial"
      , synopsis='#{x}, ... => #{x}!, ...'
      , summary="""
            The value in the #{x} register is replaced with its factorial.
        """
    )
    factorial.addTest(
        stimulus='6!'
      , result=math.factorial(6)
      , units=''
      , text='720'
    )
except AttributeError:
    factorial = None

# random number {{{3
randomNumber = Constant(
    'rand'
  , random.random
  , description="%(key)s: random number between 0 and 1"
  , synopsis='... => #{rand}, ...'
  , summary="""
        A number between 0 and 1 is chosen at random and its value is pushed on
        the stack into #{x} register.
    """
)
randomNumber.addTest('rand', units='')


# Logs, Powers, and Exponentials {{{2
powersAndLogs = Category("Powers, Roots, Exponentials and Logarithms")

# power {{{3
power = BinaryOp(
    '**'
  , operator.pow
  , description="%(key)s: raise y to the power of x"
  , synopsis='#{x}, #{y}, ... => #{y}**#{x}, ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the
        stack and replaced with the value of #{y} raised to the power of
        #{x}. 
    """
  , aliases=['pow', 'ytox']
)
power.addTest(
    stimulus='500 2**'
  , result=500**2
  , units=''
  , text='250k'
)
power.addTest(
    stimulus='8 1 3/ pow'
  , result=2
  , units=''
  , text='2'
)
if int(sys.version[0]) < 3:
    power.addTest(
        stimulus='-8 1 3/ ytox'
      , error='negative number cannot be raised to a fractional power'
    )
else:
    power.addTest(
        stimulus='-8 1 3/ ytox'
      , result=1+1j*cmath.sqrt(3)
      , units=''
      , text='1 + j1.7321'
    )

# exponential {{{3
exponential = UnaryOp(
    'exp'
  , lambda x: cmath.exp(x) if type(x) == complex else math.exp(x)
  , description="%(key)s: natural exponential"
  , synopsis='#{x}, ... => exp(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its exponential. 
        Supports a complex argument.
    """
  , aliases=['powe']
)
exponential.addTest(
    stimulus='10 exp ln'
  , result=10
  , units=''
  , text='10'
)
exponential.addTest(
    stimulus='-10 powe ln'
  , result=-10
  , units=''
  , text='-10'
)
exponential.addTest(
    stimulus='j pi * exp'
  , result=-1
  , units=''
)

# natural logarithm {{{3
naturalLog = UnaryOp(
    'ln'
  , lambda x: cmath.log(x) if (type(x) == complex or x < 0) else math.log(x)
  , description="%(key)s: natural logarithm"
  , synopsis='#{x}, ... => ln(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its natural logarithm. 
        Supports a complex argument.
    """
  , aliases=['loge']
)
naturalLog.addTest(
    stimulus='100 ln exp'
  , result=100
  , units=''
  , text='100'
)
naturalLog.addTest(
    stimulus='-100 loge'
  , result=(4.60517018599+3.14159265359j)
  , units=''
  , text='4.6052 + j3.1416'
)
naturalLog.addTest(
    stimulus='j ln'
  , result=1.57079632679j
  , units=''
  , text='j1.5708'
)

# raise 10 to the power of x {{{3
tenPower = UnaryOp(
    'pow10'
  , lambda x: 10**x
  , description="%(key)s: raise 10 to the power of x"
  , synopsis='#{x}, ... => 10**#{x}, ...'
  , summary="""
        The value in the #{x} register is replaced with 10 raised to #{x}.
    """
  , aliases=['10tox']
)
tenPower.addTest(
    stimulus='10 pow10 log'
  , result=10
  , units=''
  , text='10'
)
tenPower.addTest(
    stimulus='-10 10tox log'
  , result=-10
  , units=''
  , text='-10'
)

# common logarithm {{{3
commonLog = UnaryOp(
    'log'
  , math.log10
  , description="%(key)s: base 10 logarithm"
  , synopsis='#{x}, ... => log(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its common logarithm. 
    """
  , aliases=['log10', 'lg']
)
commonLog.addTest(
    stimulus='100 log pow10'
  , result=100
  , units=''
  , text='100'
)

# raise 2 to the power of x {{{3
twoPower = UnaryOp(
    'pow2'
  , lambda x: 2**x
  , description="%(key)s: raise 2 to the power of x"
  , synopsis='#{x}, ... => 2**#{x}, ...'
  , summary="""
        The value in the #{x} register is replaced with 2 raised to #{x}.
    """
  , aliases=['2tox']
)
twoPower.addTest(
    stimulus='16 pow2'
  , result=65536
  , units=''
  , text='65.536k'
)
twoPower.addTest(
    stimulus='-2 2tox'
  , result=0.25
  , units=''
  , text='250m'
)

# binary logarithm {{{3
binaryLog = UnaryOp(
    'log2'
  , lambda x: math.log(x)/math.log(2)
  , description="%(key)s: base 2 logarithm"
  , synopsis='#{x}, ... => log2(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its base 2 logarithm. 
    """
  , aliases=['lb']
)
binaryLog.addTest(
    stimulus='65536 log2'
  , result=16
  , units=''
  , text='16'
)
binaryLog.addTest(
    stimulus='0.25 lb'
  , result=-2
  , units=''
  , text='-2'
)

# square {{{3
square = UnaryOp(
    'sqr'
  , lambda x: x*x
  , description="%(key)s: square"
  , synopsis='#{x}, ... => #{x}**2, ...'
  , summary="""
        The value in the #{x} register is replaced with its square. 
    """
)
square.addTest(
    stimulus='4 sqr'
  , result=4*4
  , units=''
  , text='16'
)
square.addTest(
    stimulus='j sqr'
  , result=-1
  , units=''
  , text='-1'
)

# square root {{{3
squareRoot = UnaryOp(
    'sqrt'
  , lambda x: cmath.sqrt(x) if (type(x) == complex or x < 0) else math.sqrt(x)
  , description="%(key)s: square root"
  , synopsis='#{x}, ... => sqrt(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its square root.
    """
  , aliases=["rt"]
)
squareRoot.addTest(
    stimulus='16 sqrt'
  , result=4
  , units=''
  , text='4'
)
squareRoot.addTest(
    stimulus='-4 sqrt'
  , result=2j
  , units=''
  , text='j2'
)
squareRoot.addTest(
    stimulus='4 j * sqrt'
  , result=math.sqrt(2) + 1j*math.sqrt(2)
  , units=''
  , text='1.4142 + j1.4142'
)

# cube root {{{3
try:
    from ctypes import util, cdll, c_double
    libm = cdll.LoadLibrary(util.find_library('m'))
    libm.cbrt.restype = c_double
    libm.cbrt.argtypes = [c_double]
    cubeRoot = UnaryOp(
        'cbrt'
      , lambda x: libm.cbrt(x)
      , description="%(key)s: cube root"
      , synopsis='#{x}, ... => cbrt(#{x}), ...'
      , summary="""
            The value in the #{x} register is replaced with its cube root.
        """
    )
    cubeRoot.addTest(
        stimulus='64 cbrt'
      , result=4
      , units=''
      , text='4'
    )
    cubeRoot.addTest(
        stimulus='-8 cbrt'
      , result=-2
      , units=''
      , text='-2'
    )
except ImportError:
    cubeRoot = None

# Trig Functions {{{2
trigFunctions = Category("Trigonometric Functions")

# sine {{{3
sine = UnaryOp(
    'sin'
  , lambda x, calc: math.sin(calc.toRadians(x))
  , description="%(key)s: trigonometric sine"
  , needCalc=True
  , synopsis='#{x}, ... => sin(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its sine.
    """
)
sine.addTest(
    stimulus='90 sin'
  , result=1
  , units=''
  , text='1'
)
sine.addTest(
    stimulus='degs 270 sin'
  , result=-1
  , units=''
  , text='-1'
)
sine.addTest(
    stimulus='rads pi 2/ sin'
  , result=1
  , units=''
  , text='1'
)

# cosine {{{3
cosine = UnaryOp(
    'cos'
  , lambda x, calc: math.cos(calc.toRadians(x))
  , description="%(key)s: trigonometric cosine"
  , needCalc=True
  , synopsis='#{x}, ... => cos(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its cosine.
    """
)
cosine.addTest(
    stimulus='180 cos'
  , result=-1
  , units=''
  , text='-1'
)
cosine.addTest(
    stimulus='rads pi cos'
  , result=-1
  , units=''
  , text='-1'
)
cosine.addTest(
    stimulus='degs 360 cos'
  , result=1
  , units=''
  , text='1'
)

# tangent {{{3
tangent = UnaryOp(
    'tan'
  , lambda x, calc: math.tan(calc.toRadians(x))
  , description="%(key)s: trigonometric tangent"
  , needCalc=True
  , synopsis='#{x}, ... => tan(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its tangent.
    """
)
tangent.addTest(
    stimulus='45 tan'
  , result=1
  , units=''
  , text='1'
)
tangent.addTest(
    stimulus='rads pi 4/ tan'
  , result=1
  , units=''
  , text='1'
)
tangent.addTest(
    stimulus='degs -45 tan'
  , result=-1
  , units=''
  , text='-1'
)

# arc sine {{{3
arcSine = UnaryOp(
    'asin'
  , lambda x, calc: calc.fromRadians(math.asin(x))
  , description="%(key)s: trigonometric arc sine"
  , needCalc=True
  , units=lambda calc, units: calc.angleUnits()
  , synopsis='#{x}, ... => asin(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its arc sine.
    """
)
arcSine.addTest(
    stimulus='1 asin'
  , result=90
  , units='degs'
  , text='90 degs'
)
arcSine.addTest(
    stimulus='rads 1 sin asin'
  , result=1
  , units='rads'
  , text='1 rads'
)
arcSine.addTest(
    stimulus='degs -1 asin'
  , result=-90
  , units='degs'
  , text='-90 degs'
)
arcSine.addTest(
    stimulus='degs 2 asin'
  , error='math domain error'
)

# arc cosine {{{3
arcCosine = UnaryOp(
    'acos'
  , lambda x, calc: calc.fromRadians(math.acos(x))
  , description="%(key)s: trigonometric arc cosine"
  , needCalc=True
  , units=lambda calc, units: calc.angleUnits()
  , synopsis='#{x}, ... => acos(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its arc cosine.
    """
)
arcCosine.addTest(
    stimulus='0 acos'
  , result=90
  , units='degs'
  , text='90 degs'
)
arcCosine.addTest(
    stimulus='rads 1 acos'
  , result=0
  , units='rads'
  , text='0 rads'
)
arcCosine.addTest(
    stimulus='degs 45 cos acos'
  , result=45
  , units='degs'
  , text='45 degs'
)
arcCosine.addTest(
    stimulus='degs 2 acos'
  , error='math domain error'
)

# arc tangent {{{3
arcTangent = UnaryOp(
    'atan'
  , lambda x, calc: calc.fromRadians(math.atan(x))
  , description="%(key)s: trigonometric arc tangent"
  , needCalc=True
  , units=lambda calc, units: calc.angleUnits()
  , synopsis='#{x}, ... => atan(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its arc tangent.
    """
)
arcTangent.addTest(
    stimulus='0 atan'
  , result=0
  , units='degs'
  , text='0 degs'
)
arcTangent.addTest(
    stimulus='rads 0 atan'
  , result=0
  , units='rads'
  , text='0 rads'
)
arcTangent.addTest(
    stimulus='degs 45 tan atan'
  , result=45
  , units='degs'
  , text='45 degs'
)

# radians {{{3
setRadiansMode = Command(
    'rads'
  , Calculator.useRadians
  , description="%(key)s: use radians"
  , summary="""
        Switch the trigonometric mode to radians (functions such as #{sin},
        #{cos}, #{tan}, and #{ptor} expect angles to be given in radians;
        functions such as #{arg}, #{asin}, #{acos}, #{atan}, #{atan2}, and
        #{rtop} should produce angles in radians).
    """
)

# degrees {{{3
setDegreesMode = Command(
    'degs'
  , Calculator.useDegrees
  , description="%(key)s: use degrees"
  , summary="""
        Switch the trigonometric mode to degrees (functions such as #{sin},
        #{cos}, #{tan}, and #{ptor} expect angles to be given in degrees;
        functions such as #{arg}, #{asin}, #{acos}, #{atan}, #{atan2}, and
        #{rtop} should produce angles in degrees).
    """
)

# Complex and Vector Functions {{{2
complexAndVectorFunctions = Category("Complex and Vector Functions")

# absolute value {{{3
# Absolute Value of a complex number.
# Also known as the magnitude, amplitude, or modulus
absoluteValue = Dup(
    'abs'
  , lambda x: abs(x)
  , description="%(key)s: magnitude"
  , units=lambda calc, units: units[0]
  , synopsis='#{x}, ... => abs(#{x}), #{x}, ...'
  , summary="""
        The absolute value of the number in the #{x} register is pushed onto the
        stack if it is real. If the value is complex, the magnitude is pushed
        onto the stack.

        Unlike most other functions, this one does not replace the value of its
        argument on the stack. Its value is simply pushed onto the stack without
        first popping off the argument.
    """
  , aliases=['mag']
)
absoluteValue.addTest(
    stimulus='-1 abs'
  , result=1
  , units=''
  , text='1'
)
absoluteValue.addTest(
    stimulus='-1MHz abs'
  , result=1e6
  , units='Hz'
  , text='1 MHz'
)
absoluteValue.addTest(
    stimulus='j chs mag'
  , result=1
  , units=''
  , text='1'
)
absoluteValue.addTest(
    stimulus='1 j + "V" mag pop'
  , result=1+1j
  , units='V'
  , text='1 V + j V'
)

# argument {{{3
# Argument of a complex number, also known as the phase , or angle
argument = Dup(
    'arg'
  , lambda x, calc: (
        calc.fromRadians(math.atan2(x.imag,x.real))
        if type(x) == complex
        else 0
    )
  , description="%(key)s: phase"
  , needCalc=True
  , units=lambda calc, units: calc.angleUnits()
  , synopsis='#{x}, ... => arg(#{x}), #{x}, ...'
  , summary="""
        The argument of the number in the #{x} register is pushed onto the
        stack if it is complex. If the value is real, zero is pushed
        onto the stack.

        Unlike most other functions, this one does not replace the value of its
        argument on the stack. Its value is simply pushed onto the stack without
        first popping off the argument.
    """
  , aliases=['ph']
)
argument.addTest(
    stimulus='1 j + arg'
  , result=45
  , units='degs'
  , text='45 degs'
)
argument.addTest(
    stimulus='rads 1 j - ph'
  , result=-math.pi/4
  , units='rads'
  , text='-785.4 mrads'
)
argument.addTest(
    stimulus='1 j + "V" ph pop'
  , result=1+1j
  , units='V'
  , text='1 V + j V'
)
argument.addTest(
    stimulus='1 j + "m/s" arg pop'
  , result=1+1j
  , units='m/s'
  , text='1 m/s + j m/s'
)

# hypotenuse {{{3
hypotenuse = BinaryOp(
    'hypot'
  , math.hypot
  # keep units of x if they are the same as units of y
  , units=lambda calc, units: units[0] if units[0] == units[1] else ''
  , description="%(key)s: hypotenuse"
  , synopsis='#{x}, #{y}, ... => sqrt(#{x}**2+#{y}**2), ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and 
        replaced with the length of the vector from the origin to the point
        (#{x}, #{y}).
    """
  , aliases=['len']
)
hypotenuse.addTest(
    stimulus='3 4 hypot'
  , result=5
  , units=''
  , text='5'
)
hypotenuse.addTest(
    stimulus='3mm 4mm len'
  , result=5e-3
  , units='m'
  , text='5 mm'
)

# arc tangent 2 {{{3
arcTangent2 = BinaryOp(
    'atan2'
  , lambda y, x, calc: calc.fromRadians(math.atan2(y, x))
  , description="%(key)s: two-argument arc tangent"
  , needCalc=True
  , units=lambda calc, units: calc.angleUnits()
  , synopsis='#{x}, #{y}, ... => atan2(#{y},#{x}), ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and 
        replaced with the angle of the vector from the origin to the point.
    """
  , aliases=['angle']
)
arcTangent2.addTest(
    stimulus='3 3 atan2'
  , result=45
  , units='degs'
  , text='45 degs'
)
arcTangent2.addTest(
    stimulus='rads -3 3 angle'
  , result=-math.pi/4
  , units='rads'
  , text='-785.4 mrads'
)
arcTangent2.addTest(
    stimulus='-3 -3 atan2'
  , result=-135
  , units='degs'
  , text='-135 degs'
)
arcTangent2.addTest(
    stimulus='3 -3 angle'
  , result=135
  , units='degs'
  , text='135 degs'
)
arcTangent2.addTest(
    stimulus='rads 0 0 atan2'
  , result=0
  , units='rads'
  , text='0 rads'
)

# rectangular to polar {{{3
rectangularToPolar = BinaryIoOp(
    'rtop'
  , lambda y, x, calc: (math.hypot(y, x), calc.fromRadians(math.atan2(y,x)))
  # keep units of x if they are the same as units of y
  , xUnits=lambda calc, units: units[0] if units[0] == units[1] else ''
  , yUnits=lambda calc, units: calc.angleUnits()
  , description="%(key)s: convert rectangular to polar coordinates"
  , needCalc=True
  , synopsis='#{x}, #{y}, ... => sqrt(#{x}**2+#{y}**2), atan2(#{y},#{x}), ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and 
        replaced with the length of the vector from the origin to the point 
        (#{x}, #{y}) and with the angle of the vector from the origin to the 
        point (#{x}, #{y}).
    """
)
rectangularToPolar.addTest(
    stimulus='3 4 rtop'
  , result=5
  , units=''
  , text='5'
)
rectangularToPolar.addTest(
    stimulus='3kOhm -4kOhm rtop'
  , result=5e3
  , units='Ohm'
  , text='5 kOhm'
)
rectangularToPolar.addTest(
    stimulus='4MOhm 4MOhm rtop swap'
  , result=45
  , units='degs'
  , text='45 degs'
)
rectangularToPolar.addTest(
    stimulus='rads 4MOhm 4MOhm rtop swap'
  , result=math.pi/4
  , units='rads'
  , text='785.4 mrads'
)

# polar to rectangular {{{3
polarToRectangular = BinaryIoOp(
    'ptor'
  , lambda ph, mag, calc: (
        mag*math.cos(calc.toRadians(ph))
      , mag*math.sin(calc.toRadians(ph))
    )
  , description="%(key)s: convert polar to rectangular coordinates"
  , needCalc=True
  , xUnits=lambda calc, units: units[0]
  , yUnits=lambda calc, units: units[0]
  , synopsis='#{x}, #{y}, ... => #{x}*cos(#{y}), #{x}*sin(#{y}), ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and
        interpreted as the length and angle of a vector and are replaced with
        the coordinates of the end-point of that vector.
    """
)
polarToRectangular.addTest(
    stimulus='45 2 sqrt "V" ptor'
  , result=1
  , units='V'
  , text='1 V'
)
polarToRectangular.addTest(
    stimulus='45 2 sqrt "V" ptor swap'
  , result=1
  , units='V'
  , text='1 V'
)
polarToRectangular.addTest(
    stimulus='rads pi 4/ 2 sqrt "V" ptor'
  , result=1
  , units='V'
  , text='1 V'
)
polarToRectangular.addTest(
    stimulus='rads pi 4/ 2 sqrt "V" ptor swap'
  , result=1
  , units='V'
  , text='1 V'
)

# Hyperbolic Functions {{{2
hyperbolicFunctions = Category("Hyperbolic Functions")

# hyperbolic sine {{{3
hyperbolicSine = UnaryOp(
    'sinh'
  , math.sinh
  , description="%(key)s: hyperbolic sine"
  , synopsis='#{x}, ... => sinh(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic sine.
    """
)
hyperbolicSine.addTest(
    stimulus='1 sinh'
  , result=math.sinh(1)
  , units=''
  , text='1.1752'
)

# hyperbolic cosine {{{3
hyperbolicCosine = UnaryOp(
    'cosh'
  , math.cosh
  , description="%(key)s: hyperbolic cosine"
  , synopsis='#{x}, ... => cosh(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic cosine.
    """
)
hyperbolicCosine.addTest(
    stimulus='1 cosh'
  , result=math.cosh(1)
  , units=''
  , text='1.5431'
)

# hyperbolic tangent {{{3
hyperbolicTangent = UnaryOp(
    'tanh'
  , math.tanh
  , description="%(key)s: hyperbolic tangent"
  , synopsis='#{x}, ... => tanh(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic tangent.
    """
)
hyperbolicTangent.addTest(
    stimulus='1 tanh'
  , result=math.tanh(1)
  , units=''
  , text='761.59m'
)

# hyperbolic arc sine {{{3
try:
    hyperbolicArcSine = UnaryOp(
        'asinh'
      , math.asinh
      , description="%(key)s: hyperbolic arc sine"
      , synopsis='#{x}, ... => asinh(#{x}), ...'
      , summary="""
            The value in the #{x} register is replaced with its hyperbolic arc sine.
        """
    )
    hyperbolicArcSine.addTest(
        stimulus='1 sinh asinh'
      , result=1
      , units=''
      , text='1'
    )
except AttributeError:
    hyperbolicArcSine = None

# hyperbolic arc cosine {{{3
try:
    hyperbolicArcCosine = UnaryOp(
        'acosh'
      , math.acosh
      , description="%(key)s: hyperbolic arc cosine"
      , synopsis='#{x}, ... => acosh(#{x}), ...'
      , summary="""
            The value in the #{x} register is replaced with its hyperbolic arc
            cosine.
        """
    )
    hyperbolicArcCosine.addTest(
        stimulus='1 cosh acosh'
      , result=1
      , units=''
      , text='1'
    )
except AttributeError:
    hyperbolicArcCosine = None

# hyperbolic arc tangent {{{3
try:
    hyperbolicArcTangent = UnaryOp(
        'atanh'
      , math.atanh
      , description="%(key)s: hyperbolic arc tangent"
      , synopsis='#{x}, ... => atanh(#{x}), ...'
      , summary="""
            The value in the #{x} register is replaced with its hyperbolic arc
            tangent.
        """
    )
    hyperbolicArcTangent.addTest(
        stimulus='1 tanh atanh'
      , result=1
      , units=''
      , text='1'
    )
except AttributeError:
    hyperbolicArcTangent = None

# Decibel Functions {{{2
decibelFunctions = Category("Decibel Functions")

# voltage or current to decibels {{{3
decibels20 = UnaryOp(
    'db'
  , lambda x: 20*math.log10(x)
  , description="%(key)s: convert voltage or current to dB"
  , synopsis='#{x}, ... => 20*log(#{x}), ...'
  , summary="""
        The value in the #{x} register is replaced with its value in 
        decibels. It is appropriate to apply this form when 
        converting voltage or current to decibels.
    """
  , aliases=['db20', 'v2db', 'i2db']
)
decibels20.addTest(
    stimulus='100 db'
  , result=40
  , units=''
  , text='40'
)
decibels20.addTest(
    stimulus='10m db20'
  , result=-40
  , units=''
  , text='-40'
)
decibels20.addTest(
    stimulus='1000 v2db'
  , result=60
  , units=''
  , text='60'
)
decibels20.addTest(
    stimulus='1m i2db'
  , result=-60
  , units=''
  , text='-60'
)

# decibels to voltage or current {{{3
antiDecibels20 = UnaryOp(
    'adb'
  , lambda x: 10**(x/20)
  , description="%(key)s: convert dB to voltage or current"
  , synopsis='#{x}, ... => 10**(#{x}/20), ...'
  , summary="""
        The value in the #{x} register is converted from decibels and that value
        is placed back into the #{x} register.  It is appropriate to apply this
        form when converting decibels to voltage or current.  
    """
  , aliases=['db2v', 'db2i']
)
antiDecibels20.addTest(
    stimulus='40 adb'
  , result=100
  , units=''
  , text='100'
)
antiDecibels20.addTest(
    stimulus='40 db2v'
  , result=100
  , units=''
  , text='100'
)
antiDecibels20.addTest(
    stimulus='40 db2i'
  , result=100
  , units=''
  , text='100'
)

# power to decibels {{{3
decibels10 = UnaryOp(
    'db10'
  , lambda x: 10*math.log10(x)
  , description="%(key)s: convert power to dB"
  , synopsis='#{x}, ... => 10*log(#{x}), ...'
  , summary="""
        The value in the #{x} register is converted from decibels and that
        value is placed back into the #{x} register.  It is appropriate to
        apply this form when converting power to decibels.
    """
  , aliases=['p2db']
)
decibels10.addTest(
    stimulus='100 db10'
  , result=20
  , units=''
  , text='20'
)
decibels10.addTest(
    stimulus='100 p2db'
  , result=20
  , units=''
  , text='20'
)

# decibels to power {{{3
antiDecibels10 = UnaryOp(
    'adb10'
  , lambda x: 10**(x/10)
  , description="%(key)s: convert dB to power"
  , synopsis='#{x}, ... => 10**(#{x}/10), ...'
  , summary="""
        The value in the #{x} register is converted from decibels and that value
        is placed back into the #{x} register.  It is appropriate to apply this
        form when converting decibels to voltage or current.  
    """
  , aliases=['db2p']
)
antiDecibels10.addTest(
    stimulus='20 adb10'
  , result=100
  , units=''
  , text='100'
)
antiDecibels10.addTest(
    stimulus='20 db2p'
  , result=100
  , units=''
  , text='100'
)

# voltage to dBm {{{3
voltageToDbm = UnaryOp(
    'vdbm'
  , lambda x, calc: 30+10*math.log10(x*x/calc.heap['Rref'][0]/2)
  , description="%(key)s: convert peak voltage to dBm"
  , needCalc=True
  , synopsis='#{x}, ... => 30+10*log10((#{x}**2)/(2*#{Rref})), ...'
  , summary="""
        The value in the #{x} register is expected to be the peak voltage of a
        sinusoid that is driving a load resistor equal to #{Rref} (a predefined
        variable).  It is replaced with the power delivered to the resistor in
        decibels relative to 1 milliwatt.  
    """
  , aliases=['v2dbm']
)
voltageToDbm.addTest(
    stimulus='1 vdbm'
  , result=10
  , units=''
  , text='10'
)
voltageToDbm.addTest(
    stimulus='0.1 v2dbm'
  , result=-10
  , units=''
  , text='-10'
)
voltageToDbm.addTest(
    stimulus='5 "Ohms" =Rref 1 vdbm'
  , result=20
  , units=''
  , text='20'
)

# dBm to voltage {{{3
dbmToVoltage = UnaryOp(
    'dbmv'
  , lambda x, calc: math.sqrt(2*pow(10,(x - 30)/10)*calc.heap['Rref'][0])
  , description="%(key)s: dBm to peak voltage"
  , needCalc=True
  , units='V'
  , synopsis='#{x}, ... => sqrt(2*10**(#{x} - 30)/10)*#{Rref}), ...'
  , summary="""
        The value in the #{x} register is expected to be a power in decibels
        relative to one milliwatt. It is replaced with the peak voltage of a
        sinusoid that would be needed to deliver the same power to a load
        resistor equal to #{Rref} (a predefined variable).
    """
  , aliases=['dbm2v']
)
dbmToVoltage.addTest(
    stimulus='10 dbmv'
  , result=1
  , units='V'
  , text='1 V'
)
dbmToVoltage.addTest(
    stimulus='-10 dbmv'
  , result=0.1
  , units='V'
  , text='100 mV'
)
dbmToVoltage.addTest(
    stimulus='5 "Ohms" =Rref 20 dbmv'
  , result=1
  , units='V'
  , text='1 V'
)

# current to dBm {{{3
currentToDbm = UnaryOp(
    'idbm'
  , lambda x, calc: 30+10*math.log10(x*x*calc.heap['Rref'][0]/2)
  , description="%(key)s: peak current to dBm"
  , needCalc=True
  , synopsis='#{x}, ... => 30+10*log10(((#{x}**2)*#{Rref}/2), ...'
  , summary="""
        The value in the #{x} register is expected to be the peak current of a
        sinusoid that is driving a load resistor equal to #{Rref} (a predefined
        variable).  It is replaced with the power delivered to the resistor in
        decibels relative to 1 milliwatt.
    """
  , aliases=['i2dbm']
)
currentToDbm.addTest(
    stimulus='2mA idbm'
  , result=-10
  , units=''
  , text='-10'
)
currentToDbm.addTest(
    stimulus='20uA i2dbm'
  , result=-50
  , units=''
  , text='-50'
)
currentToDbm.addTest(
    stimulus='5 "Ohms" =Rref 20uA idbm'
  , result=-60
  , units=''
  , text='-60'
)

# dBm to current {{{3
dbmToCurrent = UnaryOp(
    'dbmi'
  , lambda x, calc: math.sqrt(2*pow(10,(x - 30)/10)/calc.heap['Rref'][0])
  , description="%(key)s: dBm to peak current"
  , needCalc=True
  , units='A'
  , synopsis='#{x}, ... => sqrt(2*10**(#{x} - 30)/10)/#{Rref}), ...'
  , summary="""
        The value in the #{x} register is expected to be a power in decibels
        relative to one milliwatt. It is replaced with the peak current of a
        sinusoid that would be needed to deliver the same power to a load
        resistor equal to #{Rref} (a predefined variable).
    """
  , aliases=['dbm2i']
)
dbmToCurrent.addTest(
    stimulus='10 dbmi'
  , result=20e-3
  , units='A'
  , text='20 mA'
)
dbmToCurrent.addTest(
    stimulus='-10 dbmi'
  , result=2e-3
  , units='A'
  , text='2 mA'
)
dbmToCurrent.addTest(
    stimulus='5 "Ohms" =Rref -20 dbmi'
  , result=2e-3
  , units='A'
  , text='2 mA'
)

# Constants {{{2
constants = Category("Constants")

# pi {{{3
pi = Constant(
    'pi'
  , lambda: math.pi
  , description="%(key)s: the ratio of a circle's circumference to its diameter"
  , units='rads'
  , synopsis='... => #{pi}, ...'
  , summary="""
        The value of pi (3.141592...) is pushed on the stack into the #{x}
        register.
    """
)
pi.addTest(
    stimulus='pi'
  , result=math.pi
  , units='rads'
  , text='3.1416 rads'
)

# 2 pi {{{3
twoPi = Constant(
    '2pi'
  , lambda: 2*math.pi
  , description="%(key)s: the ratio of a circle's circumference to its radius"
  , units='rads'
  , synopsis='... => 2*#{pi}, ...'
  , summary="""
        Two times the value of pi (6.283185...) is pushed on the stack into the
        #{x} register.
    """
)
twoPi.addTest(
    stimulus='2pi'
  , result=2*math.pi
  , units='rads'
  , text='6.2832 rads'
)

# sqrt 2 {{{3
squareRoot2 = Constant(
    'rt2'
  , lambda: math.sqrt(2)
  , description="%(key)s: square root of two"
  , synopsis='... => sqrt(2), ...'
  , summary="""
        The square root of two (1.4142...) is pushed on the stack into the #{x}
        register.
    """
)
squareRoot2.addTest(
    stimulus='rt2'
  , result=math.sqrt(2)
  , units=''
  , text='1.4142'
)

# j {{{3
imaginaryUnit = Constant(
    'j'
  , lambda: 1j
  , description="%(key)s: imaginary unit (square root of -1)"
  , synopsis='... => #{j}, ...'
  , summary="""
        The imaginary unit (square root of -1) is pushed on the stack into
        the #{x} register.
    """
)
imaginaryUnit.addTest(
    stimulus='j'
  , result=1j
  , units=''
  , text='j'
)

# j2pi {{{3
imaginaryTwoPi = Constant(
    'j2pi'
  , lambda: 2j*math.pi
  , description="%(key)s: j*2*pi"
  , units='rads'
  , synopsis='... => #{j}*2*#{pi}, ...'
  , summary="""
        2 pi times the imaginary unit (j6.283185...) is pushed on the stack into
        the #{x} register.
    """
)
imaginaryTwoPi.addTest(
    stimulus='j2pi'
  , result=2j*math.pi
  , units='rads'
  , text='j6.2832 rads'
)

# planck constant {{{3
planckConstant = Constant(
    'h'
  , lambda: 6.62606957e-34
  , description="%(key)s: Planck constant"
  , units='J-s'
  , synopsis='... => #{h}, ...'
  , summary="""
        The Planck constant (6.62606957e-34 J-s) is pushed on the stack into
        the #{x} register.
    """
)
planckConstant.addTest(
    stimulus='h'
  , result=6.62606957e-34
  , units='J-s'
  , text='662.61e-36 J-s'
)

# reduced plank constant {{{3
planckConstantReduced = Constant(
    'hbar'
  , lambda: 1.054571726e-34
  , description="%(key)s: Reduced Planck constant"
  , units='J-s'
  , synopsis='... => #{h}/(2*#{pi}), ...'
  , summary="""
        The reduced Planck constant (1.054571726e-34 J-s) is pushed on the stack
        into the #{x} register.
    """
)
planckConstantReduced.addTest(
    stimulus='hbar'
  , result=1.054571726e-34
  , units='J-s'
  , text='105.46e-36 J-s'
)

# planck length {{{3
planckLength = Constant(
    'lP'
  , lambda: 1.616199e-35
  , description="%(key)s: Planck length"
  , units='m'
  , synopsis='... => #{lP}, ...'
  , summary="""
        The Planck length (sqrt(h*G/(2*pi*c**3)) or 1.616199e-35 m) is pushed on
        the stack into the #{x} register.
    """
)
planckLength.addTest(
    stimulus='lP'
  , result=1.616199e-35
  , units='m'
  , text='16.162e-36m'
)

# planck mass {{{3
planckMass = Constant(
    'mP'
  , lambda: 2.17651e-5
  , description="%(key)s: Planck mass"
  , units='g'
  , synopsis='... => #{mP}, ...'
  , summary="""
        The Planck mass (sqrt(h*c/(2*pi*G)) or 2.17651e-5 g) is pushed on
        the stack into the #{x} register.
    """
)
planckMass.addTest(
    stimulus='mP'
  , result=2.17651e-5
  , units='g'
  , text='21.765ug'
)

# planck temperature {{{3
planckTemperature = Constant(
    'TP'
  , lambda: 1.416833e32
  , description="%(key)s: Planck temperature"
  , units='K'
  , synopsis='... => #{TP}, ...'
  , summary="""
        The Planck temperature (mP*c**2/k or 1.416833e32 K) is pushed
        on the stack into the #{x} register.
    """
)
planckTemperature.addTest(
    stimulus='TP'
  , result=1.416833e32
  , units='K'
  , text='141.68e30_K'
)

# planck time {{{3
planckTime = Constant(
    'tP'
  , lambda: 5.39106e-44
  , description="%(key)s: Planck time"
  , units='s'
  , synopsis='... => #{tP}, ...'
  , summary="""
        The Planck time (sqrt(h*G/(2*pi*c**5)) or 5.39106e-44 s) is pushed on
        the stack into the #{x} register.
    """
)
planckTime.addTest(
    stimulus='tP'
  , result=5.39106e-44
  , units='s'
  , text='53.911e-45s'
)

# boltzmann constant {{{3
boltzmann = Constant(
    'k'
  , lambda: 1.3806488e-23
  , description="%(key)s: Boltzmann constant"
  , units='J/K'
  , synopsis='... => #{k}, ...'
  , summary="""
        The Boltzmann constant (R/NA) or 1.3806488e-23 J/K) is pushed on the
        stack into the #{x} register.
    """
)
boltzmann.addTest(
    stimulus='k'
  , result=1.3806488e-23
  , units='J/K'
  , text='13.806e-24 J/K'
)

# elementary charge {{{3
elementaryCharge = Constant(
    'q'
  , lambda: 1.602176565e-19
  , description="%(key)s: elementary charge (the charge of an electron)"
  , units='C'
  , synopsis='... => #{q}, ...'
  , summary="""
        The elementary charge (the charge of an electron or 1.602176565e-19 C)
        is pushed on the stack into the #{x} register.
    """
)
elementaryCharge.addTest(
    stimulus='q'
  , result=1.602176565e-19
  , units='C'
  , text='160.22e-21 C'
)

# mass of electron {{{3
massOfElectron = Constant(
    'me'
  , lambda: 9.10938291e-28
  , description="%(key)s: mass of an electron"
  , units='g'
  , synopsis='... => #{me}, ...'
  , summary="""
        The mass of an electron (9.10938291e-28 g) is pushed on the stack into
        the #{x} register.
    """
)
massOfElectron.addTest(
    stimulus='me'
  , result=9.10938291e-28
  , units='g'
  , text='910.94e-30 g'
)

# mass of proton {{{3
massOfProton = Constant(
    'mp'
  , lambda: 1.672621777e-24
  , description="%(key)s: mass of a proton"
  , units='g'
  , synopsis='... => #{mp}, ...'
  , summary="""
        The mass of a proton (1.672621777e-24 g) is pushed on the stack into
        the #{x} register.
    """
)
massOfProton.addTest(
    stimulus='mp'
  , result=1.672621777e-24
  , units='g'
  , text='1.6726e-24 g'
)

# speed of light {{{3
speedOfLight = Constant(
    'c'
  , lambda: 2.99792458e8
  , description="%(key)s: speed of light in a vacuum"
  , units='m/s'
  , synopsis='... => #{c}, ...'
  , summary="""
        The speed of light in a vacuum (2.99792458e8 m/s) is pushed on the stack
        into the #{x} register.
    """
)
speedOfLight.addTest(
    stimulus='c'
  , result=2.99792458e8
  , units='m/s'
  , text='299.79 Mm/s'
)

# gravitational constant {{{3
gravitationalConstant = Constant(
    'G'
  , lambda: 6.6746e-11
  , description="%(key)s: universal gravitational constant"
  , units="m^3/(kg-s^2)"
  , synopsis='... => #{G}, ...'
  , summary="""
        The universal gravitational constant (6.6746e-11 m^3/(kg-s^2)) is pushed
        on the stack into the #{x} register.
    """
)
gravitationalConstant.addTest(
    stimulus='G'
  , result=6.6746e-11
  , units='m^3/(kg-s^2)'
  , text='66.746 pm^3/(kg-s^2)'
)

# acceleration of gravity {{{3
standardAccelerationOfGravity = Constant(
    'g'
  , lambda: 9.80665
  , description="%(key)s: standard acceleration of gravity"
  , units='m/s^2'
  , synopsis='... => #{g}, ...'
  , summary="""
        The standard acceleration of gravity on earth (9.80665 m/s^2)) is pushed
        on the stack into the #{x} register.
    """
)
standardAccelerationOfGravity.addTest(
    stimulus='g'
  , result=9.80665
  , units='m/s^2'
  , text='9.8066 m/s^2'
)

# avogadro constant {{{3
avogadroConstant = Constant(
    'NA'
  , lambda: 6.02214129e23
  , description="%(key)s: Avagadro Number"
  , units='/mol'
  , synopsis='... => #{NA}, ...'
  , summary="""
        Avogadro constant (6.02214129e23) is pushed on the stack into the #{x}
        register.
    """
)
avogadroConstant.addTest(
    stimulus='NA'
  , result=6.02214129e23
  , units='/mol'
  , text='602.21e21 /mol'
)

# gas constant {{{3
molarGasConstant = Constant(
    'R'
  , lambda: 8.3144621
  , description="%(key)s: molar gas constant"
  , units='J/(mol-K)'
  , synopsis='... => #{R}, ...'
  , summary="""
        The molar gas constant (8.3144621 J/(mol-K)) is pushed on the stack into
        the #{x} register.
    """
)
molarGasConstant.addTest(
    stimulus='R'
  , result=8.3144621
  , units='J/(mol-K)'
  , text='8.3145 J/(mol-K)'
)

# zero celsius {{{3
zeroCelsius = Constant(
    '0C'
  , lambda: 273.15
  , description="%(key)s: 0 Celsius in Kelvin"
  , units='K'
  , synopsis='... => #{0C}, ...'
  , summary="""
        Zero celsius in kelvin (273.15 K) is pushed on the stack into
        the #{x} register.
    """
)
zeroCelsius.addTest(
    stimulus='0C'
  , result=273.15
  , units='K'
  , text='273.15 K'
)

# free space permittivity {{{3
freeSpacePermittivity = Constant(
    'eps0'
  , lambda: 8.854187817e-12
  , description="%(key)s: permittivity of free space"
  , units='F/m'
  , synopsis='... => #{eps0}, ...'
  , summary="""
        The permittivity of free space (8.854187817e-12 F/m) is pushed on the
        stack into the #{x} register.
    """
)
freeSpacePermittivity.addTest(
    stimulus='eps0'
  , result=8.854187817e-12
  , units='F/m'
  , text='8.8542 pF/m'
)

# free space permeability {{{3
freeSpacePermeability = Constant(
    'mu0'
  , lambda: 4e-7*math.pi
  , description="%(key)s: permeability of free space"
  , units='H/m'
  , synopsis='... => #{mu0}, ...'
  , summary="""
        The permeability of free space (4e-7*pi H/m) is pushed on the
        stack into the #{x} register.
    """
)
freeSpacePermeability.addTest(
    stimulus='mu0'
  , result=4e-7*math.pi
  , units='H/m'
  , text='1.2566 uH/m'
)

# free space characteristic impedance {{{3
freeSpaceCharacteristicImpedance = Constant(
    'Z0'
  , lambda: 376.730313461
  , description="%(key)s: Characteristic impedance of free space"
  , units='Ohms'
  , synopsis='... => #{Z0}, ...'
  , summary="""
        The characteristic impedance of free space (376.730313461 Ohms) is
        pushed on the stack into the #{x} register.
    """
)
freeSpaceCharacteristicImpedance.addTest(
    stimulus='Z0'
  , result=376.730313461
  , units='Ohms'
  , text='376.73 Ohms'
)

# Numbers {{{2
numbers = Category("Numbers")

# real number in engineering notation {{{3
# accepts numbers both with and without SI scale factors. If an SI scale factor
# is present, then attached trailing units can also be given. It is also
# possible to include commas in the number anywhere a digit can be given. It is
# a little crude in that it allows commas in the mantissa and adjacent to the
# decimal point, but other than that it works reasonably well.
def siNumber(matches):
    sign = matches[0]
    currency = matches[1]
    imag = matches[2] == 'j'
    unsignedNum = matches[3].replace(',', '')
    num = from_eng_fmt(sign+unsignedNum)
    if imag:
       num = (1j * num[0], num[1])
    if currency:
        if num[1]:
            warn("Too many units ($ and %s)." % num[1])
        else:
            num = (num[0], currency)
    return num

engineeringNumber = Number(
    pattern=r'\A([-+]?)(\$?)(j?)((([0-9],?)*)(\.?(,?[,0-9])+)(([YZEPTGMKk_munpfazy])([a-zA-Z_]*))?)\Z'
  , action=siNumber
  , name='engnum'
  , description="<#{N}[.#{M}][#{S}[#{U}]]>: a real number"
  , synopsis='... => #{num}, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is the
        integer portion of the mantissa and #{M} is an optional fractional part.
        #{S} is a letter that represents an SI scale factor. #{U} the optional
        units (must not contain special characters).  For example, 10MHz
        represents 1e7 Hz.
    """
)
engineeringNumber.addTest(
    stimulus='1m'
  , result=1e-3
  , units=''
  , text='1m'
)
engineeringNumber.addTest(
    stimulus='+10.1n'
  , result=10.1e-9
  , units=''
  , text='10.1n'
)
engineeringNumber.addTest(
    stimulus='-1.1GHz'
  , result=-1.1e9
  , units='Hz'
  , text='-1.1 GHz'
)
engineeringNumber.addTest(
    stimulus='$100k'
  , result=1e5
  , units='$'
  , text='$100k'
)
engineeringNumber.addTest(
    stimulus='-$20M'
  , result=-20e6
  , units='$'
  , text='-$20M'
)
engineeringNumber.addTest(
    stimulus='.2MOhms'
  , result=2e5
  , units='Ohms'
  , text='200 kOhms'
)
engineeringNumber.addTest(
    stimulus='1000'
  , result=1000.0
  , units=''
  , text='1k'
)
engineeringNumber.addTest(
    stimulus='$1,000,000'
  , result=1e6
  , units='$'
  , text='$1M'
)
engineeringNumber.addTest(
    stimulus='$1,000K'
  , result=1e6
  , units='$'
  , text='$1M'
)
engineeringNumber.addTest(
    stimulus='$1,000,000.00'
  , result=1e6
  , units='$'
  , text='$1M'
)
engineeringNumber.addTest(
    stimulus='1,000.00K'
  , result=1e6
  , units=''
  , text='1M'
)
engineeringNumber.addTest(
    stimulus='$1,000.00K'
  , result=1e6
  , units='$'
  , text='$1M'
)
engineeringNumber.addTest(
    stimulus='$1,000.00'
  , result=1e3
  , units='$'
  , text='$1k'
)
engineeringNumber.addTest(
    stimulus='$1,000'
  , result=1e3
  , units='$'
  , text='$1k'
)
engineeringNumber.addTest(
    stimulus='$1000'
  , result=1e3
  , units='$'
  , text='$1k'
)
engineeringNumber.addTest(
    stimulus='+$1000'
  , result=1e3
  , units='$'
  , text='$1k'
)
engineeringNumber.addTest(
    stimulus='-$1000'
  , result=-1e3
  , units='$'
  , text='-$1k'
)
engineeringNumber.addTest(
    stimulus='j1,000.00KOhms'
  , result=1j * 1e6
  , units='Ohms'
  , text='j1 MOhms'
)
engineeringNumber.addTest(
    stimulus='j1,000.00K'
  , result=1j * 1e6
  , units=''
  , text='j1M'
)
engineeringNumber.addTest(
    stimulus='j1,000.00'
  , result=1j * 1e3
  , units=''
  , text='j1k'
)
engineeringNumber.addTest(
    stimulus='j1,000'
  , result=1j * 1e3
  , units=''
  , text='j1k'
)
engineeringNumber.addTest(
    stimulus='j1000'
  , result=1j * 1e3
  , units=''
  , text='j1k'
)
engineeringNumber.addTest(
    stimulus='j1'
  , result=1j
  , units=''
  , text='j'
)
engineeringNumber.addTest(
    stimulus='j1.5'
  , result=1.5j
  , units=''
  , text='j1.5'
)
engineeringNumber.addTest(
    stimulus='+j1'
  , result=1j
  , units=''
  , text='j'
)
engineeringNumber.addTest(
    stimulus='-j1'
  , result=-1j
  , units=''
  , text='-0 - j'
)
engineeringNumber.addTest(
    stimulus='$j1'
  , result=1j
  , units='$'
  , text='j $'
)
engineeringNumber.addTest(
    stimulus='+$j1'
  , result=1j
  , units='$'
  , text='j $'
)
engineeringNumber.addTest(
    stimulus='-$j1'
  , result=-1j
  , units='$'
  , text='-$0 - j$'
)

def sciNumber(matches):
    sign = matches[0]
    currency = matches[1]
    imag = matches[2] == 'j'
    unsignedNum = matches[3].replace(',', '')
    units = matches[4]
    num = from_eng_fmt(sign+unsignedNum+units)
    if imag:
       num = (1j * num[0], num[1])
    if currency:
        if num[1]:
            warn("Too many units ($ and %s)." % num[1])
        else:
            num = (num[0], currency)
    return num

# real number in scientific notation {{{3
scientificNumber = Number(
    pattern=r'\A([-+]?)(\$?)(j?)([0-9]*\.?[0-9]+[eE][-+]?[0-9]+)([a-zA-Z_]*)\Z'
  , action=sciNumber
  , name='scinum'
  , description="<#{N}[.#{M}]>e<#{E}[#{U}]>: a real number in scientific notation"
  , synopsis='... => #{num}, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is the
        integer portion of the mantissa and #{M} is an optional fractional part.
        #{E} is an integer exponent. #{U} the optional units (must not contain
        special characters).  For example, 2.2e-8F represents 22nF.
    """
)
scientificNumber.addTest(
    stimulus='20.0e12'
  , result=20e12
  , units=''
  , text='20T'
)
scientificNumber.addTest(
    stimulus='+2.0e+9'
  , result=2e9
  , units=''
  , text='2G'
)
scientificNumber.addTest(
    stimulus='-5.0e-9'
  , result=-5e-9
  , units=''
  , text='-5n'
)
scientificNumber.addTest(
    stimulus='.5e-12F'
  , result=5e-13
  , units='F'
  , text='500 fF'
)
scientificNumber.addTest(
    stimulus='$500e6'
  , result=5e8
  , units='$'
  , text='$500M'
)
scientificNumber.addTest(
    stimulus='+$20e+03'
  , result=2e4
  , units='$'
  , text='$20k'
)
scientificNumber.addTest(
    stimulus='-$2.0e-3'
  , result=-2e-3
  , units='$'
  , text='-$2m'
)
scientificNumber.addTest(
    stimulus='j1e6Ohms'
  , result=1j * 1e6
  , units='Ohms'
  , text='j1 MOhms'
)
scientificNumber.addTest(
    stimulus='j1000e3'
  , result=1j * 1e6
  , units=''
  , text='j1M'
)
scientificNumber.addTest(
    stimulus='+j1.5e-6Ohms'
  , result=1.5e-6j
  , units='Ohms'
  , text='j1.5 uOhms'
)
scientificNumber.addTest(
    stimulus='-j1.5e-6'
  , result=-1.5e-6j
  , units=''
  , text='-0 - j1.5u'
)
scientificNumber.addTest(
    stimulus='$j1.5e-6'
  , result=1.5e-6j
  , units='$'
  , text='j$1.5u'
)
scientificNumber.addTest(
    stimulus='+$j1.5e-6'
  , result=1.5e-6j
  , units='$'
  , text='j$1.5u'
)
scientificNumber.addTest(
    stimulus='-$j1.5e-6'
  , result=-1.5e-6j
  , units='$'
  , text='-$0 - j$1.5u'
)

# hexadecimal number {{{3
hexadecimalNumber = Number(
    pattern=r"\A([-+]?)0[xX]([0-9a-fA-F]+)\Z"
  , action=lambda matches: (int(matches[0]+matches[1], base=16), '')
  , name='hexnum'
  , description="0x<#{N}>: a hexadecimal number"
  , synopsis='... => #{num}, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 16 (use a-f to represent digits greater than 9).  For
        example, 0xFF represents the hexadecimal number FF or the decimal number
        255.
    """
)
hexadecimalNumber.addTest(
    stimulus='0x1f 0xAC + hex'
  , result=203
  , units=''
  , text='0x00cb'
)

# octal number {{{3
# oct must be before eng if we use the 0NNN form (as opposed to OoNNN form)
octalNumber = Number(
    pattern=r"\A([-+]?)0[oO]([0-7]+)\Z"
  , action=lambda matches: (int(matches[0]+matches[1], base=8), '')
  , name='octnum'
  , description="0o<#{N}>: a number in octal"
  , synopsis='... => #{num}, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 8 (it must not contain the digits 8 or 9).  For example,
        0o77 represents the octal number 77 or the decimal number 63.
    """
)
octalNumber.addTest(
    stimulus='0o77 0o33 + oct'
  , result=90
  , units=''
  , text='0o0132'
)

# binary number {{{3
binaryNumber = Number(
    pattern=r"\A([-+]?)0[bB]([01]+)\Z"
  , action=lambda matches: (int(matches[0]+matches[1], base=2), '')
  , name='binnum'
  , description="0b<#{N}>: a number in binary"
  , synopsis='... => #{num}, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 2 (it may contain only the digits 0 or 1).  For example,
        0b1111 represents the octal number 1111 or the decimal number 15.
    """
)
binaryNumber.addTest(
    stimulus='0b1111 0b0001 +'
  , result=16
  , units=''
  , text='16'
)

# hexadecimal number in verilog notation {{{3
# Verilog constants are incompatible with generalized units because the
# single quote in the Verilog constant conflicts with the single quotes that
# surround generalized units (ex: 6.28e6 'rads/s').
# Is okay now, I switched the quote characters to free up single quotes.
verilogHexadecimalNumber = Number(
    pattern=r"\A([-+]?)'[hH]([0-9a-fA-F_]*[0-9a-fA-F])\Z"
  , action=lambda matches: (int(matches[0]+matches[1].replace('_',''), base=16), '')
  , name='vhexnum'
  , description="'h<#{N}>: a number in Verilog hexadecimal notation"
  , synopsis='... => #{num}, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 16 (use a-f to represent digits greater than 9).  For
        example, 'hFF represents the hexadecimal number FF or the decimal number
        255.
    """
)
verilogHexadecimalNumber.addTest(
    stimulus="'h1f 'hAC + vhex"
  , result=203
  , units=''
  , text="'h00cb"
)

# decimal number in verilog notation {{{3
verilogDecimalNumber = Number(
    pattern=r"\A([-+]?)'[dD]([0-9_]*[0-9]+)\Z"
  , action=lambda matches: (int(matches[0]+matches[1].replace('_',''), base=10), '')
  , name='vdecnum'
  , description="'d<#{N}>: a number in Verilog decimal"
  , synopsis='... => #{num}, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 10.  For example, 'd99 represents the decimal number 99.
    """
)
verilogDecimalNumber.addTest(
    stimulus="'d99 'd01 + vdec"
  , result=100
  , units=''
  , text="'d0100"
)

# octal number in verilog notation {{{3
verilogOctalNumber = Number(
    pattern=r"\A([-+]?)'[oO]([0-7_]*[0-7]+)\Z"
  , action=lambda matches: (int(matches[0]+matches[1].replace('_',''), base=8), '')
  , name='voctnum'
  , description="'o<#{N}>: a number in Verilog octal"
  , synopsis='... => #{num}, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 8 (it must not contain the digits 8 or 9).  For example,
        'o77 represents the octal number 77 or the decimal number 63.
    """
)
verilogOctalNumber.addTest(
    stimulus="'o77 'o33 + voct"
  , result=90
  , units=''
  , text="'o0132"
)

# binary number in verilog notation {{{3
verilogBinaryNumber = Number(
    pattern=r"\A([-+]?)'[bB]([01_]*[01]+)\Z"
  , action=lambda matches: (int(matches[0]+matches[1].replace('_',''), base=2), '')
  , name='vbinnum'
  , description="'b<#{N}>: a number in Verilog binary"
  , synopsis='... => #{num}, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 2 (it may contain only the digits 0 or 1).  For example,
        'b1111 represents the binary number 1111 or the decimal number 15.
    """
)
verilogBinaryNumber.addTest(
    stimulus="'b1111 'b0001 +"
  , result=16
  , units=''
  , text="16"
)

# Number Formats {{{2
numberFormats = Category("Number Formats")

# fixed format {{{3
setFixedFormat = SetFormat(
    pattern=r'\Afix(\d{1,2})?\Z'
  , action=lambda num, digits: '{0:.{prec}f}'.format(num, prec=digits)
  , name='fix'
  , actionTakesUnits=False
  , description="%(name)s[<#{N}>]: use fixed notation"
  , summary="""
        Numbers are displayed with a fixed number of digits to the right of the
        decimal point. If an optional whole number #{N} immediately follows
        #{fix}, the number of digits to the right of the decimal point is set to
        #{N}. 
    """
)
setFixedFormat.addTest(
    stimulus="1e6 fix0"
  , result=1e6
  , units=''
  , text="1000000"
)
setFixedFormat.addTest(
    stimulus="pi fix"
  , result=math.pi
  , units='rads'
  , text="3.1416rads"
)
setFixedFormat.addTest(
    stimulus="pi fix8"
  , result=math.pi
  , units='rads'
  , text="3.14159265rads"
)
setFixedFormat.addTest(
    stimulus="$100 fix2"
  , result=100
  , units='$'
  , text="$100.00"
)

# engineering format {{{3
setEngineeringFormat = SetFormat(
    pattern=r'\Aeng(\d{1,2})?\Z'
  , action=lambda num, units, digits: to_eng_fmt(num, units, prec=digits)
  , name='eng'
  , actionTakesUnits=True
  , description="%(name)s[<#{N}>]: use engineering notation"
  , summary="""
        Numbers are displayed with a fixed number of digits of precision and the
        SI scale factors are used to convey the exponent when possible.  If an
        optional whole number #{N} immediately follows #{eng}, the precision is
        set to #{N} digits. 
    """
)
setEngineeringFormat.addTest(
    stimulus="pi 1e3 * eng"
  , result=1e3*math.pi
  , units=''
  , text="3.1416k"
)
setEngineeringFormat.addTest(
    stimulus='pi 1e3 * "rads" eng8'
  , result=1e3*math.pi
  , units='rads'
  , text="3.14159265 krads"
)

# scientific format {{{3
setScientificFormat = SetFormat(
    pattern=r'\Asci(\d{1,2})?\Z'
  , action=lambda num, digits: '{0:.{prec}e}'.format(num, prec=digits)
  , name='sci'
  , actionTakesUnits=False
  , description="%(name)s[<#{N}>]: use scientific notation"
  , summary="""
        Numbers are displayed with a fixed number of digits of precision and the
        exponent is given explicitly as an integer.  If an optional whole number
        #{N} immediately follows #{sci}, the precision is set to #{N} digits. 
    """
)
setScientificFormat.addTest(
    stimulus="pi 1e3 * sci"
  , result=1e3*math.pi
  , units=''
  , text="3.1416e+03"
)
setScientificFormat.addTest(
    stimulus='pi 1e3 * "rads" sci8'
  , result=1e3*math.pi
  , units='rads'
  , text="3.14159265e+03rads"
)
setScientificFormat.addTest(
    stimulus='1e-10 sci8'
  , result=1e-10
  , units=''
  , text="1.00000000e-10"
)
setScientificFormat.addTest(
    stimulus='$100 sci0'
  , result=100
  , units='$'
  , text="$1e+02"
)

# hexadecimal format {{{3
setHexadecimalFormat = SetFormat(
    pattern=r'\Ahex(\d{1,2})?\Z'
  , action=lambda num, units, digits: '{0:#0{width}x}'.format(int(round(num)), width=digits+2)
  , name='hex'
  , actionTakesUnits=True
  , description="%(name)s[<#{N}>]: use hexadecimal notation"
  , summary="""
        Numbers are displayed in base 16 (a-f are used to represent digits
        greater than 9) with a fixed number of digits.  If an optional whole
        number #{N} immediately follows #{hex}, the number of digits displayed
        is set to #{N}. 
    """
)
setHexadecimalFormat.addTest(
    stimulus="0xFF hex"
  , result=0xFF
  , units=''
  , text="0x00ff"
)
setHexadecimalFormat.addTest(
    stimulus="0xBEEF hex0"
  , result=0xBEEF
  , units=''
  , text="0xbeef"
)
setHexadecimalFormat.addTest(
    stimulus="0xDeadBeef hex8"
  , result=0xDeadBeef
  , units=''
  , text="0xdeadbeef"
)

# octal format {{{3
setOctalFormat = SetFormat(
    pattern=r'\Aoct(\d{1,2})?\Z'
  , action=lambda num, units, digits: '{0:#0{width}o}'.format(int(round(num)), width=digits+2)
  , name='oct'
  , actionTakesUnits=True
  , description="%(name)s[<#{N}>]: use octal notation"
  , summary="""
        Numbers are displayed in base 8 with a fixed number of digits.  If an
        optional whole number #{N} immediately follows #{oct}, the number of
        digits displayed is set to #{N}. 
    """
)
setOctalFormat.addTest(
    stimulus="0o777 oct"
  , result=0o777
  , units=''
  , text="0o0777"
)
setOctalFormat.addTest(
    stimulus="0o77 oct0"
  , result=0o77
  , units=''
  , text="0o77"
)
setOctalFormat.addTest(
    stimulus="0o76543210 oct8"
  , result=0o76543210
  , units=''
  , text="0o76543210"
)

# binary format {{{3
setBinaryFormat = SetFormat(
    pattern=r'\Abin(\d{1,2})?\Z'
  , action=lambda num, units, digits: '{0:#0{width}b}'.format(int(round(num)), width=digits+2)
  , name='bin'
  , actionTakesUnits=True
  , description="%(name)s[<#{N}>]: use binary notation"
  , summary="""
        Numbers are displayed in base 2 with a fixed number of digits.  If an
        optional whole number #{N} immediately follows #{bin}, the number of
        digits displayed is set to #{N}. 
    """
)
setBinaryFormat.addTest(
    stimulus="0b11 bin"
  , result=0b11
  , units=''
  , text="0b0011"
)
setBinaryFormat.addTest(
    stimulus="0b11 bin0"
  , result=0b11
  , units=''
  , text="0b11"
)
setBinaryFormat.addTest(
    stimulus="0b10011001 bin8"
  , result=0b10011001
  , units=''
  , text="0b10011001"
)

# verilog hexadecimal format {{{3
setVerilogHexadecimalFormat = SetFormat(
    pattern=r'\Avhex(\d{1,2})?\Z'
  , action=lambda num, units, digits: "'h{0:0{width}x}".format(int(round(num)), width=digits)
  , name='vhex'
  , actionTakesUnits=True
  , description="%(name)s[<#{N}>]: use Verilog hexadecimal notation"
  , summary="""
        Numbers are displayed in base 16 in Verilog format (a-f are used to
        represent digits greater than 9) with a fixed number of digits.  If an
        optional whole number #{N} immediately follows #{vhex}, the number of
        digits displayed is set to #{N}. 
    """
)
setVerilogHexadecimalFormat.addTest(
    stimulus="'hFF vhex"
  , result=0xFF
  , units=''
  , text="'h00ff"
)
setVerilogHexadecimalFormat.addTest(
    stimulus="'hBEEF vhex0"
  , result=0xBEEF
  , units=''
  , text="'hbeef"
)
setVerilogHexadecimalFormat.addTest(
    stimulus="'hDeadBeef vhex8"
  , result=0xDeadBeef
  , units=''
  , text="'hdeadbeef"
)

# verilog decimal format {{{3
setVerilogDecimalFormat = SetFormat(
    pattern=r'\Avdec(\d{1,2})?\Z'
  , action=lambda num, units, digits: "'d{0:0{width}d}".format(int(round(num)), width=digits)
  , name='vdec'
  , actionTakesUnits=True
  , description="%(name)s[<#{N}>]: use Verilog decimal notation"
  , summary="""
        Numbers are displayed in base 10 in Verilog format with a fixed number
        of digits.  If an optional whole number #{N} immediately follows
        #{vdec}, the number of digits displayed is set to #{N}. 
    """
)
setVerilogDecimalFormat.addTest(
    stimulus="'d99 vdec"
  , result=99
  , units=''
  , text="'d0099"
)
setVerilogDecimalFormat.addTest(
    stimulus="'d0 vdec0"
  , result=0
  , units=''
  , text="'d0"
)
setVerilogDecimalFormat.addTest(
    stimulus="'d9876543210 vdec10"
  , result=9876543210
  , units=''
  , text="'d9876543210"
)

# verilog octal format {{{3
setVerilogOctalFormat = SetFormat(
    pattern=r'\Avoct(\d{1,2})?\Z'
  , action=lambda num, units, digits: "'o{0:0{width}o}".format(int(round(num)), width=digits)
  , name='voct'
  , actionTakesUnits=True
  , description="%(name)s[<#{N}>]: use Verilog octal notation"
  , summary="""
        Numbers are displayed in base 8 in Verilog format with a fixed number of
        digits.  If an optional whole number #{N} immediately follows #{voct},
        the number of digits displayed is set to #{N}. 
    """
)
setVerilogOctalFormat.addTest(
    stimulus="'o777 voct"
  , result=0o777
  , units=''
  , text="'o0777"
)
setVerilogOctalFormat.addTest(
    stimulus="'o77 voct0"
  , result=0o77
  , units=''
  , text="'o77"
)
setVerilogOctalFormat.addTest(
    stimulus="'o76543210 voct8"
  , result=0o76543210
  , units=''
  , text="'o76543210"
)

# verilog binary format {{{3
setVerilogBinaryFormat = SetFormat(
    pattern=r'\Avbin(\d{1,2})?\Z'
  , action=lambda num, units, digits: "'b{0:0{width}b}".format(int(round(num)), width=digits)
  , name='vbin'
  , actionTakesUnits=True
  , description="%(name)s[<#{N}>]: use Verilog binary notation"
  , summary="""
        Numbers are displayed in base 2 in Verilog format with a fixed number of
        digits.  If an optional whole number #{N} immediately follows #{vbin},
        the number of digits displayed is set to #{N}. 
    """
)
setVerilogBinaryFormat.addTest(
    stimulus="'b11 vbin"
  , result=0b11
  , units=''
  , text="'b0011"
)
setVerilogBinaryFormat.addTest(
    stimulus="'b11 vbin0"
  , result=0b11
  , units=''
  , text="'b11"
)
setVerilogBinaryFormat.addTest(
    stimulus="'b10011001 vbin8"
  , result=0b10011001
  , units=''
  , text="'b10011001"
)

# Variables {{{2
variableCommands = Category("Variable Commands")

# store to variable {{{3
storeToVariable = Store(
    'store'
  , description='=<#{name}>: store value into a variable'
  , synopsis='... => ...'
  , summary="""
        Store the value in the #{x} register into a variable with the given
        name.
    """
)
storeToVariable.addTest(
    stimulus='1MHz =freq 10us =time 2pi * * time freq *'
  , result=10
  , units=''
  , text='10'
)
storeToVariable.addTest(
    stimulus='1pF =c pop c'
  , result=1e-12
  , units='F'
  , text='1 pF'
  , warnings=['c: variable has overridden built-in.']
)

# recall from variable {{{3
recallFromVariable = Recall(
    'recall'
  , description='<#{name}>: recall value of a variable'
  , synopsis='... => #{name}, ...'
  , summary="""
        Place the value of the variable with the given name into the #{x}
        register.
    """
)
recallFromVariable.addTest(
    stimulus='1MHz =freq 2pi * "rads" =omega 10us =time clstack freq'
  , result=1e6
  , units='Hz'
  , text='1 MHz'
)
recallFromVariable.addTest(
    stimulus='freq'
  , result=0
  , units=''
  , text='0'
  , error='freq: variable does not exist'
)

# list variables {{{3
listVariables = Command(
    'vars'
  , lambda calc: calc.heap.display()
  , description="%(key)s: print variables"
  , summary="""
        List all defined variables and their values.
    """
)
listVariables.addTest(
    stimulus='1MHz =freq 10us =time vars'
  , result=10e-6
  , units='s'
  , text='10 us'
  , messages=[
        '  Rref: 50 Ohms'
      , '  freq: 1 MHz'
      , '  time: 10 us'
    ]
)

# Stack {{{2
stackCommands = Category("Stack Commands")

# swap {{{3
swapXandY = Command(
    'swap'
  , Calculator.swap
  , description='%(key)s: swap x and y'
  , synopsis='#{x}, #{y}, ... => #{y}, #{x}, ...'
  , summary="""
        The values in the #{x} and #{y} registers are swapped.
    """
)
swapXandY.addTest(
    stimulus='1MHz 10us swap'
  , result=1e6
  , units='Hz'
  , text='1 MHz'
)

# dup {{{3
duplicateX = Dup(
    'dup'
  , None
  , description="%(key)s: duplicate #{x}"
  , synopsis='#{x}, ... => #{x}, #{x}, ...'
  , summary="""
        The value in the #{x} register is pushed onto the stack again.
    """
  , aliases=['enter']
)
duplicateX.addTest(
    stimulus='1MHz 10us dup'
  , result=10e-6
  , units='s'
  , text='10 us'
)
duplicateX.addTest(
    stimulus='1MHz 10us dup swap'
  , result=10e-6
  , units='s'
  , text='10 us'
)

# pop {{{3
popX = Command(
    'pop'
  , Calculator.pop
  , description='%(key)s: discard x'
  , synopsis='#{x}, ... => ...'
  , summary="""
        The value in the #{x} register is pulled from the stack and discarded.
    """
  , aliases=['clrx']
)
popX.addTest(
    stimulus='1MHz 10us pop'
  , result=1e6
  , units='Hz'
  , text='1 MHz'
)
popX.addTest(
    stimulus='pi eps0 q pop pop pop pop'
  , result=0
  , units=''
  , text='0'
)

# stack {{{3
listStack = Command(
    'stack'
  , lambda calc: calc.stack.display()
  , description="%(key)s: print stack"
  , summary="""
        Print all the values stored on the stack.
    """
)
listStack.addTest(
    stimulus='1MHz 10us q 36 stack'
  , result=36
  , units=''
  , text='36'
  , messages=[
        '     1 MHz'
      , '     10 us'
      , '  y: 160.22e-21 C'
      , '  x: 36'
    ]
)

# clstack {{{3
clearStack = Command(
    'clstack'
  , lambda calc: calc.stack.clear()
  , description="%(key)s: clear stack"
  , synopsis='... =>'
  , summary="""
        Remove all values from the stack.
    """
)
listStack.addTest(
    stimulus='1MHz 10us clstack stack'
  , result=0
  , units=''
  , text='0'
)

# Miscellaneous {{{2
miscellaneousCommands = Category("Miscellaneous Commands")

printText = Print(
    name='print'
  , description='`<text>`: print text'
  , summary="""\
        Print "text" (the contents of the back-quotes) to the terminal.
        Generally used in scripts to report and annotate results.  Any instances
        of $N or ${N} are replaced by the value of register N, where 0
        represents the #{x} register, 1 represents the #{y} register, etc.  Any
        instances of $Var or ${Var} are replaced by the value of the variable
        #{Var}.
    """
)
printText.addTest(
    stimulus='2 1 0 `Hello world!`'
  , result=0
  , units=''
  , text='0'
  , messages=["Hello world!"]
)
printText.addTest(
    stimulus='2 1 0 `$0`'
  , result=0
  , units=''
  , text='0'
  , messages=["0"]
)
printText.addTest(
    stimulus='2 1 0 `$0 is x`'
  , result=0
  , units=''
  , text='0'
  , messages=["0 is x"]
)
printText.addTest(
    stimulus='2 1 0 `x is $0`'
  , result=0
  , units=''
  , text='0'
  , messages=["x is 0"]
)
printText.addTest(
    stimulus='2 1 0 `x is $0, y is $1`'
  , result=0
  , units=''
  , text='0'
  , messages=["x is 0, y is 1"]
)
printText.addTest(
    stimulus='2 1 0 `x is ${0}, y is ${1}`'
  , result=0
  , units=''
  , text='0'
  , messages=["x is 0, y is 1"]
)
printText.addTest(
    stimulus='2 1 0 `x is $0, y is $1, z = $2`'
  , result=0
  , units=''
  , text='0'
  , messages=["x is 0, y is 1, z = 2"]
)
printText.addTest(
    stimulus='2 1 0 `x is $0, y is $1, z = $2, t is $3`'
  , result=0
  , units=''
  , text='0'
  , messages=["x is 0, y is 1, z = 2, t is $?3?"]
  , warnings=["$3: unknown."]
)
printText.addTest(
    stimulus='`I have $Rref, you have $$50`'
  , result=0
  , units=''
  , text='0'
  , messages=["I have 50 Ohms, you have $50"]
)
printText.addTest(
    stimulus='`I have ${Rref}, you have $$50`'
  , result=0
  , units=''
  , text='0'
  , messages=["I have 50 Ohms, you have $50"]
)
printText.addTest(
    stimulus='`I have $Q, you have $$50`'
  , result=0
  , units=''
  , text='0'
  , messages=["I have $?Q?, you have $50"]
  , warnings=["$Q: unknown."]
)
printText.addTest(
    stimulus='$100 ``'
  , result=100
  , units='$'
  , text='$100'
  , messages=["$100"]
)

setUnits = SetUnits(
    name='units'
  , description='"<units>": set the units of the x register'
  , synopsis='x, ... => x "units", ...'
  , summary="""\
        The units given are applied to the value in the #{x} register.
        The actual value is unchanged.
    """
)
setUnits.addTest(
    stimulus='100M "V/s"'
  , result=1e8
  , units='V/s'
  , text='100 MV/s'
)

printAbout = Command(
    'about'
  , Calculator.aboutMsg
  , description="%(key)s: print information about this calculator"
)
printAbout.addTest(
    stimulus='about'
  , messages=True
)

terminate = Command(
    'quit'
  , Calculator.quit
  , description="%(key)s: quit (:q or ^D also works)"
  , aliases=[':q']
)

printHelp = Command(
    'help'
  , Calculator.displayHelp
  , description="%(key)s: print a summary of the available features"
)
printHelp.addTest(
    stimulus='help'
  , messages=True
)

detailedHelp = Help(
    name='?'
  , description="%(name)s[<topic>]: detailed help on a particular topic"
  , summary="""\
        A topic, in the form of a symbol or name, may follow the question mark,
        in which case a detailed description will be printed for that topic.
        If no topic is given, a list of available topics is listed.
    """
)
detailedHelp.addTest(
    stimulus='?'
  , messages=True
)
detailedHelp.addTest(
    stimulus='??'
  , messages=True
)
detailedHelp.addTest(
    stimulus='?XXXXXXXXXX'
  , messages=True
  , warnings=['XXXXXXXXXX: not found.\n']
)
# The detailed help command with arguments is tested in test.ec.py.


# Action Sublists {{{1
# Arithmetic Operators {{{2
arithmeticOperatorActions = [
    arithmeticOperators,
    addition,
    subtraction,
    multiplication,
    trueDivision,
    floorDivision,
    modulus,
    negation,
    reciprocal,
    ceiling,
    floor,
    factorial,
    percentChange,
    parallel,
]

# Logs, Powers, and Exponentials {{{2
logPowerExponentialActions = [
    powersAndLogs,
    power,
    exponential,
    naturalLog,
    tenPower,
    commonLog,
    twoPower,
    binaryLog,
    square,
    squareRoot,
    cubeRoot,
]

# Trig Functions {{{2
trigFunctionActions = [
    trigFunctions,
    sine,
    cosine,
    tangent,
    arcSine,
    arcCosine,
    arcTangent,
    setRadiansMode,
    setDegreesMode,
]

# Complex and Vector Functions {{{2
complexVectorFunctionActions = [
    complexAndVectorFunctions,
    absoluteValue,
    argument,
    hypotenuse,
    arcTangent2,
    rectangularToPolar,
    polarToRectangular,
]

# Hyperbolic Functions {{{2
hyperbolicFunctionActions = [
    hyperbolicFunctions,
    hyperbolicSine,
    hyperbolicCosine,
    hyperbolicTangent,
    hyperbolicArcSine,
    hyperbolicArcCosine,
    hyperbolicArcTangent,
]

# Decibel Functions {{{2
decibelFunctionActions = [
    decibelFunctions,
    decibels20,
    antiDecibels20,
    decibels10,
    antiDecibels10,
    voltageToDbm,
    dbmToVoltage,
    currentToDbm,
    dbmToCurrent,
]

# Constants {{{2
commonConstantActions = [
    constants,
    pi,
    twoPi,
    squareRoot2,
    zeroCelsius,
]
engineeringConstantActions = [
    imaginaryUnit,
    imaginaryTwoPi,
    boltzmann,
    planckConstant,
    elementaryCharge,
    speedOfLight,
    freeSpacePermittivity,
    freeSpacePermeability,
    freeSpaceCharacteristicImpedance,
]
physicsConstantActions = [
    planckConstant,
    planckConstantReduced,
#    planckLength,
#    planckMass,
#    planckTemperature,
#    planckTime,
    boltzmann,
    elementaryCharge,
    massOfElectron,
    massOfProton,
    speedOfLight,
    gravitationalConstant,
    standardAccelerationOfGravity,
    freeSpacePermittivity,
    freeSpacePermeability,
]
chemistryConstantActions = [
    planckConstant,
    planckConstantReduced,
    boltzmann,
    elementaryCharge,
    massOfElectron,
    massOfProton,
    molarGasConstant,
    avogadroConstant,
]
constantActions = (
    commonConstantActions +
    engineeringConstantActions +
    physicsConstantActions +
    chemistryConstantActions
)

# Numbers {{{2
numberActions = [
    numbers,
    engineeringNumber,
    scientificNumber,
    hexadecimalNumber,
    octalNumber,
    binaryNumber,
    verilogHexadecimalNumber,
    verilogDecimalNumber,
    verilogOctalNumber,
    verilogBinaryNumber,
]
realNumberActions = [
    numbers,
    engineeringNumber,
    scientificNumber,
]

# Number Formats {{{2
numberFormatActions = [
    numberFormats,
    setEngineeringFormat,
    setScientificFormat,
    setFixedFormat,
    setHexadecimalFormat,
    setOctalFormat,
    setBinaryFormat,
    setVerilogHexadecimalFormat,
    setVerilogDecimalFormat,
    setVerilogOctalFormat,
    setVerilogBinaryFormat,
]
realNumberFormatActions = [
    numberFormats,
    setEngineeringFormat,
    setScientificFormat,
    setFixedFormat,
]

# Variables {{{2
variableActions = [
    variableCommands,
    storeToVariable,
    recallFromVariable,
    listVariables,
]

# Stack {{{2
stackActions = [
    stackCommands,
    swapXandY,
    duplicateX,
    popX,
    listStack,
    clearStack,
]

# Miscellaneous {{{2
miscellaneousActions = [
    miscellaneousCommands,
    randomNumber,
    printText,
    setUnits,
    printAbout,
    terminate,
    printHelp,
    detailedHelp,
]

# Action Lists {{{1
# All actions {{{2
allActions = (
    arithmeticOperatorActions +
    logPowerExponentialActions +
    trigFunctionActions +
    complexVectorFunctionActions +
    hyperbolicFunctionActions +
    decibelFunctionActions +
    constantActions +
    numberActions +
    numberFormatActions +
    variableActions +
    stackActions +
    miscellaneousActions
)

# Engineering actions {{{2
engineeringActions = (
    arithmeticOperatorActions +
    logPowerExponentialActions +
    trigFunctionActions +
    complexVectorFunctionActions +
    hyperbolicFunctionActions +
    decibelFunctionActions +
    commonConstantActions +
    engineeringConstantActions +
    numberActions +
    numberFormatActions +
    variableActions +
    stackActions +
    miscellaneousActions
)

# Physics actions {{{2
physicsActions = (
    arithmeticOperatorActions +
    logPowerExponentialActions +
    trigFunctionActions +
    complexVectorFunctionActions +
    hyperbolicFunctionActions +
    commonConstantActions +
    physicsConstantActions +
    realNumberActions +
    realNumberFormatActions +
    variableActions +
    stackActions +
    miscellaneousActions
)

# Chemistry actions {{{2
chemistryActions = (
    arithmeticOperatorActions +
    logPowerExponentialActions +
    trigFunctionActions +
    commonConstantActions +
    chemistryConstantActions +
    realNumberActions +
    realNumberFormatActions +
    variableActions +
    stackActions +
    miscellaneousActions
)

# Configure Calculator {{{1
# To modify the personality of the calculator, chose the set of actions to use
# and any predefined variables needed here. You can also adjust the list of
# actions by commenting out undesired ones in the lists above.
actionsToUse = allActions
if (
    voltageToDbm in actionsToUse or
    dbmToVoltage in actionsToUse or
    currentToDbm in actionsToUse or
    dbmToCurrent in actionsToUse
):
    predefinedVariables = {'Rref': (50, 'Ohms')}
else:
    predefinedVariables = {}

# The following variables are imported into the calculator and affect its
# default behavior.
defaultFormat = setEngineeringFormat
defaultDigits = 4

# The following variables control the generation of the documentation
# (the man page).
documentComplexNumbers = (
    imaginaryUnit in actionsToUse or
    imaginaryTwoPi in actionsToUse
)
documentVerilogIntegers = (
    verilogHexadecimalNumber in actionsToUse or
    verilogDecimalNumber in actionsToUse or
    verilogOctalNumber in actionsToUse or
    verilogBinaryNumber in actionsToUse or
    setVerilogHexadecimalFormat in actionsToUse or
    setVerilogDecimalFormat in actionsToUse or
    setVerilogOctalFormat in actionsToUse or
    setVerilogBinaryFormat in actionsToUse
)
documentIntegers = (
    documentVerilogIntegers in actionsToUse or
    hexadecimalNumber in actionsToUse or
    octalNumber in actionsToUse or
    binaryNumber in actionsToUse or
    setHexadecimalFormat in actionsToUse or
    setOctalFormat in actionsToUse or
    setBinaryFormat in actionsToUse
)
