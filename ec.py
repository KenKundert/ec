#!/usr/bin/env python
#
# Engineering Calculator
#
# An RPN calculator that supports numbers with SI scale factors and units.

from __future__ import division
import operator
import math
import cmath
import random
import engfmt
import re
from os.path import expanduser
from copy import copy
from pydoc import pager
engfmt.setSpacer(' ')

# Utility classes {{{1
# CalculatorError {{{2
class CalculatorError(Exception):
    def __init__(self, message):
        self.message = message

# Stack {{{2
class Stack:
    def __init__(self, parent, stack = None):
        self.parent = parent
        if stack == None:
            stack = []
        self.stack = stack

    def push(self, item):
        self.stack.insert(0, item)

    def pop(self):
        try:
            return self.stack.pop(0)
        except IndexError:
            return (0, '')

    def peek(self, reg = 0):
        try:
            return self.stack[reg]
        except IndexError:
            return (0, '')

    def clear(self):
        self.stack = []

    def clone(self):
        return Stack(copy(self.stack))

    def __str__(self):
        return str(self.stack)

    def display(self):
        length = len(self.stack)
        labels = ['x:', 'y:'] + (length-2)*['  ']
        for label, value in zip(labels, self.stack):
            self.parent.printMessage(
                '  %s %s' % (label, self.parent.format(value))
            )

# Heap {{{2
class Heap:
    def __init__(
        self
      , parent = None
      , initialState = None
      , reserved = None
      , removeAction = None
    ):
        self.parent = parent
        self.initialState = initialState if initialState != None else {}
        self.reserved = reserved
        self.heap = copy(self.initialState)
        self.removeAction = removeAction

    def clear(self):
        self.heap = copy(self.initialState)

    def __str__(self):
        return str(self.heap)

    def display(self):
        for key in sorted(self.heap.keys()):
            self.parent.printMessage(
                '  %s: %s' % (key, calc.format(self.heap[key]))
            )

    def __getitem__(self, key):
        return self.heap[key]

    def __setitem__(self, key, value):
        if key in self.reserved:
            if self.removeAction:
                self.parent.printWarning(
                    "%s: variable overrides built-in." % key
                )
                del self.reserved[self.reserved.index(key)]
                self.removeAction(key)
            else:
                raise KeyError
        self.heap[key] = value

    def __contains__(self, key):
        return key in self.heap

# Display {{{2
class Display:
    def __init__(self, style = 'eng', digits = 4):
        self.defaultStyle = style
        self.defaultDigits = digits
        self.style = style
        self.digits = digits

    def setStyle(self, style):
        self.style = style

    def setDigits(self, digits):
        self.digits = digits

    def format(self, val):
        num, units = val
        if type(num) == complex:
            real = self.format((num.real, units))
            imag = self.format((num.imag, units))
            if imag[0] in ['0', '-0']:
                return real
            elif imag[0] == '-':
                return "%s - j%s" % (real, imag[1:])
            else:
                return "%s + j%s" % (real, imag)
        if self.style == 'eng':
            return engfmt.toEngFmt(num, units, prec=self.digits)
        if self.style == 'fix':
            return '%.*f' % (self.digits, num)
        elif self.style == 'sci':
            return '%.*e' % (self.digits, num)
        elif self.style == 'hex':
            return "%#.*x" % (self.digits, int(num))
        elif self.style == 'oct':
            return "%#.*o" % (self.digits, int(num))
        elif self.style == 'vhex':
            return "'h%.*x" % (self.digits, int(num))
        elif self.style == 'vdec':
            return "'d%.*d" % (self.digits, int(num))
        elif self.style == 'voct':
            return "'o%.*o" % (self.digits, int(num))
        else:
            raise AssertionError

    def clear(self):
        self.style = self.defaultStyle
        self.digits = self.defaultDigits

# Helper functions {{{2
def displayHelp(stack, calc):
    lines = []
    for each in calc.actions:
        if each.description:
            lines += ['    ' + each.description % each.__dict__]
    pager('\n'.join(lines) + '\n')

def useRadians(stack, calc):
    calc.setTrigMode('rads')

def useDegees(stack, calc):
    calc.setTrigMode('degs')

def quit(stack, calc):
    exit()

