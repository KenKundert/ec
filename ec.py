#!/usr/bin/env python
#
# Engineering Calculator
#
# An RPN calculator that supports numbers with SI scale factors and units.

# Imports {{{1
from __future__ import division
import operator
import math
import cmath
import random
import engfmt
engfmt.setSpacer(' ')
import re
from os.path import expanduser
from copy import copy
from pydoc import pager

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
        return Stack(self.parent, copy(self.stack))

    def __str__(self):
        return str(self.stack)

    def display(self):
        length = len(self.stack)
        labels = ['x:', 'y:'] + (length-2)*['  ']
        for label, value in reversed(zip(labels, self.stack)):
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
                    "%s: variable has overridden built-in." % key
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
            if hasattr(each, 'category'):
                lines += ['\n' + each.description % (each.__dict__)]
            else:
                aliases = each.getAliases()
                if aliases:
                    if len(aliases) > 1:
                        aliases = ' (aliases: %s)' % ','.join(aliases)
                    else:
                        aliases = ' (alias: %s)' % ','.join(aliases)
                else:
                    aliases = ''
                lines += ['    ' + each.description % (each.__dict__) + aliases]
    pager('\n'.join(lines) + '\n')

def useRadians(stack, calc):
    calc.setTrigMode('rads')

def useDegees(stack, calc):
    calc.setTrigMode('degs')

def aboutMsg(stack, calc):
    print "EC was written by Ken Kundert."
    print "Email your comments and questions to ec@shalmirane.com."
    print "To get the source, use 'git clone git@github.com:KenKundert/ec.git'."

def quit(stack, calc):
    exit()

# Action classes {{{1
availableActions = {}
class Action:
    def __init__(self):
        raise NotImplementedError

    def register(self, name):
        assert name not in availableActions, "%s: already defined." % name
        availableActions.update({name: self})

    def addAliases(self, aliases):
        try:
            self.aliases |= set(aliases)
        except AttributeError:
            self.aliases = set(aliases)

    def getAliases(self):
        try:
            return self.aliases
        except AttributeError:
            return set()

# Command (pop 0, push 0, match name) {{{2
class Command(Action):
    """
    Operation that does not affect the stack.
    """
    def __init__(self, key, action, description = None):
        self.key = key
        self.action = action
        self.description = description
        self.register(self.key)

    def execute(self, stack, calc):
        self.action(stack, calc)

# Constant (pop 0, push 1, match name) {{{2
class Constant(Action):
    """
    Operation that pushes one value onto the stack without removing any values.
    """
    def __init__(self, key, action, description = None, units = ''):
        self.key = key
        self.action = action
        self.description = description
        self.units = units
        self.register(self.key)

    def execute(self, stack, calc):
        result = self.action()
        stack.push((result, self.units))

# UnaryOp (pop 1, push 1, match name) {{{2
class UnaryOp(Action):
    """
    Operation that removes one value from the stack, replacing it with another.
    """
    def __init__(self, key, action, description = None, needCalc=False, units=''):
        self.key = key
        self.action = action
        self.description = description
        self.needCalc = needCalc
        self.units = units
        self.register(self.key)

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
class BinaryOp(Action):
    """
    Operation that removes two values from the stack and returns one value.
    """
    def __init__(self, key, action, description = None, needCalc=False, units=''):
        self.key = key
        self.action = action
        self.description = description
        self.needCalc = needCalc
        self.units = units
        self.register(self.key)

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
class BinaryIoOp(Action):
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
        self.register(self.key)

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
class Number(Action):
    def __init__(self, kind, description = None):
        self.kind = kind
        self.description = description
        if kind == 'hexnum':
            pattern = r"0[xX]([0-9a-fA-F]+)"
            self.base = 16
        elif kind == 'octnum':
            pattern = r"0([0-7]+)"
            self.base = 8
        elif kind == 'vhexnum':
            pattern = r"'[hH]([0-9a-fA-F_]*[0-9a-fA-F])"
            self.base = 16
        elif kind == 'vdecnum':
            pattern = r"'[dD]([0-9_]*[0-9])"
            self.base = 10
        elif kind == 'voctnum':
            pattern = r"'[oO]([0-7_]*[0-7])"
            self.base = 8
        elif kind == 'vbinnum':
            pattern = r"'[bB]([01_]*[01])"
            self.base = 2
        elif kind == 'engnum':
            pattern = r'\A(\$?([-+]?[0-9]*\.?[0-9]+)(([YZEPTGMKk_munpfazy])([a-zA-Z_]*))?)\Z'
        elif kind == 'scinum':
            pattern = r'\A(\$?[-+]?[0-9]*\.?[0-9]+[eE][-+]?[0-9]+)([a-zA-Z_]*)\Z'
        else:
            raise NotImplementedError
        self.regex = re.compile(pattern)
        self.register(self.kind)

    def execute(self, matchGroups, stack, calc):
        units = ''
        if self.kind == 'scinum':
            num, units = float(matchGroups[0]), matchGroups[1]
        elif self.kind == 'engnum':
            numWithUnits = engfmt.toNumber(matchGroups[0])
            num, units = numWithUnits
            num = float(num)
        else:
            num = matchGroups[0]
            num = int(num, self.base)
        stack.push((num, units))

