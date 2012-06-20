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
from textwrap import wrap, fill, dedent

# Utility functions {{{1
italicsRegex = re.compile(r'#\{(\w+)\}')
boldRegex = re.compile(r'@\{(\w+)\}')

def stripFormatting(text):
    text = italicsRegex.sub(r'\1', text)
    text = boldRegex.sub(r'\1', text)
    return text

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
            return '{0:.{precision}f}'.format(num, precision=self.digits)
        elif self.style == 'sci':
            return '{0:.{precision}e}'.format(num, precision=self.digits)
        elif self.style == 'hex':
            return '{0:#0{width}x}'.format(int(round(num)), width=self.digits+2)
        elif self.style == 'oct':
            return '{0:#0{width}o}'.format(int(round(num)), width=self.digits+2)
        elif self.style == 'bin':
            return '{0:#0{width}b}'.format(int(round(num)), width=self.digits+2)
        elif self.style == 'vhex':
            return "'h{0:0{width}x}".format(int(round(num)), width=self.digits)
        elif self.style == 'vdec':
            return "'d{0:0{width}d}".format(int(round(num)), width=self.digits)
        elif self.style == 'voct':
            return "'o{0:0{width}o}".format(int(round(num)), width=self.digits)
        elif self.style == 'vbin':
            return "'b{0:0{width}b}".format(int(round(num)), width=self.digits)
        else:
            raise AssertionError

    def clear(self):
        self.style = self.defaultStyle
        self.digits = self.defaultDigits

# Helper functions {{{2
from pydoc import pager
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
                lines += wrap(
                    stripFormatting(
                        each.description % (each.__dict__)
                    ) + aliases
                  , initial_indent='    '
                  , subsequent_indent='        '
                )
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

    def getName(self, givenName = None):
        if hasattr(self, 'name') and self.name:
            primaryName = self.name
        elif hasattr(self, 'key') and self.key:
            primaryName = self.key
        else:
            primaryName = None

        if givenName:
            # An argument is given: assure that it corresponds to this action,
            # if so return the primary name, otherwise return None
            if hasattr(self, 'name') and givenName == self.name:
                return primaryName
            if hasattr(self, 'key') and givenName == self.key:
                return primaryName
            if hasattr(self, 'aliases') and givenName in self.aliases:
                return primaryName
            return None
        else:
            # No argument is given: the primary name is returned.
            return primaryName

    def getSynopsis(self):
        try:
            return self.synopsis if self.synopsis else ''
        except AttributeError:
            return ''

    def getSummary(self):
        try:
            return self.summary if self.summary else ''
        except AttributeError:
            return ''

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
    def __init__(self, key, action
      , description = None
      , synopsis = None
      , summary = None
      , aliases = frozenset()
    ):
        self.key = key
        self.action = action
        self.description = description
        self.synopsis = synopsis
        self.summary = summary
        self.aliases = aliases
        self.register(self.key)

    def execute(self, stack, calc):
        self.action(stack, calc)

# Constant (pop 0, push 1, match name) {{{2
class Constant(Action):
    """
    Operation that pushes one value onto the stack without removing any values.
    """
    def __init__(self, key, action
      , description = None
      , units = ''
      , synopsis = None
      , summary = None
      , aliases = frozenset()
    ):
        self.key = key
        self.action = action
        self.description = description
        self.units = units
        self.synopsis = synopsis
        self.summary = summary
        self.aliases = aliases
        self.register(self.key)

    def execute(self, stack, calc):
        result = self.action()
        stack.push((result, self.units))