# Action classes {{{1
# Command (pop 0, push 0, match name) {{{2
class Command:
    """
    Operation that does not affect the stack.
    """
    def __init__(self, key, action, description = None):
        self.key = key
        self.action = action
        self.description = description

    def execute(self, stack, calc):
        self.action(stack, calc)

# Constant (pop 0, push 1, match name) {{{2
class Constant:
    """
    Operation that pushes one value onto the stack without removing any values.
    """
    def __init__(self, key, action, description = None, units = ''):
        self.key = key
        self.action = action
        self.description = description
        self.units = units

    def execute(self, stack, calc):
        result = self.action()
        stack.push((result, self.units))

# UnaryOp (pop 1, push 1, match name) {{{2
class UnaryOp:
    """
    Operation that removes one value from the stack, replacing it with another.
    """
    def __init__(self, key, action, description = None, needCalc=False, units=''):
        self.key = key
        self.action = action
        self.description = description
        self.needCalc = needCalc
        self.units = units

    def execute(self, stack, calc):
        x, xUnits = stack.pop()
        if self.needCalc:
            x = self.action(x, calc)
        else:
            x = self.action(x)
        if callable(self.units):
            units = self.units(calc, [xUnits])
        else:
            units = self.units
        stack.push((x, units))

# BinaryOp (pop 2, push 1, match name) {{{2
class BinaryOp:
    """
    Operation that removes two values from the stack and returns one value.
    """
    def __init__(self, key, action, description = None, needCalc=False, units=''):
        self.key = key
        self.action = action
        self.description = description
        self.needCalc = needCalc
        self.units = units

    def execute(self, stack, calc):
        x, xUnits = stack.pop()
        y, yUnits = stack.pop()
        if self.needCalc:
            result = self.action(y, x, calc)
        else:
            result = self.action(y, x)
        if callable(self.units):
            units = self.units(calc, [xUnits, yUnits])
        else:
            units = self.units
        stack.push((result, units))

# BinaryIoOp (pop 2, push 2, match name) {{{2
class BinaryIoOp:
    """
    Operation that removes two values from the stack and returns two values.
    """
    def __init__(self, key, action, description=None, needCalc=False, xUnits='', yUnits=''):
        self.key = key
        self.action = action
        self.description = description
        self.needCalc = needCalc
        self.xUnits = xUnits
        self.yUnits = yUnits

    def execute(self, stack, calc):
        x, xUnits = stack.pop()
        y, yUnits = stack.pop()
        if self.needCalc:
            result = self.action(y, x, calc)
        else:
            result = self.action(y, x)
        if callable(self.xUnits):
            xUnits = self.xUnits(calc)
        else:
            xUnits = self.xUnits
        if callable(self.yUnits):
            yUnits = self.yUnits(calc)
        else:
            yUnits = self.yUnits
        stack.push((result[1], yUnits))
        stack.push((result[0], xUnits))

# Number (pop 0, push 1, match regex) {{{2
class Number:
    def __init__(self, kind, description = None):
        self.kind = kind
        self.description = description
        if kind == 'hex':
            pattern = r"0[xX]([0-9a-fA-F]+)"
            self.base = 16
        elif kind == 'oct':
            pattern = r"0([0-7]+)"
            self.base = 8
        elif kind == 'vhex':
            pattern = r"'[hH]([0-9a-fA-F_]*[0-9a-fA-F])"
            self.base = 16
        elif kind == 'vdec':
            pattern = r"'[dD]([0-9_]*[0-9])"
            self.base = 10
        elif kind == 'voct':
            pattern = r"'[oO]([0-7_]*[0-7])"
            self.base = 8
        elif kind == 'vbin':
            pattern = r"'[bB]([01_]*[01])"
            self.base = 2
        elif kind == 'eng':
            pattern = r'\A(\$?([-+]?[0-9]*\.?[0-9]+)(([YZEPTGMKk_munpfazy])([a-zA-Z_]*))?)\Z'
        elif kind == 'sci':
            pattern = r'\A(\$?[-+]?[0-9]*\.?[0-9]+[eE][-+]?[0-9]+)([a-zA-Z_]*)\Z'
        self.regex = re.compile(pattern)

    def execute(self, matchGroups, stack, calc):
        units = ''
        if self.kind == 'sci':
            num, units = float(matchGroups[0]), matchGroups[1]
        elif self.kind == 'eng':
            numWithUnits = engfmt.toNumber(matchGroups[0])
            num, units = numWithUnits
            num = float(num)
        else:
            num = matchGroups[0]
            num = int(num, self.base)
        stack.push((num, units))