# SetFormat (pop 0, push 0, match regex) {{{2
class SetFormat(Action):
    def __init__(self, kind, description = None):
        self.kind = kind
        self.description = description
        self.regex = re.compile('(%s)(\d{1,2})?' % kind)
        self.register(self.kind)

    def execute(self, matchGroups, stack, calc):
        num = matchGroups[0]
        calc.formatter.setStyle(matchGroups[0])
        if matchGroups[1] != None:
            calc.formatter.setDigits(int(matchGroups[1]))

# Store (peek 1, push 0, match regex) {{{2
class Store(Action):
    def __init__(self, description = None):
        self.description = description
        self.regex = re.compile(r'=([a-z]\w*)', re.I)
        self.register('store')

    def execute(self, matchGroups, stack, calc):
        name = matchGroups[0]
        try:
            calc.heap[name] = stack.peek()
        except KeyError:
            raise CalculatorError("%s: reserved, cannot be used as variable name." % name)

# Recall (pop 0, push 1, match regex) {{{2
class Recall(Action):
    def __init__(self, description = None):
        self.description = description
        self.regex = re.compile(r'([a-z]\w*)', re.I)
        self.register('recall')

    def execute(self, matchGroups, stack, calc):
        name = matchGroups[0]
        if name in calc.heap:
            stack.push(calc.heap[name])
        else:
            raise CalculatorError("%s: variable does not exist" % name)

# SetUnits (pop 1, push 1, match regex) {{{2
class SetUnits(Action):
    def __init__(self, description = None):
        self.description = description
        self.regex = re.compile(r"'(.*)'")
        self.register('units')

    def execute(self, matchGroups, stack, calc):
        units, = matchGroups
        x, xUnits = stack.pop()
        stack.push((x, units))

# Print (pop 0, push (Action)0, match regex) {{{2
class Print(Action):
    def __init__(self, description = None):
        self.description = description
        self.regex = re.compile(r'"(.*)"')
        self.argsRegex = re.compile(r'\${?(\w+|\$)}?')
        self.register('print')

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
class Swap(Action):
    """
    Swap the top two entries on the stack.
    """
    def __init__(self, description = None):
        self.key = 'swap'
        self.description = description
        self.register(self.key)

    def execute(self, stack, calc):
        x, xUnits = stack.pop()
        y, yUnits = stack.pop()
        stack.push((x, yUnits))
        stack.push((y, yUnits))

# Dup (peek 1, pu(Action)sh 1, match name) {{{2
class Dup(Action):
    def __init__(self, key, action, description = None, needCalc=False, units=''):
        self.key = key
        self.action = action
        self.description = description
        self.needCalc = needCalc
        self.units = units
        self.register(self.key)

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
class Pop(Action):
    """
    Pop the latest value off stack and discard it.
    """
    def __init__(self, description = None):
        self.key = 'pop'
        self.description = description
        self.register(self.key)

    def execute(self, stack, calc):
        stack.pop()

# Category (not an action, merely a header in the help summary) {{{2
class Category(Action):
    """
    Print a category header in the help command.
    """
    def __init__(self, category, description):
        self.category = category
        self.description = description
        self.register(category)