# UnaryOp (pop 1, push 1, match name) {{{2
class UnaryOp(Action):
    """
    Operation that removes one value from the stack, replacing it with another.
    """
    def __init__(self, key, action
      , description = None
      , needCalc = False
      , units = ''
      , synopsis = None
      , summary = None
      , aliases = frozenset()
    ):
        self.key = key
        self.action = action
        self.description = description
        self.needCalc = needCalc
        self.units = units
        self.synopsis = synopsis
        self.summary = summary
        self.aliases = aliases
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
    def __init__(self, key, action
      , description = None
      , needCalc = False
      , units = ''
      , synopsis = None
      , summary = None
      , aliases = frozenset()
    ):
        self.key = key
        self.action = action
        self.description = description
        self.needCalc = needCalc
        self.units = units
        self.synopsis = synopsis
        self.summary = summary
        self.aliases = aliases
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
    def __init__(self, key, action
      , description=None
      , needCalc=False
      , xUnits=''
      , yUnits=''
      , synopsis = None
      , summary = None
      , aliases = frozenset()
    ):
        self.key = key
        self.action = action
        self.description = description
        self.needCalc = needCalc
        self.xUnits = xUnits
        self.yUnits = yUnits
        self.synopsis = synopsis
        self.summary = summary
        self.aliases = aliases
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
    def __init__(self, name
      , description = None
      , synopsis = None
      , summary = None
      , aliases = frozenset()
    ):
        self.name = name
        self.description = description
        self.synopsis = synopsis
        self.summary = summary
        self.aliases = aliases
        if name == 'hexnum':
            pattern = r"0[xX]([0-9a-fA-F]+)\Z"
            self.base = 16
        elif name == 'octnum':
            pattern = r"0[oO]([0-7]+)\Z"
            self.base = 8
        elif name == 'binnum':
            pattern = r"0[bB]([01]+)\Z"
            self.base = 2
        elif name == 'vhexnum':
            pattern = r"'[hH]([0-9a-fA-F_]*[0-9a-fA-F])\Z"
            self.base = 16
        elif name == 'vdecnum':
            pattern = r"'[dD]([0-9_]*[0-9])\Z"
            self.base = 10
        elif name == 'voctnum':
            pattern = r"'[oO]([0-7_]*[0-7])\Z"
            self.base = 8
        elif name == 'vbinnum':
            pattern = r"'[bB]([01_]*[01])\Z"
            self.base = 2
        elif name == 'engnum':
            pattern = r'\A(\$?([-+]?[0-9]*\.?[0-9]+)(([YZEPTGMKk_munpfazy])([a-zA-Z_]*))?)\Z'
        elif name == 'scinum':
            pattern = r'\A(\$?[-+]?[0-9]*\.?[0-9]+[eE][-+]?[0-9]+)([a-zA-Z_]*)\Z'
        else:
            raise NotImplementedError
        self.regex = re.compile(pattern)
        self.register(self.name)

    def execute(self, matchGroups, stack, calc):
        units = ''
        if self.name == 'scinum':
            num, units = float(matchGroups[0]), matchGroups[1]
        elif self.name == 'engnum':
            numWithUnits = engfmt.toNumber(matchGroups[0])
            num, units = numWithUnits
            num = float(num)
        else:
            num = matchGroups[0]
            num = int(num, self.base)
        stack.push((num, units))

# SetFormat (pop 0, push 0, match regex) {{{2
class SetFormat(Action):
    def __init__(self, name
      , allowPrecision = True
      , description = None
      , summary = None
    ):
        self.name = name
        self.description = description
        self.summary = summary
        self.allowPrecison = allowPrecision
        if allowPrecision:
            self.regex = re.compile(r'(%s)(\d{1,2})?\Z' % name)
        else:
            self.regex = re.compile(r'(%s)\Z' % name)
        self.register(self.name)

    def execute(self, matchGroups, stack, calc):
        num = matchGroups[0]
        calc.formatter.setStyle(matchGroups[0])
        if self.allowPrecison and matchGroups[1] != None:
            calc.formatter.setDigits(int(matchGroups[1]))

# Help (pop 0, push 0, match regex) {{{2
class Help(Action):
    def __init__(self, name = None, description = None, summary = None):
        self.name = name
        self.description = description
        self.summary = summary
        self.regex = re.compile(r'\?(\S+)?')

    def execute(self, matchGroups, stack, calc):
        topic = matchGroups[0]

        # give detailed help on a particular topic
        if topic:
            for action in calc.actions:
                found = action.getName(topic)
                if found:
                    summary = action.getSummary()
                    synopsis = stripFormatting(action.getSynopsis())
                    aliases = action.getAliases()
                    if aliases:
                        if len(aliases) > 1:
                            aliases = 'aliases: %s' % ','.join(aliases)
                        else:
                            aliases = 'alias: %s' % ','.join(aliases)
                    else:
                        aliases = ''
                    if action.description:
                        print stripFormatting(
                            action.description % (action.__dict__)
                        )
                    else:
                        print found + ':'
                    if summary:
                        print
                        print self.formatHelpText(summary)
                    if synopsis or aliases:
                        print
                    if synopsis:
                        print 'synopsis: %s' % synopsis
                    if aliases:
                        print aliases
                    return
            print "%s: not found." % topic
            print

        # present the user with the list of available help topics
        topics = [action.getName() for action in calc.actions if action.getName()]
        colWidth = max([len(topic) for topic in topics]) + 3
        topics.sort()
        print "For summary of all topics, use 'help'."
        print "For help on a particular topic, use '?topic'."
        print
        print "Available topics:"
        numCols = 78//colWidth
        numRows = (len(topics) + numCols - 1)//numCols
        cols = []
        for i in range(numCols):
            cols.append(topics[i*numRows:(i+1)*numRows])
        for i in range(len(cols[0])):
            for j in range(numCols):
                try:
                    print "{0:{width}s}".format(cols[j][i], width=colWidth),
                except IndexError:
                    pass
            print
        return

    def formatHelpText(self, text):
        # get rid of leading indentation and break into individual lines
        lines = dedent(text).strip().splitlines()
        paragraphs = []
        gatheredLines = []
        verbatim = False
        for line in lines:
            if line.strip() == r'\verb{':
                # start of verbatim region
                verbatim = True
                # emit lines gathered so far as a paragraph
                paragraphs += [fill(' '.join(gatheredLines))]
                gatheredLines = []
            elif line.strip() == '}':
                # end of verbatim region
                verbatim = False
            else:
                line = stripFormatting(line)
                if verbatim:
                    paragraphs += [line.rstrip()]
                else:
                    gatheredLines += [line.strip()]
        if gatheredLines:
            paragraphs += [fill(' '.join(gatheredLines))]
        return '\n'.join(paragraphs)