# SetFormat (pop 0, push 0, match regex) {{{2
class SetFormat:
    def __init__(self, kind, description = None):
        self.kind = kind
        self.description = description
        self.regex = re.compile('(%s)(\d{1,2})?' % kind)

    def execute(self, matchGroups, stack, calc):
        num = matchGroups[0]
        calc.formatter.setStyle(matchGroups[0])
        if matchGroups[1] != None:
            calc.formatter.setDigits(int(matchGroups[1]))

# Store (peek 1, push 0, match regex) {{{2
class Store:
    def __init__(self, description = None):
        self.description = description
        self.regex = re.compile(r'=([a-z]\w*)', re.I)

    def execute(self, matchGroups, stack, calc):
        name = matchGroups[0]
        try:
            calc.heap[name] = stack.peek()
        except KeyError:
            raise CalculatorError("%s: reserved, cannot be used as variable name." % name)

# Recall (pop 0, push 1, match regex) {{{2
class Recall:
    def __init__(self, description = None):
        self.description = description
        self.regex = re.compile(r'([a-z]\w*)', re.I)

    def execute(self, matchGroups, stack, calc):
        name = matchGroups[0]
        if name in calc.heap:
            stack.push(calc.heap[name])
        else:
            raise CalculatorError("%s: variable does not exist" % name)

# SetUnits (pop 1, push 1, match regex) {{{2
class SetUnits:
    def __init__(self, description = None):
        self.description = description
        self.regex = re.compile(r"'(.*)'")

    def execute(self, matchGroups, stack, calc):
        units, = matchGroups
        x, xUnits = stack.pop()
        stack.push((x, units))

# Print (pop 0, push 0, match regex) {{{2
class Print:
    def __init__(self, description = None):
        self.description = description
        self.regex = re.compile(r'"(.*)"')
        self.argsRegex = re.compile(r'\${?(\w+|\$)}?')

    def execute(self, matchGroups, stack, calc):
        # Prints a message after expanding any $codes it contains
        # $N or ${N} are replaced by the contents of a stack register (0=x, ...)
        # $name or ${name} are replaced by the contents of a variable
        # $$ is replaced by $
        text, = matchGroups
        if not text:
            message = calc.format(stack.stack[0])
        else:
            # process newlines and tabs
            text = text.replace(r'\n', '\n')
            text = text.replace(r'\t', '\t')
            components = self.argsRegex.split(text)
            textFrags = components[0::2]
            args = components[1::2]
            formattedArgs = []
            for arg in args:
                if arg[0] == '{' and arg[-1] == '}':
                    arg = arg[1:-1]
                try:
                    try:
                        arg = stack.stack[int(arg)]
                    except ValueError:
                        arg = calc.heap[arg]
                    arg = calc.format(arg)
                except (KeyError, IndexError):
                    if arg != '$':
                        if calc.warningPrinter:
                            calc.warningPrinter("$%s: unknown." % arg)
                        arg = '$?%s?' % arg
                formattedArgs += [arg]
            components[1::2] = formattedArgs
            message = ''.join(components)
        calc.printMessage(message)

# Swap (pop 2, push 2, match name) {{{2
class Swap:
    """
    Swap the top two entries on the stack.
    """
    def __init__(self, description = None):
        self.key = 'swap'
        self.description = description

    def execute(self, stack, calc):
        x, xUnits = stack.pop()
        y, yUnits = stack.pop()
        stack.push((x, yUnits))
        stack.push((y, yUnits))

# Dup (peek 1, push 1, match name) {{{2
class Dup:
    def __init__(self, key, action, description = None, needCalc=False, units=''):
        self.key = key
        self.action = action
        self.description = description
        self.needCalc = needCalc
        self.units = units

    def execute(self, stack, calc):
        x, xUnits = stack.peek()
        if self.action:
            if self.needCalc:
                x = self.action(x, calc)
            else:
                x = self.action(x)
            if self.units:
                if callable(self.units):
                    xUnits = self.units(calc, [xUnits])
                else:
                    xUnits = self.units
        stack.push((x, xUnits))

