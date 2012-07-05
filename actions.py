#!/usr/bin/env python
#
# Engineering Calculator Actions
#
# An RPN calculator that supports numbers with SI scale factors and units.

# Imports {{{1
from __future__ import division
import operator
import math
import cmath
import random
from calculator import (
    Command, Constant, UnaryOp, BinaryOp, BinaryIoOp, Number,
    SetFormat, Help, Store, Recall, SetUnits, Print, Dup, Category,
    Calculator
)
from engfmt import toNumber, toEngFmt

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
  , synopsis='x, y, ... => x+y, ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the
        stack and the sum is placed back on the stack into the #{x}
        register.
    """
)

# subtraction {{{3
subtraction = BinaryOp(
    '-'
  , operator.sub
  , description="%(key)s: subtraction"
  # keep units of x if they are the same as units of y
  , units=lambda calc, units: units[0] if units[0] == units[1] else ''
  , synopsis='x, ... => x-y, ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the
        stack and the difference is placed back on the stack into the #{x}
        register.
    """
)

# multiplication {{{3
multiplication = BinaryOp(
    '*'
  , operator.mul
  , description="%(key)s: multiplication"
  , synopsis='x, y, ... => x*y, ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the
        stack and the product is placed back on the stack into the #{x}
        register.
    """
)

# true division {{{3
trueDivision = BinaryOp(
    '/'
  , operator.truediv
  , description="%(key)s: true division"
  , synopsis='x, y, ... => y/x, ...'
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

# floor division {{{3
floorDivision = BinaryOp(
    '//'
  , operator.floordiv
  , description="%(key)s: floor division"
  , synopsis='x, y, ... => y//x, ...'
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

# modulus {{{3
modulus = BinaryOp(
    '%'
  , operator.mod
  , description="%(key)s: modulus"
  , synopsis='x, y, ... => y%x, ...'
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

# percent change {{{3
percentChange = BinaryOp(
    '%chg'
  , lambda y, x: 100*(x-y)/y
  , description="%(key)s: percent change"
  , synopsis='x, y, ... => 100*(x-y)/y, ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and 
        the percent difference between #{x} and #{y} relative to #{y} is pushed 
        back into the #{x} register.
    """
)