# Store (peek 1, push 0, match regex) {{{2
class Store(Action):
    def __init__(self, name, description = None, summary = None):
        self.name = name
        self.description = description
        self.summary = summary
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
    def __init__(self, name, description = None, summary = None):
        self.name = name
        self.description = description
        self.summary = summary
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
    def __init__(self, name, description = None, summary = None):
        self.name = name
        self.description = description
        self.summary = summary
        self.regex = re.compile(r'"(.*)"')
        self.register('units')

    def execute(self, matchGroups, stack, calc):
        units, = matchGroups
        x, xUnits = stack.pop()
        stack.push((x, units))

# Print (pop 0, push (Action)0, match regex) {{{2
class Print(Action):
    def __init__(self, name, description = None, summary = None):
        self.name = name
        self.description = description
        self.summary = summary
        self.regex = re.compile(r'`(.*)`')
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
    def __init__(self, key
      , description = None
      , synopsis = None
      , summary = None
      , aliases = frozenset()
    ):
        self.key = key
        self.description = description
        self.synopsis = synopsis
        self.summary = summary
        self.aliases = aliases
        self.register(self.key)

    def execute(self, stack, calc):
        x, xUnits = stack.pop()
        y, yUnits = stack.pop()
        stack.push((x, yUnits))
        stack.push((y, yUnits))

# Dup (peek 1, pu(Action)sh 1, match name) {{{2
class Dup(Action):
    def __init__(self, key, action
      , description = None
      , needCalc=False
      , units=''
      , synopsis = None
      , summary = None
      , aliases = frozenset()
    ):
        self.key = key
        self.action = action
        self.description = description
        self.summary = summary
        self.needCalc = needCalc
        self.units = units
        self.synopsis = synopsis
        self.summary = summary
        self.aliases = aliases
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
    def __init__(self, key
      , description = None
      , synopsis = None
      , summary = None
      , aliases = frozenset()
    ):
        self.key = key
        self.description = description
        self.synopsis = synopsis
        self.summary = summary
        self.aliases = aliases
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
# addition {{{3
addition = BinaryOp(
    '+'
  , operator.add
  , description="%(key)s: addition"
  # keep units of x if they are the same as units of y
  , units=lambda calc, units: units[0] if units[0] == units[1] else ''
  , synopsis='#{x} <= #{x}+#{y}'
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
  , synopsis='#{x} <= #{x}-#{y}'
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
  , synopsis='#{x} <= #{x}*#{y}'
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
  , synopsis='#{x} <= #{y}/#{x}'
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
  , synopsis='#{x} <= #{y}//#{x}'
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
  , synopsis='#{x} <= #{y}%#{x}'
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
  , synopsis='#{x} <= 100*(#{x}-#{y})/#{y}'
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
  , synopsis='#{x} <= 1/(1/#{x}+1/#{y})'
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
  , synopsis='#{x} <= -#{x}'
  , summary="""
        The value in the #{x} register is replaced with its negative. 
    """
)
# reciprocal {{{3
reciprocal = UnaryOp(
    'recip'
  , lambda x: 1/x
  , description="%(key)s: reciprocal"
  , synopsis='#{x} <= 1/#{x}'
  , summary="""
        The value in the #{x} register is replaced with its reciprocal. 
    """
)
# ceiling {{{3
ceiling = UnaryOp(
    'ceil'
  , math.ceil
  , description="%(key)s: round towards positive infinity"
  , synopsis='#{x} <= ceil(#{x})'
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
  , synopsis='#{x} <= floor(#{x})'
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
  , synopsis='#{x} <= #{x}!'
  , summary="""
        The value in the #{x} register is replaced with its factorial.
    """
)
# random number {{{3
randomNumber = Constant(
    'rand'
  , random.random
  , description="%(key)s: random number between 0 and 1"
  , synopsis='#{x} <= rand'
  , summary="""
        A number between 0 and 1 is chosen at random and its value is pushed on
        the stack into #{x} register.
    """
)