# Pop (pop 1, push 0, match name) {{{2
class Pop:
    """
    Pop the latest value off stack and discard it.
    """
    def __init__(self, description = None):
        self.key = 'pop'
        self.description = description

    def execute(self, stack, calc):
        stack.pop()

# Actions {{{1
Actions = [
    BinaryOp(
        '+'
      , operator.add
      , "%(key)s: addition"
      # keep units of x if they are the same as units of y
      , units=lambda calc, units: units[0] if units[0] == units[1] else ''
    )
  , BinaryOp(
        '-'
      , operator.sub
      , "%(key)s: subtraction"
      # keep units of x if they are the same as units of y
      , units=lambda calc, units: units[0] if units[0] == units[1] else ''
    )
  , BinaryOp('*', operator.mul, "%(key)s: multiplication")
  , BinaryOp('/', operator.truediv, "%(key)s: true division")
  , BinaryOp('//', operator.floordiv, "%(key)s: floor division")
  , BinaryOp('%', operator.mod, "%(key)s: modulus")
  , BinaryOp(
        '%chg'
      , lambda y, x: 100*(x-y)/y
      , "%(key)s: percent change (100*(x-y)/y)"
    )
  , BinaryOp('**', operator.pow, "%(key)s: raise y to the power of x")
  , UnaryOp('chs', operator.neg, "%(key)s: change sign")
  , UnaryOp('recip', lambda x: 1/x, "%(key)s: reciprocal")
  , UnaryOp('ceil', math.ceil, "%(key)s: round towards positive infinity")
  , UnaryOp('floor', math.floor, "%(key)s: round towards negative infinity")
  , UnaryOp('!', math.factorial, "%(key)s: factorial")
  , UnaryOp(
        'exp'
      , lambda x: cmath.exp(x) if type(x) == complex else math.exp(x)
      , "%(key)s: natural exponential"
    )
  , UnaryOp(
        'ln'
      , lambda x: cmath.log(x) if type(x) == complex else math.log(x)
      , "%(key)s: natural logarithm")
  , UnaryOp('pow10', lambda x: 10**x, "%(key)s: raise 10 to the power of x")
  , UnaryOp('log', math.log10, "%(key)s: base 10 logarithm")
  , UnaryOp(
        'log2'
      , lambda x: math.log(x)/math.log(2)
      , "%(key)s: base 2 logarithm"
    )
  , UnaryOp(
        'sqrt'
      , lambda x: cmath.sqrt(x) if type(x) == complex else math.sqrt(x)
      , "%(key)s: square root"
    )
  , UnaryOp('sqr', lambda x: x*x, "%(key)s: square")
  , Dup(
        'mag'
      , lambda x: abs(x)
      , "%(key)s: magnitude"
      , units=lambda calc, units: units[0]
    )
  , Dup(
        'ph'
      , lambda x, calc: (
            calc._fromRadians(math.atan2(x.imag,x.real))
            if type(x) == complex
            else 0
        )
      , "%(key)s: phase"
      , True
      , units=lambda calc, units: calc._angleUnits()
    )
  , BinaryOp('||', lambda y, x: (x/(x+y))*y, "%(key)s: parallel combination")
  , UnaryOp(
        'sin'
      , lambda x, calc: math.sin(calc._toRadians(x))
      , "%(key)s: sine"
      , True
    )
  , UnaryOp(
        'cos'
      , lambda x, calc: math.cos(calc._toRadians(x))
      , "%(key)s: cosine"
      , True
    )
  , UnaryOp(
        'tan'
      , lambda x, calc: math.tan(calc._toRadians(x))
      , "%(key)s: tangent"
      , True
    )
  , UnaryOp(
        'asin'
      , lambda x, calc: calc._fromRadians(math.asin(x))
      , "%(key)s: arc sine"
      , True
      , units=lambda calc, units: calc._angleUnits()
    )
  , UnaryOp(
        'acos'
      , lambda x, calc: calc._fromRadians(math.acos(x))
      , "%(key)s: arc cosine"
      , True
      , units=lambda calc, units: calc._angleUnits()
    )
  , UnaryOp(
        'atan'
      , lambda x, calc: calc._fromRadians(math.atan(x))
      , "%(key)s: arc tangent"
      , True
      , units=lambda calc, units: calc._angleUnits()
    )
  , BinaryOp(
        'atan2'
      , lambda y, x, calc: calc._fromRadians(math.atan2(y, x))
      , "%(key)s: two-argument arc tangent"
      , True
      , units=lambda calc, units: calc._angleUnits()
    )
  , BinaryOp('hypot', math.hypot, "%(key)s: hypotenuse")
  , BinaryIoOp(
        'rtop'
      , lambda y, x, calc: (math.hypot(y, x), calc._fromRadians(math.atan2(y,x)))
      , "%(key)s: convert rectangular to polar coordinates"
      , True
      , yUnits=lambda calc: calc._angleUnits()
    )
  , BinaryIoOp(
        'ptor'
      , lambda ph, mag, calc: (
            mag*math.cos(calc._toRadians(ph))
          , mag*math.sin(calc._toRadians(ph))
        )
      , "%(key)s: convert polar to rectangular coordinates"
      , True
      , xUnits=lambda calc: calc.stack.peek()[1]
      , yUnits=lambda calc: calc.stack.peek()[1]
    )
  , UnaryOp('sinh', math.sinh, "%(key)s: hyperbolic sine")
  , UnaryOp('cosh', math.cosh, "%(key)s: hyperbolic cosine")
  , UnaryOp('tanh', math.tanh, "%(key)s: hyperbolic tangent")
  , UnaryOp('asinh', math.asinh, "%(key)s: hyperbolic arc sine")
  , UnaryOp('acosh', math.acosh, "%(key)s: hyperbolic arc cosine")
  , UnaryOp('atanh', math.atanh, "%(key)s: hyperbolic arc tangent")
  , UnaryOp(
        'db'
      , lambda x: 20*math.log10(x)
      , "%(key)s: convert voltage or current to dB"
    )
  , UnaryOp(
        'adb'
      , lambda x: 10**(x/20)
      , "%(key)s: convert dB to voltage or current"
    )
  , UnaryOp('db10', lambda x: 10*math.log10(x), "%(key)s: convert power to dB")
  , UnaryOp('adb10', lambda x: 10**(x/10), "%(key)s: convert dB to power")
  , UnaryOp(
        'vdbm'
      , lambda x, calc: 30+10*math.log10(x*x/calc.heap['R'][0]/2)
      , "%(key)s: peak voltage to dBm"
      , True
    )
  , UnaryOp(
        'dbmv'
      , lambda x, calc: math.sqrt(2*pow(10,(x - 30)/10)*calc.heap['R'][0])
      , "%(key)s: dBm to peak voltage"
      , True
      , 'V'
    )
  , UnaryOp(
        'idbm'
      , lambda x, calc: 30+10*math.log10(x*x*calc.heap['R'][0]/2)
      , "%(key)s: peak current to dBm"
      , True
    )
  , UnaryOp(
        'dbmi'
      , lambda x, calc: math.sqrt(2*pow(10,(x - 30)/10)/calc.heap['R'][0])
      , "%(key)s: dBm to peak current"
      , True
      , 'A'
    )
  , Constant('rand', random.random, "%(key)s: random number between 0 and 1")
  , Constant('pi', lambda: math.pi, "%(key)s: 3.141592...", 'rads')
  , Constant('2pi', lambda: 2*math.pi, "%(key)s: 2*pi: 6.283185...", 'rads')
  , Constant(
        'rt2'
      , lambda: math.sqrt(2)
      , "%(key)s: square root of two: 1.4142..."
    )
  , Constant('j', lambda: 1j, "%(key)s: imaginary unit (square root of -1)")
  , Constant('j2pi', lambda: 2j*math.pi, "%(key)s: j*2*pi", 'rads')
  , Constant(
        'h'
      , lambda: 6.6260693e-34
      , "%(key)s: Plank's constant: 6.6260693e-34 J-s"
      , 'J-s'
    )
  , Constant(
        'k'
      , lambda: 1.3806505e-23
      , "%(key)s: Boltzmann's constant: 1.3806505e-23 J/K"
      , 'J/K'
    )
  , Constant(
        'q'
      , lambda: 1.60217653e-19
      , "%(key)s: charge of an electron: 1.60217653e-19 Coul"
      , 'Coul'
    )
  , Constant(
        'c'
      , lambda: 2.99792458e8
      , "%(key)s: speed of light in a vacuum: 2.99792458e8 m/s"
      , 'm/s'
    )
#  , Constant(
#        'G'
#      , lambda: 6.6746e-11
#      , "%(key)s: universal gravitational constant: 6.6746e-11"
#    )
  , Constant(
        '0C'
      , lambda: 273.15
      , "%(key)s: 0 Celsius in Kelvin: 273.15 K"
      , 'K'
    )
  , Constant(
        'eps0'
      , lambda: 8.854187817e-12
      , "%(key)s: 0 permittivity of free space: 8.854187817e-12 F/m"
      , 'F/m'
    )
  , Constant(
        'mu0'
      , lambda: 4e-7*math.pi
      , "%(key)s: 0 permeability of free space: 4e-7*pi N/A^2"
      , 'N/A^2'
    )
  , Number('hex', "0xFF (ex): a number in hexadecimal")
  , Number('oct', "077 (ex): a number in octal") # oct must be before eng
  , Number(
        'eng'
      , "10MHz (ex): a real number, perhaps with a scale factor and units"
    )
  , Number(
        'sci'
      , "1e7 (ex): a real number in scientific notation, perhaps with units"
    )
# Support for Verilog constants was removed when units were added because the
# single quote in the Verilog constant conflicts with the single quotes that
# surround units.
#  , Number(
#        'vhex'
#      , "'hFF (ex): a number in Verilog hexadecimal"
#    )
#  , Number(
#        'vdec'
#      , "'d99 (ex): a number in Verilog decimal"
#    )
#  , Number(
#        'voct'
#      , "'o77 (ex): a number in Verilog octal"
#    )
#  , Number(
#        'vbin'
#      , "'b11 (ex): a number in Verilog binary"
#    )
  , SetFormat(
        'eng'
      , "%(kind)s[N]: use engineering notation, optionally set precision to N digits"
    )
  , SetFormat(
        'fix'
      , "%(kind)s[N]: use fixed notation, optionally set precision to N digits"
    )
  , SetFormat(
        'sci'
      , "%(kind)s[N]: use scientific notation, optionally set precision to N digits"
    )
  , SetFormat(
        'hex'
      , "%(kind)s[N]: use hexadecimal notation, optionally set precision to N digits"
    )
  , SetFormat(
        'oct'
      , "%(kind)s[N]: use octal notation, optionally set precision to N digits"
    )
  , SetFormat(
        'vhex'
      , "%(kind)s[N]: use Verilog hexadecimal notation, optionally set precision to N digits"
    )
  , SetFormat(
        'vdec'
      , "%(kind)s[N]: use Verilog decimal notation, optionally set precision to N digits"
    )
  , SetFormat(
        'voct'
      , "%(kind)s[N]: use Verilog octal notation, optionally set precision to N digits"
    )
  , Store('=name: store value into a variable')
  , Recall('name: recall value of a variable')
  , Print('"text": print text (replacing $N and $Var with the values of register N and variable Var)')
  , SetUnits("'units': set the units of the x register")
  , Swap('%(key)s: swap x and y')
  , Dup('dup', None, '%(key)s: push x onto the stack again')
  , Pop('%(key)s: discard x')
  , Command('rads', useRadians, "%(key)s: use radians")
  , Command('degs', useDegees, "%(key)s: use degrees")
  , Command(
        'vars'
      , lambda stack, calc: calc.heap.display()
      , "%(key)s: print variables"
    )
  , Command(
        'stack'
      , lambda stack, calc: stack.display()
      , "%(key)s: print stack"
    )
  , Command('clstack', lambda stack, calc: stack.clear(), "%(key)s: clear stack")
  , Command('quit', quit, "%(key)s: quit (:q or ^D also works)")
  , Command(':q', quit)
  , Command('help', displayHelp)
]