# parallel combination {{{3
parallel = BinaryOp(
    '||'
  , lambda y, x: (x/(x+y))*y
  , description="%(key)s: parallel combination"
  , synopsis='x, y, ... => 1/(1/x+1/y), ...'
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

# negation {{{3
negation = UnaryOp(
    'chs'
  , operator.neg
  , description="%(key)s: change sign"
  , synopsis='x, ... => -x, ...'
  , summary="""
        The value in the #{x} register is replaced with its negative. 
    """
)

# reciprocal {{{3
reciprocal = UnaryOp(
    'recip'
  , lambda x: 1/x
  , description="%(key)s: reciprocal"
  , synopsis='x, ... => 1/x, ...'
  , summary="""
        The value in the #{x} register is replaced with its reciprocal. 
    """
)

# ceiling {{{3
ceiling = UnaryOp(
    'ceil'
  , math.ceil
  , description="%(key)s: round towards positive infinity"
  , synopsis='x, ... => ceil(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its value rounded
        towards infinity (replaced with the smallest integer greater than its
        value).
    """
)

# floor {{{3
floor = UnaryOp(
    'floor'
  , math.floor
  , description="%(key)s: round towards negative infinity"
  , synopsis='x, ... => floor(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its value rounded
        towards negative infinity (replaced with the largest integer smaller
        than its value).
    """
)

# factorial {{{3
factorial = UnaryOp(
    '!'
  , math.factorial
  , description="%(key)s: factorial"
  , synopsis='x, ... => x!, ...'
  , summary="""
        The value in the #{x} register is replaced with its factorial.
    """
)

# random number {{{3
randomNumber = Constant(
    'rand'
  , random.random
  , description="%(key)s: random number between 0 and 1"
  , synopsis='... => rand, ...'
  , summary="""
        A number between 0 and 1 is chosen at random and its value is pushed on
        the stack into #{x} register.
    """
)

# Logs, Powers, and Exponentials {{{2
powersAndLogs = Category("Powers, Roots, Exponentials and Logarithms")

# power {{{3
power = BinaryOp(
    '**'
  , operator.pow
  , description="%(key)s: raise y to the power of x"
  , synopsis='x, y, ... => y**x, ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the
        stack and replaced with the value of #{y} raised to the power of
        #{x}. 
    """
  , aliases=['pow', 'ytox']
)

# exponential {{{3
exponential = UnaryOp(
    'exp'
  , lambda x: cmath.exp(x) if type(x) == complex else math.exp(x)
  , description="%(key)s: natural exponential"
  , synopsis='x, ... => exp(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its exponential. 
        Supports a complex argument.
    """
  , aliases=['powe']
)

# natural logarithm {{{3
naturalLog = UnaryOp(
    'ln'
  , lambda x: cmath.log(x) if type(x) == complex else math.log(x)
  , description="%(key)s: natural logarithm"
  , synopsis='x, ... => ln(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its natural logarithm. 
        Supports a complex argument.
    """
  , aliases=['loge']
)

# raise 10 to the power of x {{{3
tenPower = UnaryOp(
    'pow10'
  , lambda x: 10**x
  , description="%(key)s: raise 10 to the power of x"
  , synopsis='x, ... => 10**x, ...'
  , summary="""
        The value in the #{x} register is replaced with 10 raised to #{x}.
    """
  , aliases=['10tox']
)

# common logarithm {{{3
commonLog = UnaryOp(
    'log'
  , math.log10
  , description="%(key)s: base 10 logarithm"
  , synopsis='x, ... => log(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its common logarithm. 
    """
  , aliases=['log10', 'lg']
)

# binary logarithm {{{3
binaryLog = UnaryOp(
    'log2'
  , lambda x: math.log(x)/math.log(2)
  , description="%(key)s: base 2 logarithm"
  , synopsis='x, ... => log2(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its common logarithm. 
    """
  , aliases=['lb']
)

# square {{{3
square = UnaryOp(
    'sqr'
  , lambda x: x*x
  , description="%(key)s: square"
  , synopsis='x, ... => x**2, ...'
  , summary="""
        The value in the #{x} register is replaced with its square. 
    """
)

# square root {{{3
squareRoot = UnaryOp(
    'sqrt'
  , lambda x: cmath.sqrt(x) if type(x) == complex else math.sqrt(x)
  , description="%(key)s: square root"
  , synopsis='x, ... => sqrt(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its square root.
    """
)

# cube root {{{3
from ctypes import util, cdll, c_double
libm = cdll.LoadLibrary(util.find_library('m'))
libm.cbrt.restype = c_double
libm.cbrt.argtypes = [c_double]
cubeRoot = UnaryOp(
    'cbrt'
  , lambda x: libm.cbrt(x)
  , description="%(key)s: cube root"
  , synopsis='x, ... => cbrt(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its cube root.
    """
)

# Trig Functions {{{2
trigFunctions = Category("Trigonometric Functions")

# sine {{{3
sine = UnaryOp(
    'sin'
  , lambda x, calc: math.sin(calc.toRadians(x))
  , description="%(key)s: trigonometric sine"
  , needCalc=True
  , synopsis='x, ... => sin(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its sine.
    """
)

# cosine {{{3
cosine = UnaryOp(
    'cos'
  , lambda x, calc: math.cos(calc.toRadians(x))
  , description="%(key)s: trigonometric cosine"
  , needCalc=True
  , synopsis='x, ... => cos(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its cosine.
    """
)

# tangent {{{3
tangent = UnaryOp(
    'tan'
  , lambda x, calc: math.tan(calc.toRadians(x))
  , description="%(key)s: trigonometric tangent"
  , needCalc=True
  , synopsis='x, ... => tan(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its tangent.
    """
)

# arc sine {{{3
arcSine = UnaryOp(
    'asin'
  , lambda x, calc: calc.fromRadians(math.asin(x))
  , description="%(key)s: trigonometric arc sine"
  , needCalc=True
  , units=lambda calc, units: calc.angleUnits()
  , synopsis='x, ... => asin(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its arc sine.
    """
)

# arc cosine {{{3
arcCosine = UnaryOp(
    'acos'
  , lambda x, calc: calc.fromRadians(math.acos(x))
  , description="%(key)s: trigonometric arc cosine"
  , needCalc=True
  , units=lambda calc, units: calc.angleUnits()
  , synopsis='x, ... => acos(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its arc cosine.
    """
)

# arc tangent {{{3
arcTangent = UnaryOp(
    'atan'
  , lambda x, calc: calc.fromRadians(math.atan(x))
  , description="%(key)s: trigonometric arc tangent"
  , needCalc=True
  , units=lambda calc, units: calc.angleUnits()
  , synopsis='x, ... => atan(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its arc tangent.
    """
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
  , synopsis='x, ... => abs(x), x, ...'
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
  , synopsis='x, ... => arg(x), x, ...'
  , summary="""
        The argument of the number in the #{x} register is pushed onto the
        stack if it is complex. If the value is real, zero is pushed
        onto the stack.
    """
  , aliases=['ph']
)
# hypotenuse {{{3
hypotenuse = BinaryOp(
    'hypot'
  , math.hypot
  , description="%(key)s: hypotenuse"
  , synopsis='x, y, ... => sqrt(x**2+y**2), ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and 
        replaced with the length of the vector from the origin to the point
        (#{x},#{y}).
    """
  , aliases=['len']
)

# arc tangent 2 {{{3
arcTangent2 = BinaryOp(
    'atan2'
  , lambda y, x, calc: calc.fromRadians(math.atan2(y, x))
  , description="%(key)s: two-argument arc tangent"
  , needCalc=True
  , units=lambda calc, units: calc.angleUnits()
  , synopsis='x, y, ... => atan2(y,x), ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and 
        replaced with the angle of the vector from the origin to the point.
    """
  , aliases=['angle']
)

# rectangular to polar {{{3
rectangularToPolar = BinaryIoOp(
    'rtop'
  , lambda y, x, calc: (math.hypot(y, x), calc.fromRadians(math.atan2(y,x)))
  , description="%(key)s: convert rectangular to polar coordinates"
  , needCalc=True
  , yUnits=lambda calc: calc.angleUnits()
  , synopsis='x, y, ... => sqrt(x**2+y**2), atan2(y,x), ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and 
        replaced with the length of the vector from the origin to the point 
        (#{x},#{y}) and with the angle of the vector from the origin to the point 
        (#{x},#{y}).
    """
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
  , xUnits=lambda calc: calc.stack.peek()[1]
  , yUnits=lambda calc: calc.stack.peek()[1]
  , synopsis='x, y, ... => x*cos(y), x*sin(y), ...'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and
        interpreted as the length and angle of a vector and are replaced with
        the coordinates of the end-point of that vector.
    """
)

# Hyperbolic Functions {{{2
hyperbolicFunctions = Category("Hyperbolic Functions")

# hyperbolic sine {{{3
hyperbolicSine = UnaryOp(
    'sinh'
  , math.sinh
  , description="%(key)s: hyperbolic sine"
  , synopsis='x, ... => sinh(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic sine.
    """
)

# hyperbolic cosine {{{3
hyperbolicCosine = UnaryOp(
    'cosh'
  , math.cosh
  , description="%(key)s: hyperbolic cosine"
  , synopsis='x, ... => cosh(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic cosine.
    """
)

# hyperbolic tangent {{{3
hyperbolicTangent = UnaryOp(
    'tanh'
  , math.tanh
  , description="%(key)s: hyperbolic tangent"
  , synopsis='x, ... => tanh(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic tangent.
    """
)

# hyperbolic arc sine {{{3
hyperbolicArcSine = UnaryOp(
    'asinh'
  , math.asinh
  , description="%(key)s: hyperbolic arc sine"
  , synopsis='x, ... => asinh(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic arc sine.
    """
)

# hyperbolic arc cosine {{{3
hyperbolicArcCosine = UnaryOp(
    'acosh'
  , math.acosh
  , description="%(key)s: hyperbolic arc cosine"
  , synopsis='x, ... => acosh(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic arc
        cosine.
    """
)

# hyperbolic arc tangent {{{3
hyperbolicArcTangent = UnaryOp(
    'atanh'
  , math.atanh
  , description="%(key)s: hyperbolic arc tangent"
  , synopsis='x, ... => atanh(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic arc
        tangent.
    """
)

# Decibel Functions {{{2
decibelFunctions = Category("Decibel Functions")

# voltage or current to decibels {{{3
decibels20 = UnaryOp(
    'db'
  , lambda x: 20*math.log10(x)
  , description="%(key)s: convert voltage or current to dB"
  , synopsis='x, ... => 20*log(x), ...'
  , summary="""
        The value in the #{x} register is replaced with its value in 
        decibels. It is appropriate to apply this form when 
        converting voltage or current to decibels.
    """
  , aliases=['db20', 'v2db', 'i2db']
)

# decibels to voltage or current {{{3
antiDecibels20 = UnaryOp(
    'adb'
  , lambda x: 10**(x/20)
  , description="%(key)s: convert dB to voltage or current"
  , synopsis='x, ... => 10**(x/20), ...'
  , summary="""
        The value in the #{x} register is converted from decibels and that value
        is placed back into the #{x} register.  It is appropriate to apply this
        form when converting decibels to voltage or current.  
    """
  , aliases=['db2v', 'db2i']
)
# power to decibels {{{3
decibels10 = UnaryOp(
    'db10'
  , lambda x: 10*math.log10(x)
  , description="%(key)s: convert power to dB"
  , synopsis='x, ... => 10*log(x), ...'
  , summary="""
        The value in the #{x} register is converted from decibels and that
        value is placed back into the #{x} register.  It is appropriate to
        apply this form when converting power to decibels.
    """
  , aliases=['p2db']
)

# decibels to power {{{3
antiDecibels10 = UnaryOp(
    'adb10'
  , lambda x: 10**(x/10)
  , description="%(key)s: convert dB to power"
  , synopsis='x, ... => 10**(x/10), ...'
  , summary="""
        The value in the #{x} register is converted from decibels and that value
        is placed back into the #{x} register.  It is appropriate to apply this
        form when converting decibels to voltage or current.  
    """
  , aliases=['db2p']
)

# voltage to dBm {{{3
voltageToDbm = UnaryOp(
    'vdbm'
  , lambda x, calc: 30+10*math.log10(x*x/calc.heap['Rref'][0]/2)
  , description="%(key)s: convert peak voltage to dBm"
  , needCalc=True
  , synopsis='x, ... => 30+10*log10((x**2)/(2*#{Rref})), ...'
  , summary="""
        The value in the #{x} register is expected to be the peak voltage of a
        sinusoid that is driving a load resistor equal to #{Rref} (a predefined
        variable).  It is replaced with the power delivered to the resistor in
        decibels relative to 1 milliwatt.  
    """
  , aliases=['v2dbm']
)

# dBm to voltage {{{3
dbmToVoltage = UnaryOp(
    'dbmv'
  , lambda x, calc: math.sqrt(2*pow(10,(x - 30)/10)*calc.heap['Rref'][0])
  , description="%(key)s: dBm to peak voltage"
  , needCalc=True
  , units='V'
  , synopsis='x, ... => sqrt(2*10**(x - 30)/10)*#{Rref}), ...'
  , summary="""
        The value in the #{x} register is expected to be a power in decibels
        relative to one milliwatt. It is replaced with the peak voltage of a
        sinusoid that would be needed to deliver the same power to a load
        resistor equal to #{Rref} (a predefined variable).
    """
  , aliases=['dbm2v']
)

# current to dBm {{{3
currentToDbm = UnaryOp(
    'idbm'
  , lambda x, calc: 30+10*math.log10(x*x*calc.heap['Rref'][0]/2)
  , description="%(key)s: peak current to dBm"
  , needCalc=True
  , synopsis='x, ... => 30+10*log10(((x**2)*#{Rref}/2), ...'
  , summary="""
        The value in the #{x} register is expected to be the peak current of a
        sinusoid that is driving a load resistor equal to #{Rref} (a predefined
        variable).  It is replaced with the power delivered to the resistor in
        decibels relative to 1 milliwatt.
    """
  , aliases=['i2dbm']
)

# dBm to current {{{3
dbmToCurrent = UnaryOp(
    'dbmi'
  , lambda x, calc: math.sqrt(2*pow(10,(x - 30)/10)/calc.heap['Rref'][0])
  , description="%(key)s: dBm to peak current"
  , needCalc=True
  , units='A'
  , synopsis='x, ... => sqrt(2*10**(x - 30)/10)/#{Rref}), ...'
  , summary="""
        The value in the #{x} register is expected to be a power in decibels
        relative to one milliwatt. It is replaced with the peak current of a
        sinusoid that would be needed to deliver the same power to a load
        resistor equal to #{Rref} (a predefined variable).
    """
  , aliases=['dbm2i']
)

# Constants {{{2
constants = Category("Constants")

# pi {{{3
pi = Constant(
    'pi'
  , lambda: math.pi
  , description="%(key)s: the ratio of a circle's circumference to its diameter"
  , units='rads'
  , synopsis='... => pi, ...'
  , summary="""
        The value of pi (3.141592...) is pushed on the stack into the #{x}
        register.
    """
)

# 2 pi {{{3
twoPi = Constant(
    '2pi'
  , lambda: 2*math.pi
  , description="%(key)s: the ratio of a circle's circumference to its radius"
  , units='rads'
  , synopsis='... => 2*pi, ...'
  , summary="""
        Two times the value of pi (6.283185...) is pushed on the stack into the
        #{x} register.
    """
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

# j {{{3
imaginaryUnit = Constant(
    'j'
  , lambda: 1j
  , description="%(key)s: imaginary unit (square root of -1)"
  , synopsis='... => j, ...'
  , summary="""
        The imaginary unit (square root of -1) is pushed on the stack into
        the #{x} register.
    """
)

# j2pi {{{3
imaginaryTwoPi = Constant(
    'j2pi'
  , lambda: 2j*math.pi
  , description="%(key)s: j*2*pi"
  , units='rads'
  , synopsis='... => j*2*pi, ...'
  , summary="""
        2 pi times the imaginary unit (j6.283185...) is pushed on the stack into
        the #{x} register.
    """
)

# plank constant {{{3
planckConstant = Constant(
    'h'
  , lambda: 6.62606957e-34
  , description="%(key)s: Planck constant"
  , units='J-s'
  , synopsis='... => h, ...'
  , summary="""
        The Planck constant (6.62606957e-34 J-s) is pushed on the stack into
        the #{x} register.
    """
)

# reduced plank constant {{{3
planckConstantReduced = Constant(
    'hbar'
  , lambda: 1.054571726e-34
  , description="%(key)s: Reduced Planck constant"
  , units='J-s'
  , synopsis='... => h/(2*pi), ...'
  , summary="""
        The reduced Planck constant (1.054571726e-34 J-s) is pushed on the stack
        into the #{x} register.
    """
)

# planck length {{{3
planckLength = Constant(
    'lP'
  , lambda: 1.616199e-35
  , description="%(key)s: Planck length"
  , units='m'
  , synopsis='... => lP, ...'
  , summary="""
        The Planck length (sqrt(h*G/(2*pi*c**3)) or 1.616199e-35 m) is pushed on
        the stack into the #{x} register.
    """
)

# planck mass {{{3
planckMass = Constant(
    'mP'
  , lambda: 2.17651e-5
  , description="%(key)s: Planck mass"
  , units='g'
  , synopsis='... => mP, ...'
  , summary="""
        The Planck mass (sqrt(h*c/(2*pi*G)) or 2.17651e-5 g) is pushed on
        the stack into the #{x} register.
    """
)

# reduced planck mass {{{3
planckMassReduced = Constant(
    'mPr'
  , lambda: 2.17651e-5
  , description="%(key)s: Reduced Planck mass"
  , units='g'
  , synopsis='... => mPr, ...'
  , summary="""
        The reduced Planck mass (sqrt(h*c/(16*pi**2*G)) or 4.341e-6 g) is pushed
        on the stack into the #{x} register.
    """
)

# planck temperature {{{3
planckTemperature = Constant(
    'TP'
  , lambda: 1.416833e32
  , description="%(key)s: Planck temperature"
  , units='K'
  , synopsis='... => TP, ...'
  , summary="""
        The Planck temperature (mP*c**2/k or 1.416833e32 K) is pushed
        on the stack into the #{x} register.
    """
)

# planck time {{{3
planckTime = Constant(
    'tP'
  , lambda: 5.39106e-44
  , description="%(key)s: Planck time"
  , units='s'
  , synopsis='... => tP, ...'
  , summary="""
        The Planck time (sqrt(h*G/(2*pi*c**5)) or 5.39106e-44 s) is pushed on
        the stack into the #{x} register.
    """
)

# boltzmann constant {{{3
boltzmann = Constant(
    'k'
  , lambda: 1.3806488e-23
  , description="%(key)s: Boltzmann constant"
  , units='J/K'
  , synopsis='... => k, ...'
  , summary="""
        The Boltzmann constant (R/NA) or 1.3806488e-23 J/K) is pushed on the
        stack into the #{x} register.
    """
)

# elementary charge {{{3
elementaryCharge = Constant(
    'q'
  , lambda: 1.602176565e-19
  , description="%(key)s: elementary charge (the charge of an electron)"
  , units='C'
  , synopsis='... => q, ...'
  , summary="""
        The elementary charge (the charge of an electron or 1.602176565e-19 C)
        is pushed on the stack into the #{x} register.
    """
)

# mass of electron {{{3
massOfElectron = Constant(
    'me'
  , lambda: 9.10938291e-28
  , description="%(key)s: mass of an electron"
  , units='g'
  , synopsis='... => me, ...'
  , summary="""
        The mass of an electron (9.10938291e-28 g) is pushed on the stack into
        the #{x} register.
    """
)

# mass of proton {{{3
massOfProton = Constant(
    'mp'
  , lambda: 1.672621777e-24
  , description="%(key)s: mass of a proton"
  , units='g'
  , synopsis='... => mp, ...'
  , summary="""
        The mass of a proton (1.672621777e-24 g) is pushed on the stack into
        the #{x} register.
    """
)

# speed of light {{{3
speedOfLight = Constant(
    'c'
  , lambda: 2.99792458e8
  , description="%(key)s: speed of light in a vacuum"
  , units='m/s'
  , synopsis='... => c, ...'
  , summary="""
        The speed of light in a vacuum (2.99792458e8 m/s) is pushed on the stack
        into the #{x} register.
    """
)

# gravitational constant {{{3
gravitationalConstant = Constant(
    'G'
  , lambda: 6.6746e-11
  , description="%(key)s: universal gravitational constant"
  , units="m^3/(kg-s^2)"
  , synopsis='... => G, ...'
  , summary="""
        The universal gravitational constant (6.6746e-11 m^3/(kg-s^2)) is pushed
        on the stack into the #{x} register.
    """
)

# acceleration of gravity {{{3
standardAccelerationOfGravity = Constant(
    'g'
  , lambda: 9.80665
  , description="%(key)s: standard acceleration of gravity"
  , units='m/s^2'
  , synopsis='... => g, ...'
  , summary="""
        The standard acceleration of gravity on earth (9.80665 m/s^2)) is pushed
        on the stack into the #{x} register.
    """
)

# avogadro constant {{{3
avogadroConstant = Constant(
    'NA'
  , lambda: 6.02214129e23
  , description="%(key)s: Avagadro Number"
  , units='/mol'
  , synopsis='... => NA, ...'
  , summary="""
        Avogadro constant (6.02214129e23) is pushed on the stack into the #{x}
        register.
    """
)

# gas constant {{{3
molarGasConstant = Constant(
    'R'
  , lambda: 8.3144621
  , description="%(key)s: molar gas constant"
  , units='J/(mol-K)'
  , synopsis='... => R, ...'
  , summary="""
        The molar gas constant (8.3144621 J/(mol-K)) is pushed on the stack into
        the #{x} register.
    """
)

# zero celsius {{{3
zeroCelsius = Constant(
    '0C'
  , lambda: 273.15
  , description="%(key)s: 0 Celsius in Kelvin"
  , units='K'
  , synopsis='... => 0C, ...'
  , summary="""
        Zero celsius in kelvin (273.15 K) is pushed on the stack into
        the #{x} register.
    """
)

# free space permittivity {{{3
freeSpacePermittivity = Constant(
    'eps0'
  , lambda: 8.854187817e-12
  , description="%(key)s: permittivity of free space"
  , units='F/m'
  , synopsis='... => eps0, ...'
  , summary="""
        The permittivity of free space (8.854187817e-12 F/m) is pushed on the
        stack into the #{x} register.
    """
)

# free space permeability {{{3
freeSpacePermeability = Constant(
    'mu0'
  , lambda: 4e-7*math.pi
  , description="%(key)s: permeability of free space"
  , units='N/A^2'
  , synopsis='... => mu0, ...'
  , summary="""
        The permeability of free space (4e-7*pi N/A^2) is pushed on the
        stack into the #{x} register.
    """
)

# free space characteristic impedance {{{3
freeSpaceCharacteristicImpedance = Constant(
    'Z0'
  , lambda: 376.730313461
  , description="%(key)s: Characteristic impedance of free space"
  , units='Ohms'
  , synopsis='... => Z0, ...'
  , summary="""
        The characteristic impedance of free space (376.730313461 Ohms) is
        pushed on the stack into the #{x} register.
    """
)

# Numbers {{{2
numbers = Category("Numbers")

# real number in engineering notation {{{3
engineeringNumber = Number(
    pattern=r'\A(\$?([-+]?[0-9]*\.?[0-9]+)(([YZEPTGMKk_munpfazy])([a-zA-Z_]*))?)\Z'
  , action=lambda matches: toNumber(matches[0])
  , name='engnum'
  , description="<#{N}[.#{M}][#{S}[#{U}]]>: a real number"
  , synopsis='... => num, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is the
        integer portion of the mantissa and #{M} is an optional fractional part.
        #{S} is a letter that represents an SI scale factor. #{U} the optional
        units (must not contain special characters).  For example, 10MHz
        represents 1e7 Hz.
    """
)