# Logs, Powers, and Exponentials {{{2
powersAndLogs = Category(
    'powersAndLogs'
  , "Powers, Roots, Exponentials and Logarithms"
)
# power {{{3
power = BinaryOp(
    '**'
  , operator.pow
  , description="%(key)s: raise y to the power of x"
  , synopsis='#{x} <= #{y}**#{x}'
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
  , synopsis='#{x} <= exp(#{x})'
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
  , synopsis='#{x} <= ln(#{x})'
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
  , synopsis='#{x} <= 10**#{x}'
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
  , synopsis='#{x} <= log(#{x})'
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
  , synopsis='#{x} <= log2(#{x})'
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
  , synopsis='#{x} <= #{x}**2'
  , summary="""
        The value in the #{x} register is replaced with its square. 
    """
)
# square root {{{3
squareRoot = UnaryOp(
    'sqrt'
  , lambda x: cmath.sqrt(x) if type(x) == complex else math.sqrt(x)
  , description="%(key)s: square root"
  , synopsis='#{x} <= sqrt(#{x})'
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
  , synopsis='#{x} <= cbrt(#{x})'
  , summary="""
        The value in the #{x} register is replaced with its cube root.
    """
)

# Trig Functions {{{2
trigFunctions = Category(
    'trigFunctions'
  , "Trigonometric Functions"
)
# sine {{{3
sine = UnaryOp(
    'sin'
  , lambda x, calc: math.sin(calc._toRadians(x))
  , description="%(key)s: trigonometric sine"
  , needCalc=True
  , synopsis='#{x} <= sin(#{x})'
  , summary="""
        The value in the #{x} register is replaced with its sine.
    """
)
# cosine {{{3
cosine = UnaryOp(
    'cos'
  , lambda x, calc: math.cos(calc._toRadians(x))
  , description="%(key)s: trigonometric cosine"
  , needCalc=True
  , synopsis='#{x} <= cos(#{x})'
  , summary="""
        The value in the #{x} register is replaced with its cosine.
    """
)
# tangent {{{3
tangent = UnaryOp(
    'tan'
  , lambda x, calc: math.tan(calc._toRadians(x))
  , description="%(key)s: trigonometric tangent"
  , needCalc=True
  , synopsis='#{x} <= tan(#{x})'
  , summary="""
        The value in the #{x} register is replaced with its tangent.
    """
)
# arc sine {{{3
arcSine = UnaryOp(
    'asin'
  , lambda x, calc: calc._fromRadians(math.asin(x))
  , description="%(key)s: trigonometric arc sine"
  , needCalc=True
  , units=lambda calc, units: calc._angleUnits()
  , synopsis='#{x} <= asin(#{x})'
  , summary="""
        The value in the #{x} register is replaced with its arc sine.
    """
)
# arc cosine {{{3
arcCosine = UnaryOp(
    'acos'
  , lambda x, calc: calc._fromRadians(math.acos(x))
  , description="%(key)s: trigonometric arc cosine"
  , needCalc=True
  , units=lambda calc, units: calc._angleUnits()
  , synopsis='#{x} <= acos(#{x})'
  , summary="""
        The value in the #{x} register is replaced with its arc cosine.
    """
)
# arc tangent {{{3
arcTangent = UnaryOp(
    'atan'
  , lambda x, calc: calc._fromRadians(math.atan(x))
  , description="%(key)s: trigonometric arc tangent"
  , needCalc=True
  , units=lambda calc, units: calc._angleUnits()
  , synopsis='#{x} <= atan(#{x})'
  , summary="""
        The value in the #{x} register is replaced with its arc tangent.
    """
)
# radians {{{3
setRadiansMode = Command(
    'rads'
  , useRadians
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
  , useDegees
  , description="%(key)s: use degrees"
  , summary="""
        Switch the trigonometric mode to degrees (functions such as #{sin},
        #{cos}, #{tan}, and #{ptor} expect angles to be given in degrees;
        functions such as #{arg}, #{asin}, #{acos}, #{atan}, #{atan2}, and
        #{rtop} should produce angles in degrees).
    """
)