# Calculator {{{1
class Calculator:
    # before splitting the input, the following regex will be replaced by a
    # space. This allows certain operators to be given abutted to numbers
    operatorSplitRegex = re.compile('''
        (?<=[a-zA-Z0-9])    # alphanum before the split
        (?=[-+*/%!](\s|\Z)) # selected operators followed by white space or EOL
    ''', re.X)
    stringSplitRegex = re.compile(r'''((?:"[^"]*"|'[^']*')+)''')

    # constructor {{{2
    def __init__(
        self
      , actions
      , formatter
      , backUpStack=False
      , messagePrinter=None
      , warningPrinter=None
    ):
        # process the actions, partitioning them into two collections, one with
        # simple names, one with regular expressions
        self.actions = actions
        self.smplActions = {}
        self.regexActions = []
        for each in actions:
            try:
                self.smplActions.update({each.key: each})
            except AttributeError:
                self.regexActions += [each]

        # Initialize the calculator
        self.formatter = formatter
        self.backUpStack = backUpStack
        self.messagePrinter = messagePrinter
        self.warningPrinter = warningPrinter
        self.stack = Stack(parent=self)
        self.heap = Heap(
            initialState = {'R': (50, 'Ohms')}
          , reserved = self.smplActions.keys()
          , removeAction = self.removeAction
          , parent = self
        )
        self.clear()

    # split input into commands {{{2
    def split(self, given):
        '''
        Split a command string into tokens.
        There are a couple of things that complicate this.
        First, strings must be kept intact.
        Second, operators can follow immediately after numbers of words without
            a space, such as in '2 3*'. We want to split those.
        Third, parens, brackets, and braces may but up against the things they
            are grouping, as in '(1.6*)toKm'. In this case the parens should be
            split from their contents, so this should be split into ['(', '1.6',
            '*', ')toKm'].
        '''
        # first add spaces after leading parens and after trailing ones
        processed = given.replace('(', '( ').replace(')', ' )')

        # second, split into strings and non-strings
        components = Calculator.stringSplitRegex.split(processed)
        tokens = []
        for i, component in enumerate(components):
            if i % 2:
                # token is a string
                tokens += [component]
            else:
                # token is not a string
                # add spaces between numbers/identifiers and operators, then
                # split again
                tokens += Calculator.operatorSplitRegex.sub(' ', component).split()
        return tokens

    # evaluate commands {{{2
    def evaluate(self, given):
        '''
        Evaluate a list of commands.
        '''
        if self.backUpStack:
            self.prevStack = self.stack.clone()
        try:
            for cmd in given:
                if cmd in self.smplActions:
                    self.smplActions[cmd].execute(self.stack, self)
                else:
                    for action in self.regexActions:
                        match = action.regex.match(cmd)
                        if match:
                            action.execute(match.groups(), self.stack, self)
                            break
                    else:
                        raise CalculatorError("%s: unrecognized" % cmd)
            return self.stack.peek()
        except (ValueError, OverflowError, ZeroDivisionError, TypeError), err:
            if (
                isinstance(err, TypeError) and
                err.message == "can't convert complex to float"
            ):
                raise CalculatorError(
                    "Function does not support a complex argument."
                )
            else:
                raise CalculatorError(err.message)

    # utility methods {{{2
    def clear(self):
        '''
        Clear the state of the calculator.
        '''
        self.stack.clear()
        self.prevStack = None
        self.formatter.clear()
        self.heap.clear()
        self.setTrigMode('degs')

    def restoreStack(self):
        '''
        Restore stack to its state before the last evaluate.
        Used for recovering from errors.
        '''
        assert self.backUpStack and self.prevStack
        self.stack = self.prevStack

    def format(self, value):
        '''
        Convert a number to a string using the current format settings.
        '''
        return self.formatter.format(value)

    def setTrigMode(self, mode):
        assert mode in ['degs', 'rads']
        self.trigMode = mode
        if mode == 'degs':
            self.convertToRadians = math.pi/180
        else:
            self.convertToRadians = 1

    def removeAction(self, key):
        del self.smplActions[key]

    def _toRadians(self, arg):
        return arg * self.convertToRadians

    def _fromRadians(self, arg):
        return arg / self.convertToRadians

    def _angleUnits(self):
        return self.trigMode

    def printMessage(self, message):
        if self.messagePrinter:
            self.messagePrinter(message)
        else:
            print message

    def printWarning(self, warning):
        if self.warningPrinter:
            self.warningPrinter(warning)
        else:
            print "Warning: %s" % (warning)