# Actions {{{1
# Create actions here, they will be registered into availableActions
# automatically. That will be used to build the list of actions to make
# available to the user based on calculator personality later.

# Arithmetic Operators {{{2
arithmeticOperators = Category('arithmeticOperators', "Arithmetic Operators")
addition = BinaryOp(
    '+'
  , operator.add
  , "%(key)s: addition"
  # keep units of x if they are the same as units of y
  , units=lambda calc, units: units[0] if units[0] == units[1] else ''
)
subtraction = BinaryOp(
    '-'
  , operator.sub
  , "%(key)s: subtraction"
  # keep units of x if they are the same as units of y
  , units=lambda calc, units: units[0] if units[0] == units[1] else ''
)
multiplication = BinaryOp('*', operator.mul, "%(key)s: multiplication")
division = BinaryOp('/', operator.truediv, "%(key)s: true division")
floorDivision = BinaryOp('//', operator.floordiv, "%(key)s: floor division")
modulus = BinaryOp('%', operator.mod, "%(key)s: modulus")
percentChange = BinaryOp(
    '%chg'
  , lambda y, x: 100*(x-y)/y
  , "%(key)s: percent change (100*(x-y)/y)"
)
parallel = BinaryOp('||', lambda y, x: (x/(x+y))*y, "%(key)s: parallel combination")
negation = UnaryOp('chs', operator.neg, "%(key)s: change sign")
reciprocal = UnaryOp('recip', lambda x: 1/x, "%(key)s: reciprocal")
ceiling = UnaryOp('ceil', math.ceil, "%(key)s: round towards positive infinity")
floor = UnaryOp('floor', math.floor, "%(key)s: round towards negative infinity")
factorial = UnaryOp('!', math.factorial, "%(key)s: factorial")

# Logs, Powers, and Exponentials {{{2
powersAndLogs = Category(
    'powersAndLogs'
  , "Powers, Roots, Exponentials and Logarithms"
)
power = BinaryOp(
    '**'
  , operator.pow
  , "%(key)s: raise y to the power of x"
)
power.addAliases(['pow', 'ytox'])
exponential = UnaryOp(
    'exp'
  , lambda x: cmath.exp(x) if type(x) == complex else math.exp(x)
  , "%(key)s: natural exponential"
)
exponential.addAliases(['powe'])
naturalLog = UnaryOp(
    'ln'
  , lambda x: cmath.log(x) if type(x) == complex else math.log(x)
  , "%(key)s: natural logarithm"
)
naturalLog.addAliases(['loge'])
tenPower = UnaryOp('pow10', lambda x: 10**x, "%(key)s: raise 10 to the power of x")
tenPower.addAliases(['10tox'])
tenLog = UnaryOp(
    'lg'
  , math.log10
  , "%(key)s: base 10 logarithm"
)
tenLog.addAliases(['log', 'log10'])
twoLog = UnaryOp(
    'lb'
  , lambda x: math.log(x)/math.log(2)
  , "%(key)s: base 2 logarithm"
)
twoLog.addAliases(['log2'])
square = UnaryOp('sqr', lambda x: x*x, "%(key)s: square")
squareRoot = UnaryOp(
    'sqrt'
  , lambda x: cmath.sqrt(x) if type(x) == complex else math.sqrt(x)
  , "%(key)s: square root"
)

from ctypes import util, cdll, c_double
libm = cdll.LoadLibrary(util.find_library('m'))
libm.cbrt.restype = c_double
libm.cbrt.argtypes = [c_double]
cubeRoot = UnaryOp(
    'cbrt'
  , lambda x: libm.cbrt(x)
  , "%(key)s: cube root"
)

# Trig Functions {{{2
trigFunctions = Category(
    'trigFunctions'
  , "Trigonometric Functions"
)
sine = UnaryOp(
        'sin'
      , lambda x, calc: math.sin(calc._toRadians(x))
      , "%(key)s: sine"
      , True
    )
cosine = UnaryOp(
        'cos'
      , lambda x, calc: math.cos(calc._toRadians(x))
      , "%(key)s: cosine"
      , True
    )
tangent = UnaryOp(
        'tan'
      , lambda x, calc: math.tan(calc._toRadians(x))
      , "%(key)s: tangent"
      , True
    )