# Complex and Vector Functions {{{2
complexAndVectorFunctions = Category(
    'complexAndVectorFunctions'
  , "Complex and Vector Functions"
)
# absolute value {{{3
# Absolute Value of a complex number.
# Also known as the magnitude, amplitude, or modulus
absoluteValue = Dup(
    'abs'
  , lambda x: abs(x)
  , description="%(key)s: magnitude"
  , units=lambda calc, units: units[0]
  , synopsis='#{x}, #{y} <= abs(#{x}), #{x}'
  , summary="""
        The absolute value of the number in the #{x} register is pushed onto the
        stack if it is real. If the value is complex, the magnitude is pushed
        onto the stack.
    """
  , aliases=['mag']
)
# argument {{{3
# Argument of a complex number, also known as the phase , or angle
argument = Dup(
    'arg'
  , lambda x, calc: (
        calc._fromRadians(math.atan2(x.imag,x.real))
        if type(x) == complex
        else 0
    )
  , description="%(key)s: phase"
  , needCalc=True
  , units=lambda calc, units: calc._angleUnits()
  , synopsis='#{x}, #{y} <= arg(#{x}), #{x}'
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
  , synopsis='#{x} <= sqrt(#{x}**2+#{y}**2)'
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
  , lambda y, x, calc: calc._fromRadians(math.atan2(y, x))
  , description="%(key)s: two-argument arc tangent"
  , needCalc=True
  , units=lambda calc, units: calc._angleUnits()
  , synopsis='#{x} <= atan2(#{y},#{x})'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and 
        replaced with the angle of the vector from the origin to the point.
    """
  , aliases=['angle']
)
# rectangular to polar {{{3
rectangularToPolar = BinaryIoOp(
    'rtop'
  , lambda y, x, calc: (math.hypot(y, x), calc._fromRadians(math.atan2(y,x)))
  , description="%(key)s: convert rectangular to polar coordinates"
  , needCalc=True
  , yUnits=lambda calc: calc._angleUnits()
  , synopsis='#{x}, #{y} <= sqrt(#{x}**2+#{y}**2), atan2(#{y},#{x})'
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
        mag*math.cos(calc._toRadians(ph))
      , mag*math.sin(calc._toRadians(ph))
    )
  , description="%(key)s: convert polar to rectangular coordinates"
  , needCalc=True
  , xUnits=lambda calc: calc.stack.peek()[1]
  , yUnits=lambda calc: calc.stack.peek()[1]
  , synopsis='#{x}, #{y} <= #{x}*cos(#{y}), #{x}*sin(#{y})'
  , summary="""
        The values in the #{x} and #{y} registers are popped from the stack and
        interpreted as the length and angle of a vector and are replaced with
        the coordinates of the end-point of that vector.
    """
)

# Hyperbolic Functions {{{2
hyperbolicFunctions = Category(
    'hyperbolicFunctions'
  , "Hyperbolic Functions"
)
# hyperbolic sine {{{3
hyperbolicSine = UnaryOp(
    'sinh'
  , math.sinh
  , description="%(key)s: hyperbolic sine"
  , synopsis='#{x} <= sinh(#{x})'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic sine.
    """
)
# hyperbolic cosine {{{3
hyperbolicCosine = UnaryOp(
    'cosh'
  , math.cosh
  , description="%(key)s: hyperbolic cosine"
  , synopsis='#{x} <= cosh(#{x})'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic cosine.
    """
)
# hyperbolic tangent {{{3
hyperbolicTangent = UnaryOp(
    'tanh'
  , math.tanh
  , description="%(key)s: hyperbolic tangent"
  , synopsis='#{x} <= tanh(#{x})'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic tangent.
    """
)
# hyperbolic arc sine {{{3
hyperbolicArcSine = UnaryOp(
    'asinh'
  , math.asinh
  , description="%(key)s: hyperbolic arc sine"
  , synopsis='#{x} <= asinh(#{x})'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic arc sine.
    """
)
# hyperbolic arc cosine {{{3
hyperbolicArcCosine = UnaryOp(
    'acosh'
  , math.acosh
  , description="%(key)s: hyperbolic arc cosine"
  , synopsis='#{x} <= acosh(#{x})'
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
  , synopsis='#{x} <= atanh(#{x})'
  , summary="""
        The value in the #{x} register is replaced with its hyperbolic arc
        tangent.
    """
)

# Decibel Functions {{{2
decibelFunctions = Category(
    'decibelFunctions'
  , "Decibel Functions"
)
# voltage or current to decibels {{{3
decibels20 = UnaryOp(
    'db'
  , lambda x: 20*math.log10(x)
  , description="%(key)s: convert voltage or current to dB"
  , synopsis='#{x} <= 20*log(#{x})'
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
  , synopsis='#{x} <= #{x}=10**(#{x}/20)'
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
  , synopsis='#{x} <= 10*log(#{x})'
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
  , synopsis='#{x} <= 10**(#{x}/10)'
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
  , synopsis='#{x}= 30+10*log10((#{x}**2)/(2*#{Rref}))'
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
  , synopsis='#{x}=sqrt(2*10**(#{x} - 30)/10)*#{Rref})'
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
  , synopsis='#{x}= 30+10*log10(((#{x}**2)*#{Rref}/2)'
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
  , synopsis='#{x}=sqrt(2*10**(#{x} - 30)/10)/#{Rref})'
  , summary="""
        The value in the #{x} register is expected to be a power in decibels
        relative to one milliwatt. It is replaced with the peak current of a
        sinusoid that would be needed to deliver the same power to a load
        resistor equal to #{Rref} (a predefined variable).
    """
  , aliases=['dbm2i']
)

# Constants {{{2
constants = Category(
    'constants'
  , "Constants"
)
# pi {{{3
pi = Constant(
    'pi'
  , lambda: math.pi
  , description="%(key)s: pi"
  , units='rads'
  , synopsis='#{x}=pi'
  , summary="""
        The value of pi (3.141592...) is pushed on the stack into the #{x}
        register.
    """
)
# 2 pi {{{3
twoPi = Constant(
    '2pi'
  , lambda: 2*math.pi
  , description="%(key)s: 2*pi"
  , units='rads'
  , synopsis='#{x}=2*pi'
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
  , synopsis='#{x}=sqrt(2)'
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
  , synopsis='#{x}=j'
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
  , synopsis='#{x}=j*2*pi'
  , summary="""
        2 pi times the imaginary unit (j6.283185...) is pushed on the stack into
        the #{x} register.
    """
)
# plank constant {{{3
planckConstantH = Constant(
    'h'
  , lambda: 6.62606957e-34
  , description="%(key)s: Planck constant"
  , units='J-s'
  , synopsis='#{x}=h'
  , summary="""
        The Planck constant (6.62606957e-34 J-s) is pushed on the stack into
        the #{x} register.
    """
)
# reduced plank constant {{{3
planckConstantHbar = Constant(
    'hbar'
  , lambda: 1.054571726e-34
  , description="%(key)s: Reduced Planck constant"
  , units='J-s'
  , synopsis='#{x}=h/(2*pi)'
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
  , synopsis='#{x}=lP'
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
  , synopsis='#{x}=mP'
  , summary="""
        The Planck mass (sqrt(h*c/(2*pi*G)) or 2.17651e-5 g) is pushed on
        the stack into the #{x} register.
    """
)
# reduced planck mass {{{3
planckMass = Constant(
    'mPr'
  , lambda: 2.17651e-5
  , description="%(key)s: Reduced Planck mass"
  , units='g'
  , synopsis='#{x}=mPr'
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
  , synopsis='#{x}=TP'
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
  , synopsis='#{x}=tP'
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
  , synopsis='#{x}=k'
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
  , synopsis='#{x}=q'
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
  , synopsis='#{x}=me'
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
  , synopsis='#{x}=mp'
  , summary="""
        The mass of a proton (1.672621777e-24 g) is pushed on the stack into
        the #{x} register.
    """
)
# speed of light {{{3
speedOfLight = Constant(
    'c'
  , lambda: 2.99792458e8
  , description="%(key)s: speed of light in a vacuum: 2.99792458e8 m/s"
  , units='m/s'
  , synopsis='#{x}=c'
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
  , synopsis='#{x}=G'
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
  , synopsis='#{x}=g'
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
  , synopsis='#{x}=NA'
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
  , synopsis='#{x}=R'
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
  , synopsis='#{x}=0C'
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
  , synopsis='#{x}=eps0'
  , summary="""
        The permittivity of free space (8.854187817e-12 F/m) is pushed on the
        stack into the #{x} register.
    """
)
# free space permeability {{{3
freeSpacePermeability = Constant(
    'mu0'
  , lambda: 4e-7*math.pi
  , description="%(key)s: 0 permeability of free space"
  , units='N/A^2'
  , synopsis='#{x}=mu0'
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
  , synopsis='#{x}=Z0'
  , summary="""
        The characteristic impedance of free space (376.730313461 Ohms) is
        pushed on the stack into the #{x} register.
    """
)

# Numbers {{{2
numbers = Category(
    'numbers'
  , "Numbers"
)
# real number in engineering notation {{{3
engineeringNumber = Number(
    'engnum'
  , description="<#{N}[.#{M}][#{S}[#{U}]]>: a real number"
  , synopsis='#{x}=num'
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
    'scinum'
  , description="<#{N}[.#{M}]>e<#{E}[#{U}]>: a real number in scientific notation"
  , synopsis='#{x}=num'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is the
        integer portion of the mantissa and #{M} is an optional fractional part.
        #{E} is an integer exponent. #{U} the optional units (must not contain
        special characters).  For example, 2.2e-8F represents 22nF.
    """
)
# hexadecimal number {{{3
hexadecimalNumber = Number(
    'hexnum'
  , description="0x<#{N}>: a hexadecimal number"
  , synopsis='#{x}=num'
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
    'octnum'
  , description="0o<#{N}>: a number in octal"
  , synopsis='#{x}=num'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 8 (it must not contain the digits 8 or 9).  For example,
        0o77 represents the octal number 77 or the decimal number 63.
    """
)
# binary number {{{3
binaryNumber = Number(
    'binnum'
  , description="0b<#{N}>: a number in octal"
  , synopsis='#{x}=num'
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
# Is okay now, cause I switched the quote characters to free up single quotes.
verilogHexadecimalNumber = Number(
    'vhexnum'
  , description="'h<#{N}>: a number in Verilog hexadecimal notation"
  , synopsis='#{x}=num'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 16 (use a-f to represent digits greater than 9).  For
        example, 'hFF represents the hexadecimal number FF or the decimal number
        255.
    """
)
# decimal number in verilog notation {{{3
verilogDecimalNumber = Number(
    'vdecnum'
  , description="'d<#{N}>: a number in Verilog decimal"
  , synopsis='#{x}=num'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 10.  For example, 'd99 represents the decimal number 99.
    """
)
# octal number in verilog notation {{{3
verilogOctalNumber = Number(
    'voctnum'
  , description="'o<#{N}>: a number in Verilog octal"
  , synopsis='#{x}=num'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 8 (it must not contain the digits 8 or 9).  For example,
        'o77 represents the octal number 77 or the decimal number 63.
    """
)
# binary number in verilog notation {{{3
verilogBinaryNumber = Number(
    'vbinnum'
  , description="'b<#{N}>: a number in Verilog binary"
  , synopsis='#{x}=num'
  , summary="""
        The number is pushed on the stack into the #{x} register.  #{N} is an
        integer in base 2 (it may contain only the digits 0 or 1).  For example,
        'b1111 represents the binary number 1111 or the decimal number 15.
    """
)