# real number in scientific notation {{{3
scientificNumber = Number(
    pattern=r'\A(\$?[-+]?[0-9]*\.?[0-9]+[eE][-+]?[0-9]+)([a-zA-Z_]*)\Z'
  , action=lambda matches: (float(matches[0]), matches[1])
  , name='scinum'
  , description="<#{N}[.#{M}]>e<#{E}[#{U}]>: a real number in scientific notation"
  , synopsis='... => num, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is the
        integer portion of the mantissa and #{M} is an optional fractional part.
        #{E} is an integer exponent. #{U} the optional units (must not contain
        special characters).  For example, 2.2e-8F represents 22nF.
    """
)

# hexadecimal number {{{3
hexadecimalNumber = Number(
    pattern=r"\A([-+]?)0[xX]([0-9a-fA-F]+)\Z"
  , action=lambda matches: (int(matches[0]+matches[1], base=16), '')
  , name='hexnum'
  , description="0x<#{N}>: a hexadecimal number"
  , synopsis='... => num, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 16 (use a-f to represent digits greater than 9).  For
        example, 0xFF represents the hexadecimal number FF or the decimal number
        255.
    """
)

# octal number {{{3
# oct must be before eng if we use the 0NNN form (as opposed to OoNNN form)
octalNumber = Number(
    pattern=r"\A([-+]?)0[oO]([0-7]+)\Z"
  , action=lambda matches: (int(matches[0]+matches[1], base=8), '')
  , name='octnum'
  , description="0o<#{N}>: a number in octal"
  , synopsis='... => num, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 8 (it must not contain the digits 8 or 9).  For example,
        0o77 represents the octal number 77 or the decimal number 63.
    """
)

# binary number {{{3
binaryNumber = Number(
    pattern=r"\A([-+]?)0[bB]([01]+)\Z"
  , action=lambda matches: (int(matches[0]+matches[1], base=2), '')
  , name='binnum'
  , description="0b<#{N}>: a number in octal"
  , synopsis='... => num, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 2 (it may contain only the digits 0 or 1).  For example,
        0b1111 represents the octal number 1111 or the decimal number 15.
    """
)