arcSine = UnaryOp(
        'asin'
      , lambda x, calc: calc._fromRadians(math.asin(x))
      , "%(key)s: arc sine"
      , True
      , units=lambda calc, units: calc._angleUnits()
    )
arcCosine = UnaryOp(
        'acos'
      , lambda x, calc: calc._fromRadians(math.acos(x))
      , "%(key)s: arc cosine"
      , True
      , units=lambda calc, units: calc._angleUnits()
    )
arcTangent = UnaryOp(
        'atan'
      , lambda x, calc: calc._fromRadians(math.atan(x))
      , "%(key)s: arc tangent"
      , True
      , units=lambda calc, units: calc._angleUnits()
    )
setRadiansMode = Command('rads', useRadians, "%(key)s: use radians")
setDegreesMode = Command('degs', useDegees, "%(key)s: use degrees")

# Complex and Vector Functions {{{2
complexAndVectorFunctions = Category(
    'complexAndVectorFunctions'
  , "Complex and Vector Functions"
)
# Absolute Value of a complex number, also known as the magnitude, amplitude, or
# modulus
absoluteValue = Dup(
        'abs'
      , lambda x: abs(x)
      , "%(key)s: magnitude"
      , units=lambda calc, units: units[0]
    )
absoluteValue.addAliases(['mag'])
# Argument of a complex number, also known as the phase , or angle
argument = Dup(
        'arg'
      , lambda x, calc: (
            calc._fromRadians(math.atan2(x.imag,x.real))
            if type(x) == complex
            else 0
        )
      , "%(key)s: phase"
      , True
      , units=lambda calc, units: calc._angleUnits()
    )