# Number Formats {{{2
numberFormats = Category(
    'numberFormats'
  , "Number Formats"
)
# fixed format {{{3
setFixedFormat = SetFormat(
    'fix'
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
    'eng'
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
    'sci'
  , description="%(name)s[<#{N}>]: use scientific notation"
  , summary="""
        Numbers are displayed with a fixed number of digits of precision and the
        exponent is given explicitly as an integer.  If an optional whole number
        #{N} immediately follows #{sci}, the precision is set to #{N} digits. 
    """
)
# hexadecimal format {{{3
setHexadecimalFormat = SetFormat(
    'hex'
  , allowPrecision=True
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
    'oct'
  , allowPrecision=True
  , description="%(name)s[<#{N}>]: use octal notation"
  , summary="""
        Numbers are displayed in base 8 with a fixed number of digits.  If an
        optional whole number #{N} immediately follows #{oct}, the number of
        digits displayed is set to #{N}. 
    """
)
# binary format {{{3
setBinaryFormat = SetFormat(
    'bin'
  , allowPrecision=True
  , description="%(name)s[<#{N}>]: use binary notation"
  , summary="""
        Numbers are displayed in base 2 with a fixed number of digits.  If an
        optional whole number #{N} immediately follows #{bin}, the number of
        digits displayed is set to #{N}. 
    """
)
# verilog hexadecimal format {{{3
setVerilogHexadecimalFormat = SetFormat(
    'vhex'
  , allowPrecision=True
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
    'vdec'
  , allowPrecision=True
  , description="%(name)s[<#{N}>]: use Verilog decimal notation"
  , summary="""
        Numbers are displayed in base 10 in Verilog format with a fixed number
        of digits.  If an optional whole number #{N} immediately follows
        #{vdec}, the number of digits displayed is set to #{N}. 
    """
)
# verilog octal format {{{3
setVerilogOctalFormat = SetFormat(
    'voct'
  , allowPrecision=True
  , description="%(name)s[<#{N}>]: use Verilog octal notation"
  , summary="""
        Numbers are displayed in base 8 in Verilog format with a fixed number of
        digits.  If an optional whole number #{N} immediately follows #{voct},
        the number of digits displayed is set to #{N}. 
    """
)
# verilog binary format {{{3
setVerilogBinaryFormat = SetFormat(
    'vbin'
  , allowPrecision=True
  , description="%(name)s[<#{N}>]: use Verilog binary notation"
  , summary="""
        Numbers are displayed in base 2 in Verilog format with a fixed number of
        digits.  If an optional whole number #{N} immediately follows #{vbin},
        the number of digits displayed is set to #{N}. 
    """
)