# Main {{{1
if __name__ == '__main__':
    import sys, os

    # Configure the command line processor {{{2
    from cmdline import commandLineProcessor

    clp = commandLineProcessor()
    clp.setDescription('Engineering Calculator', '\n'.join([
        'A stack-based (RPN) engineering calculator with a text-based user '
      , 'interface that is intended to be used interactively.'
      , ''
      , 'If run with no arguments, an interactive session is started. '
      , 'If arguments are present, they are tested to see if they are '
      , 'filenames, and if so, the files are opened and the contents are '
      , 'executed as a script.  If they are not file names, then the arguments '
      , 'themselves are treated as scripts and executed directly. The scripts '
      , 'are run in the order they are specified.  In this case an interactive '
      , 'session would not normally be started, but if the interactive option '
      , 'is specified, it would be started after all scripts have been run.'
      , ''
      , 'The contents of ~/.ecrc, ./.ecrc, and the start up file will be run '
      , 'upon start up if they exist, and then the stack is cleared.'
    ]))
    clp.setNumArgs((0,), '[scripts ...]')
    clp.setHelpParams(key='--help', colWidth=18)
    opt = clp.addOption(key='interactive', shortName='i', longName='interactive')
    opt.setSummary('Open an interactive session.')
    opt = clp.addOption(key='printx', shortName='x', longName='printx')
    opt.setSummary(' '.join([
        'Print value of x register upon termination,'
      , 'ignored with interactive sessions.'
    ]))
    opt = clp.addOption(key='startup', shortName='s', longName='startup')
    opt.setSummary(' '.join([
        'Run commands from file to initialize calculator before any script or'
      , 'interactive session is run, stack is cleared after it is run.'
    ]))
    opt.setNumArgs(1, 'file')
    opt = clp.addOption(key='nocolor', shortName='c', longName='nocolor')
    opt.setSummary('Do not color the output.')
    opt = clp.addOption(
        key='help', shortName='h', longName='help', action=clp.printHelp
    )
    opt.setSummary('Print usage information.')

    # Process the command line {{{2
    clp.process()

    # get the command line options and arguments
    opts = clp.getOptions()
    args = clp.getArguments()
    progName = clp.progName()
    colorize = 'nocolor' not in opts
    startUpFile = opts.get('startup', [])
    interactiveSession = True if 'interactive' in opts else not args
    printXuponTermination = 'printx' in opts

    # Import and configure the text colorizer {{{2
    if colorize:
        try:
            import textcolors
        except ImportError:
            colorize = False

    if colorize:
        colors = textcolors.Colors()
        error = colors.colorizer('red')
        highlight = colors.colorizer('magenta')
        warning = colors.colorizer('yellow')
    else:
        error = highlight = warning = lambda x: x

    # Define utility functions {{{2
    def printWarning(message):
        print "%s: %s" % (warning('Warning'), message)

    def evaluateLine(calc, line, prompt):
        try:
            result = calc.evaluate(
                calc.split(line)
            )
            prompt = calc.format(result)
        except CalculatorError, err:
            print error(err.message)
            calc.restoreStack()
        return prompt

    # Create calculator {{{2
    calc = Calculator(
        Actions
      , Display('eng', 4)
      , backUpStack=True
      , warningPrinter=printWarning
    )
    prompt = '0'

    # Run start up files {{{2
    rcFiles = ['%s/.ecrc' % each for each in ['~', '.']]
    for each in rcFiles + startUpFile:
        try:
            cmdFile = expanduser(each)
            with open(cmdFile) as pFile:
                for lineno, line in enumerate(pFile):
                    prompt = evaluateLine(calc, line, prompt)
        except IOError, err:
            if err.errno != 2 or each not in rcFiles:
                exit('%s.$s: %s: %s' % (
                    each, lineno+1, err.filename, err.strerror
                ))
    calc.stack.clear()
    prompt = '0'

    # Run scripts {{{2
    for arg in args:
        try:
            cmdFile = expanduser(arg)
            if os.path.exists(cmdFile):
                with open(cmdFile) as pFile:
                    for lineno, line in enumerate(pFile):
                        loc = '%s.%s: ' % (cmdFile, lineno+1)
                        prompt = evaluateLine(calc, line, prompt)
            else:
                loc = ''
                prompt = evaluateLine(calc, arg, prompt)
        except IOError, err:
            if err.errno != 2:
                exit('%s: %s' % (err.filename, err.strerror))

    # Interact with user {{{2
    if (interactiveSession):
        while(True):
            try:
                entered = raw_input('%s: ' % highlight(prompt))
            except (EOFError, KeyboardInterrupt):
                print
                exit()
            prompt = evaluateLine(calc, entered, prompt)
    elif printXuponTermination:
        print prompt