argument.addAliases(['ph'])
hypotenuse = BinaryOp(
    'hypot'
  , math.hypot
  , "%(key)s: hypotenuse"
)
hypotenuse.addAliases(['len'])
arcTangent2 = BinaryOp(
    'atan2'
  , lambda y, x, calc: calc._fromRadians(math.atan2(y, x))
  , "%(key)s: two-argument arc tangent"
  , True
  , units=lambda calc, units: calc._angleUnits()
)
arcTangent2.addAliases(['angle'])
rectangularToPolar = BinaryIoOp(
    'rtop'
  , lambda y, x, calc: (math.hypot(y, x), calc._fromRadians(math.atan2(y,x)))
  , "%(key)s: convert rectangular to polar coordinates"
  , True
  , yUnits=lambda calc: calc._angleUnits()
)
polarToRectangular = BinaryIoOp(
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

# Hyperbolic Functions {{{2
hyperbolicFunctions = Category(
    'hyperbolicFunctions'
  , "Hyperbolic Functions"
)
hyperbolicSine = UnaryOp(
    'sinh'
  , math.sinh
  , "%(key)s: hyperbolic sine"
)
hyperbolicCosine = UnaryOp(
    'cosh'
  , math.cosh
  , "%(key)s: hyperbolic cosine"
)
hyperbolicTangent = UnaryOp(
    'tanh'
  , math.tanh
  , "%(key)s: hyperbolic tangent"
)
hyperbolicArcSine = UnaryOp(
    'asinh'
  , math.asinh
  , "%(key)s: hyperbolic arc sine"
)
hyperbolicArcCosine = UnaryOp(
    'acosh'
  , math.acosh
  , "%(key)s: hyperbolic arc cosine"
)
hyperbolicArcTangent = UnaryOp(
    'atanh'
  , math.atanh
  , "%(key)s: hyperbolic arc tangent"
)

# Decibel Functions {{{2
decibelFunctions = Category(
    'decibelFunctions'
  , "Decibel Functions"
)
decibels20 = UnaryOp(
    'db'
  , lambda x: 20*math.log10(x)
  , "%(key)s: convert voltage or current to dB"
)
decibels20.addAliases(['db20', 'v2db', 'i2db'])
antiDecibels20 = UnaryOp(
    'adb'
  , lambda x: 10**(x/20)
  , "%(key)s: convert dB to voltage or current"
)
antiDecibels20.addAliases(['db2v', 'db2i'])
decibels10 = UnaryOp(
    'db10'
  , lambda x: 10*math.log10(x)
  , "%(key)s: convert power to dB"
)
decibels10.addAliases(['p2db'])
antiDecibels10 = UnaryOp(
    'adb10'
  , lambda x: 10**(x/10)
  , "%(key)s: convert dB to power"
)
antiDecibels10.addAliases(['db2p'])
voltageToDbm = UnaryOp(
    'vdbm'
  , lambda x, calc: 30+10*math.log10(x*x/calc.heap['Rref'][0]/2)
  , "%(key)s: peak voltage to dBm (assumes reference resistance of Rref)"
  , True
)
voltageToDbm.addAliases(['v2dbm'])
dbmToVoltage = UnaryOp(
    'dbmv'
  , lambda x, calc: math.sqrt(2*pow(10,(x - 30)/10)*calc.heap['Rref'][0])
  , "%(key)s: dBm to peak voltage (assumes reference resistance of Rref)"
  , True
  , 'V'
)
dbmToVoltage.addAliases(['dbm2v'])
currentToDbm = UnaryOp(
    'idbm'
  , lambda x, calc: 30+10*math.log10(x*x*calc.heap['Rref'][0]/2)
  , "%(key)s: peak current to dBm (assumes reference resistance of Rref)"
  , True
)
currentToDbm.addAliases(['i2dbm'])
dbmToCurrent = UnaryOp(
    'dbmi'
  , lambda x, calc: math.sqrt(2*pow(10,(x - 30)/10)/calc.heap['Rref'][0])
  , "%(key)s: dBm to peak current (assumes reference resistance of Rref)"
  , True
  , 'A'
)
dbmToCurrent.addAliases(['dbm2i'])

# Constants {{{2
constants = Category(
    'constants'
  , "Constants"
)
pi = Constant('pi', lambda: math.pi, "%(key)s: 3.141592...", 'rads')
twoPi = Constant('2pi', lambda: 2*math.pi, "%(key)s: 2*pi: 6.283185...", 'rads')
squareRoot2 = Constant(
    'rt2'
  , lambda: math.sqrt(2)
  , "%(key)s: square root of two: 1.4142..."
)
imaginaryUnit = Constant(
    'j'
  , lambda: 1j
  , "%(key)s: imaginary unit (square root of -1)"
)
imaginaryTwoPi = Constant('j2pi', lambda: 2j*math.pi, "%(key)s: j*2*pi", 'rads')
planksConstantH = Constant(
    'h'
  , lambda: 6.62606957e-34
  , "%(key)s: Plank's constant: 6.62606957e-34 J-s"
  , 'J-s'
)
planksConstantHbar = Constant(
    'hbar'
  , lambda: 1.054571726e-34
  , "%(key)s: Plank's constant: 1.054571726e-34 J-s"
  , 'J-s'
)
planksLength = Constant(
    'lP'
  , lambda: 1.616199e-35
  , "%(key)s: Plank's length: 1.616199e-35 m"
  , 'm'
)
planksMass = Constant(
    'mP'
  , lambda: 2.17651e-5
  , "%(key)s: Plank's mass: 2.17651e-5 g"
  , 'g'
)
planksTemperature = Constant(
    'TP'
  , lambda: 1.416833e32
  , "%(key)s: Plank's temperature: 1.416833e32 K"
  , 'K'
)
planksTime = Constant(
    'tP'
  , lambda: 5.39106e-44
  , "%(key)s: Plank's time: 5.39106e-44 s"
  , 's'
)
boltzmann = Constant(
    'k'
  , lambda: 1.3806488e-23
  , "%(key)s: Boltzmann's constant: 1.3806488e-23 J/K"
  , 'J/K'
)
chargeOfElectron = Constant(
    'q'
  , lambda: 1.602176565e-19
  , "%(key)s: charge of an electron (the elementary charge): 1.602176565e-19 C"
  , 'C'
)
massOfElectron = Constant(
    'me'
  , lambda: 9.10938291e-28
  , "%(key)s: mass of an electron: 9.10938291e-28 g"
  , 'g'
)
massOfProton = Constant(
    'mp'
  , lambda: 1.672621777e-24
  , "%(key)s: mass of a proton: 1.672621777e-24 g"
  , 'g'
)
speedOfLight = Constant(
    'c'
  , lambda: 2.99792458e8
  , "%(key)s: speed of light in a vacuum: 2.99792458e8 m/s"
  , 'm/s'
)
gravitationalConstant = Constant(
    'G'
  , lambda: 6.6746e-11
  , "%(key)s: universal gravitational constant: 6.6746e-11 m^3/(kg-s^2)"
  , "m^3/(kg-s^2)"
)
standardAccelerationOfGravity = Constant(
    'g'
  , lambda: 9.80665
  , "%(key)s: standard acceleration of gravity: 9.80665 m/s^2"
  , 'm/s^2'
)
molarGasConstant = Constant(
    'R'
  , lambda: 8.3144621
  , "%(key)s: molar gas constant: 8.3144621 J/(mol-K)"
  , 'J/(mol-K)'
)
zeroCelsius = Constant(
    '0C'
  , lambda: 273.15
  , "%(key)s: 0 Celsius in Kelvin: 273.15 K"
  , 'K'
)
freeSpacePermittivity = Constant(
    'eps0'
  , lambda: 8.854187817e-12
  , "%(key)s: 0 permittivity of free space: 8.854187817e-12 F/m"
  , 'F/m'
)
freeSpacePermeability = Constant(
    'mu0'
  , lambda: 4e-7*math.pi
  , "%(key)s: 0 permeability of free space: 4e-7*pi N/A^2"
  , 'N/A^2'
)
freeSpaceCharacteristicImpedance = Constant(
    'Z0'
  , lambda: 376.730313461
  , "%(key)s: Characteristic impedance of free space: 376.730313461 Ohms"
  , 'Ohms'
)
avagadroNumber = Constant(
    'NA'
  , lambda: 6.02214129e23
  , "%(key)s: Avagadro Number: 6.02214129e23"
  , 'Ohms'
)
randomNumber = Constant(
    'rand'
  , random.random
  , "%(key)s: random number between 0 and 1"
)

# Numbers {{{2
numbers = Category(
    'numbers'
  , "Numbers"
)
hexadecimalNumber = Number('hexnum', "0xFF (ex): a number in hexadecimal")
octalNumber = Number('octnum', "077 (ex): a number in octal")
    # oct must be before eng
engineeringNumber = Number(
        'engnum'
      , "10MHz (ex): a real number, perhaps with a scale factor and units"
    )
scientificNumber = Number(
        'scinum'
      , "1e7 (ex): a real number in scientific notation, perhaps with units"
    )
# Verilog constants are incompatible with the print command because the
# single quote in the Verilog constant conflicts with the single quotes that
# surround units.
verilogHexadecimalNumber = Number(
    'vhexnum'
  , "'hFF (ex): a number in Verilog hexadecimal"
)
verilogDecimalNumber = Number(
    'vdecnum'
  , "'d99 (ex): a number in Verilog decimal"
)
verilogOctalNumber = Number(
    'voctnum'
  , "'o77 (ex): a number in Verilog octal"
)
verilogBinaryNumber = Number(
    'vbinnum'
  , "'b11 (ex): a number in Verilog binary"
)
setEngineeringFormat = SetFormat(
    'eng'
  , "%(kind)s[N]: use engineering notation, optionally set precision to N digits"
)

# Number Formats {{{2
numberFormats = Category(
    'numberFormats'
  , "Number Formats"
)
setFixedFormat = SetFormat(
    'fix'
  , "%(kind)s[N]: use fixed notation, optionally set precision to N digits"
)
setScientificFormat = SetFormat(
    'sci'
  , "%(kind)s[N]: use scientific notation, optionally set precision to N digits"
)
setHexadecimalFormat = SetFormat(
    'hex'
  , "%(kind)s[N]: use hexadecimal notation, optionally set precision to N digits"
)
setOctalFormat = SetFormat(
    'oct'
  , "%(kind)s[N]: use octal notation, optionally set precision to N digits"
)
setVerilogHexadecimalFormat = SetFormat(
    'vhex'
  , "%(kind)s[N]: use Verilog hexadecimal notation, optionally set precision to N digits"
)
setVerilogDecimalFormat = SetFormat(
    'vdec'
  , "%(kind)s[N]: use Verilog decimal notation, optionally set precision to N digits"
)
setVerilogOctalFormat = SetFormat(
    'voct'
  , "%(kind)s[N]: use Verilog octal notation, optionally set precision to N digits"
)

# Variables {{{2
variableCommands = Category('variableCommands', "Variable Commands")
storeToVariable = Store('=name: store value into a variable')
recallFromVariable = Recall('name: recall value of a variable')
listVariables = Command(
    'vars'
  , lambda stack, calc: calc.heap.display()
  , "%(key)s: print variables"
)

# Stack {{{2
stackCommands = Category('stackCommands', "Stack Commands")
swapXandY = Swap('%(key)s: swap x and y')
duplicateX = Dup('dup', None, '%(key)s: push x onto the stack again')
duplicateX.addAliases(['enter'])
popX = Pop('%(key)s: discard x')
popX.addAliases(['clrx'])
listStack = Command(
    'stack'
  , lambda stack, calc: stack.display()
  , "%(key)s: print stack"
)
clearStack = Command('clstack', lambda stack, calc: stack.clear(), "%(key)s: clear stack")

# Miscellaneous {{{2
miscellaneousCommands = Category('miscellaneous', "Miscellaneous")
printText = Print(' '.join([
    '"text": print text'
  , '(replacing $N and $Var with the values of register N and variable Var)'
]))
setUnits = SetUnits("'units': set the units of the x register")
printAbout = Command('about', aboutMsg, "%(key)s: print information about ec")
terminate = Command('quit', quit, "%(key)s: quit (:q or ^D also works)")
terminate.addAliases([':q'])
printHelp = Command('help', displayHelp)

# Action Sublists {{{1
# Arithmetic Operators {{{2
arithmeticOperatorActions = [
    arithmeticOperators,
    addition,
    subtraction,
    multiplication,
    division,
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
    tenLog,
    twoLog,
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
    planksConstantH,
    chargeOfElectron,
    speedOfLight,
    freeSpacePermittivity,
    freeSpacePermeability,
    freeSpaceCharacteristicImpedance,
]
physicsConstantActions = [
    planksConstantH,
    planksConstantHbar,
    planksLength,
    planksMass,
    planksTemperature,
    planksTime,
    chargeOfElectron,
    massOfElectron,
    massOfProton,
    speedOfLight,
    gravitationalConstant,
    standardAccelerationOfGravity,
    freeSpacePermittivity,
    freeSpacePermeability,
]
chemistryConstantActions = [
    planksConstantH,
    planksConstantHbar,
    chargeOfElectron,
    massOfElectron,
    massOfProton,
    molarGasConstant,
    avagadroNumber,
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
    hexadecimalNumber,
    octalNumber,
    engineeringNumber,
    scientificNumber,
    #verilogHexadecimalNumber,
    #verilogDecimalNumber,
    #verilogOctalNumber,
    #verilogBinaryNumber,
]

# Number Formats {{{2
numberFormatActions = [
    numberFormats,
    setEngineeringFormat,
    setFixedFormat,
    setScientificFormat,
    setHexadecimalFormat,
    setOctalFormat,
    setVerilogHexadecimalFormat,
    setVerilogDecimalFormat,
    setVerilogOctalFormat,
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

# Eliminate any redundancies in the actions list {{{2
alreadySeen = set()
actions = []
for action in actionsToUse:
    try:
        if action.key not in alreadySeen:
            actions += [action]
            alreadySeen.add(action.key)
    except AttributeError:
        try:
            if action.regex not in alreadySeen:
                actions += [action]
                alreadySeen.add(action.regex)
        except AttributeError:
            if action.category not in alreadySeen:
                actions += [action]
                alreadySeen.add(action.category)

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
      , predefinedVariables={}
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
                for alias in each.getAliases():
                    self.smplActions.update({alias: each})
            except AttributeError:
                if hasattr(each, 'regex'):
                    self.regexActions += [each]
                else:
                    assert hasattr(each, 'category')

        # Initialize the calculator
        self.formatter = formatter
        self.backUpStack = backUpStack
        self.messagePrinter = messagePrinter
        self.warningPrinter = warningPrinter
        self.stack = Stack(parent=self)
        self.heap = Heap(
            initialState = predefinedVariables
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
        return self.format(self.stack.peek())

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
            prompt = calc.restoreStack()
        return prompt

    # Create calculator {{{2
    calc = Calculator(
        actions
      , Display('eng', 4)
      , predefinedVariables
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