# Variables {{{2
variableCommands = Category('variableCommands', "Variable Commands")
# store to variable {{{3
storeToVariable = Store(
    'store'
  , description='=<#{name}>: store value into a variable'
  , summary="""
        Store the value in the #{x} register into a variable with the given
        name.
    """
)
# recall from variable {{{3
recallFromVariable = Recall(
    'recall'
  , description='<#{name}>: recall value of a variable'
  , summary="""
        Place the value of the variable with the given name into the #{x}
        register.
    """
)
# list variables {{{3
listVariables = Command(
    'vars'
  , lambda stack, calc: calc.heap.display()
  , description="%(key)s: print variables"
  , summary="""
        List all defined variables and their values.
    """
)

# Stack {{{2
stackCommands = Category('stackCommands', "Stack Commands")
# swap {{{3
swapXandY = Swap(
    'swap'
  , description='%(key)s: swap x and y'
  , synopsis='#{x}, #{y} <= #{y}, #{x}'
  , summary="""
        The values in the #{x} and #{y} registers are swapped.
    """
)
# dup {{{3
duplicateX = Dup(
    'dup'
  , None
  , description="%(key)s: duplicate #{x}"
  , synopsis='#{x}, #{y} <= #{x}, #{x}'
  , summary="""
        The value in the #{x} register is pushed onto the stack again.
    """
  , aliases=['enter']
)
# pop {{{3
popX = Pop(
    'pop'
  , description='%(key)s: discard x'
  , summary="""
        The value in the #{x} register is pulled from the stack and discarded.
    """
  , aliases=['clrx']
)
# stack {{{3
listStack = Command(
    'stack'
  , lambda stack, calc: stack.display()
  , description="%(key)s: print stack"
  , summary="""
        Print all the values stored on the stack.
    """
)
clearStack = Command(
    'clstack'
  , lambda stack, calc: stack.clear()
  , description="%(key)s: clear stack"
  , summary="""
        Remove all values from the stack.
    """
)