# hexadecimal number in verilog notation {{{3
# Verilog constants are incompatible with generalized units because the
# single quote in the Verilog constant conflicts with the single quotes that
# surround generalized units (ex: 6.28e6 'rads/s').
# Is okay now, I switched the quote characters to free up single quotes.
verilogHexadecimalNumber = Number(
    pattern=r"\A([-+]?)'[hH]([0-9a-fA-F_]*[0-9a-fA-F])\Z"
  , action=lambda matches: (int(matches[0]+matches[1], base=16), '')
  , name='vhexnum'
  , description="'h<#{N}>: a number in Verilog hexadecimal notation"
  , synopsis='... => num, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 16 (use a-f to represent digits greater than 9).  For
        example, 'hFF represents the hexadecimal number FF or the decimal number
        255.
    """
)

# decimal number in verilog notation {{{3
verilogDecimalNumber = Number(
    pattern=r"\A([-+]?)'[dD]([0-9_]*[0-9]+)\Z"
  , action=lambda matches: (int(matches[0]+matches[1], base=10), '')
  , name='vdecnum'
  , description="'d<#{N}>: a number in Verilog decimal"
  , synopsis='... => num, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 10.  For example, 'd99 represents the decimal number 99.
    """
)

# octal number in verilog notation {{{3
verilogOctalNumber = Number(
    pattern=r"\A([-+]?)'[oO]([0-7_]*[0-7]+)\Z"
  , action=lambda matches: (int(matches[0]+matches[1], base=8), '')
  , name='voctnum'
  , description="'o<#{N}>: a number in Verilog octal"
  , synopsis='... => num, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 8 (it must not contain the digits 8 or 9).  For example,
        'o77 represents the octal number 77 or the decimal number 63.
    """
)

# binary number in verilog notation {{{3
verilogBinaryNumber = Number(
    pattern=r"\A([-+]?)'[bB]([01_]*[01]+)\Z"
  , action=lambda matches: (int(matches[0]+matches[1], base=2), '')
  , name='vbinnum'
  , description="'b<#{N}>: a number in Verilog binary"
  , synopsis='... => num, ...'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 2 (it may contain only the digits 0 or 1).  For example,
        'b1111 represents the binary number 1111 or the decimal number 15.
    """
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

# engineering format {{{3
setEngineeringFormat = SetFormat(
    pattern=r'\Aeng(\d{1,2})?\Z'
  , action=lambda num, units, digits: toEngFmt(num, units, prec=digits)
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

# Variables {{{2
variableCommands = Category("Variable Commands")

# store to variable {{{3
storeToVariable = Store(
    'store'
  , description='=<#{name}>: store value into a variable'
  , synopsis='x, ... => x, ...'
  , summary="""
        Store the value in the #{x} register into a variable with the given
        name.
    """
)

# recall from variable {{{3
recallFromVariable = Recall(
    'recall'
  , description='<#{name}>: recall value of a variable'
  , synopsis='... => name, ...'
  , summary="""
        Place the value of the variable with the given name into the #{x}
        register.
    """
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

# Stack {{{2
stackCommands = Category("Stack Commands")

# swap {{{3
swapXandY = Command(
    'swap'
  , Calculator.swap
  , description='%(key)s: swap x and y'
  , synopsis='x, y, ... => y, x, ...'
  , summary="""
        The values in the #{x} and #{y} registers are swapped.
    """
)

# dup {{{3
duplicateX = Dup(
    'dup'
  , None
  , description="%(key)s: duplicate #{x}"
  , synopsis='x, ... => x, x, ...'
  , summary="""
        The value in the #{x} register is pushed onto the stack again.
    """
  , aliases=['enter']
)

# pop {{{3
popX = Command(
    'pop'
  , Calculator.pop
  , description='%(key)s: discard x'
  , synopsis='x, ... => ...'
  , summary="""
        The value in the #{x} register is pulled from the stack and discarded.
    """
  , aliases=['clrx']
)

# stack {{{3
listStack = Command(
    'stack'
  , lambda calc: stack.display()
  , description="%(key)s: print stack"
  , summary="""
        Print all the values stored on the stack.
    """
)

clearStack = Command(
    'clstack'
  , lambda calc: calc.stack.clear()
  , description="%(key)s: clear stack"
  , synopsis='... =>'
  , summary="""
        Remove all values from the stack.
    """
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

setUnits = SetUnits(
    name='units'
  , description='"<units>": set the units of the x register'
  , synopsis='x, ... => x "units", ...'
  , summary="""\
        The units given are applied to the value in the #{x} register.
        The actual value is unchanged.
    """
)

printAbout = Command(
    'about'
  , Calculator.aboutMsg
  , description="%(key)s: print information about this calculator"
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

detailedHelp = Help(
    name='?'
  , description="%(name)s[<topic>]: detailed help on a particular topic"
  , summary="""\
        A topic, in the form of a symbol or name, may follow the question mark,
        in which case a detailed description will be printed for that topic.
        If no topic is given, a list of available topics is listed.
    """
)

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
    planckLength,
    planckMass,
    planckMassReduced,
    planckTemperature,
    planckTime,
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
    decibelFunctionActions +
    commonConstantActions +
    physicsConstantActions +
    numberActions +
    numberFormatActions +
    variableActions +
    stackActions +
    miscellaneousActions
)

# Chemistry actions {{{2
chemistryActions = (
    arithmeticOperatorActions +
    logPowerExponentialActions +
    trigFunctionActions +
    complexVectorFunctionActions +
    hyperbolicFunctionActions +
    decibelFunctionActions +
    commonConstantActions +
    chemistryConstantActions +
    numberActions +
    numberFormatActions +
    variableActions +
    stackActions +
    miscellaneousActions
)

# Choose action list {{{2
# To modify the personality of the calculator, chose the set of actions to use
# and any predefined variables needed here. You can also adjust the list of
# actions by commenting out undesired ones in the lists above.
actionsToUse = engineeringActions
predefinedVariables = {'Rref': (50, 'Ohms')}
defaultFormat = setEngineeringFormat
defaultDigits = 4
documentComplexNumbers = (
    imaginaryUnit in actionsToUse or
    imaginaryTwoPi in actionsToUse
)
documentVerilogIntegers = (
    verilogHexadecimalNumber or
    verilogDecimalNumber or
    verilogOctalNumber or
    verilogBinaryNumber or
    setVerilogHexadecimalFormat or
    setVerilogDecimalFormat or
    setVerilogOctalFormat or
    setVerilogBinaryFormat
)
documentIntegers = (
    documentVerilogIntegers or
    hexadecimalNumber or
    octalNumber or
    binaryNumber or
    setHexadecimalFormat or
    setOctalFormat or
    setBinaryFormat
)