# Miscellaneous {{{2
miscellaneousCommands = Category('miscellaneous', "Miscellaneous Commands")
printText = Print(
    name='print'
  , description='`<text>`: print text'
  , summary=dedent("""\
        Print "text" (the contents of the back-quotes) to the terminal.
        Generally used in scripts to report and annotate results.  Any instances
        of $N or ${N} are replaced by the value of register N, where 0
        represents the #{x} register, 1 represents the #{y} register, etc.  Any
        instances of $Var or ${Var} are replaced by the value of the variable
        #{Var}.
    """)
)
setUnits = SetUnits(
    name='units'
  , description='"<units>": set the units of the x register'
)
printAbout = Command(
    'about'
  , aboutMsg
  , description="%(key)s: print information about this calculator"
)
terminate = Command(
    'quit'
  , quit
  , description="%(key)s: quit (:q or ^D also works)"
  , aliases=[':q']
)
printHelp = Command(
    'help'
  , displayHelp
  , description="%(key)s: print a summary of the available features"
)
detailedHelp = Help(
    name='?'
  , description="%(name)s[<topic>]: detailed help on a particular topic"
  , summary=dedent("""\
        A topic, in the form of a symbol or name, may follow the question mark,
        in which case a detailed description will be printed for that topic.
        If no topic is given, a list of available topics is listed.
    """)
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
    planckConstantH,
    elementaryCharge,
    speedOfLight,
    freeSpacePermittivity,
    freeSpacePermeability,
    freeSpaceCharacteristicImpedance,
]
physicsConstantActions = [
    planckConstantH,
    planckConstantHbar,
    planckLength,
    planckMass,
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
    planckConstantH,
    planckConstantHbar,
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
    # strings are delimited by "" and `` (' is reserved for use with verilog
    # integer literals)
    stringSplitRegex = re.compile(r'''((?:"[^"]*"|`[^`]*`)+)''')

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
        Third, parens, brackets, and braces may butt up against the things they
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
        lineno = None
        try:
            cmdFile = expanduser(each)
            with open(cmdFile) as pFile:
                for lineno, line in enumerate(pFile):
                    prompt = evaluateLine(calc, line, prompt)
        except IOError, err:
            if err.errno != 2 or each not in rcFiles:
                exit('%s%s: %s: %s' % (
                    each
                  , ('.%s' % lineno+1) if lineno != None else ''
                  , err.filename
                  , err.strerror
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
