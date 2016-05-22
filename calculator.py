#!/usr/bin/env python
#
# Engineering Calculator Core
#
# An RPN calculator that supports numbers with SI scale factors and units.

# Imports {{{1
from __future__ import division
from __future__ import print_function
import math
import re
from copy import copy
from textwrap import wrap, fill, dedent
from inform import display, warn
from pydoc import pager
import sys

# Set the version information {{{1
versionNumber = '1.1.1'
versionDate = '2016-05-22'

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
    '''
    Calculator Error

    Indicates that an error was found when executing the calculator and contains
    the error message.
    '''
    def __init__(self, message):
        self.message = message
    def getMessage(self):
        '''
        Get the error message.
        '''
        return self.message

# Stack {{{2
class Stack:
    """
    The stack is the used by the calculator to hold the input values, the output
    values, and the intermediate used during a computation.
    """
    def __init__(self, parent, stack = None):
        """
        Creates a stack object.

        Takes one or two arguments:
        parent: the calculator (must provide a method printMessage() that takes
            one string and delivers it to the user).
        stack: a list of values used to initialize the stack (optional).
        """
        self.parent = parent
        if stack == None:
            stack = []
        self.stack = stack

    def push(self, value):
        """
        Push a value onto the stack.

        Takes one argument, the value to be pushed onto the stack.
        """
        self.stack.insert(0, value)

    def pop(self):
        """
        Pop a value off of the stack and return it.
        """
        try:
            return self.stack.pop(0)
        except IndexError:
            return (0, '')

    def peek(self, reg = 0):
        """
        Returns the most recent value pushed onto the stack.
        The stack is not changed.
        """
        try:
            return self.stack[reg]
        except IndexError:
            return (0, '')

    def clear(self):
        """
        Clear the stack.
        """
        self.stack = []

    def clone(self):
        """
        Clone the stack.
        Returns a copy of the stack object.
        """
        return Stack(self.parent, copy(self.stack))

    def __str__(self):
        return str(self.stack)

    def display(self):
        """
        Display the stack
        Prints all of the values contained on the stack.
        """
        length = len(self.stack)
        labels = ['x:', 'y:'] + (length-2)*['  ']
        for label, value in reversed(list(zip(labels, self.stack))):
            self.parent.printMessage(
                '  %s %s' % (label, self.parent.format(value))
            )

# Heap {{{2
class Heap:
    """
    The heap is the used by the calculator for long term storage. It contains a
    set of named values.
    """
    def __init__(
        self
      , parent = None
      , initialState = None
      , reserved = []
      , removeAction = None
    ):
        """
        Creates a heap object.

        Takes the following arguments, all of which are optional:
        parent: the calculator (must provide the methods printMessage() and
            printWarning() that take one string and delivers it to the user).
        initialState: a dictionary of values used to initialize the heap.
        reserved: a list of named actions (individual actions are deleted
            if a heap value is created with the same name if *removeAction* is
            true). In this way variable names (heap values) override built-in
            command and function names.
        removeAction:
            A boolean that indicates that a variable names should override
            built-in command and function names.
        """
        self.parent = parent
        self.initialState = initialState if initialState != None else {}
        self.reserved = list(reserved)
        self.heap = copy(self.initialState)
        self.removeAction = removeAction

    def clear(self):
        """
        Clear the heap.
        """
        self.heap = copy(self.initialState)

    def __str__(self):
        return str(self.heap)

    def display(self):
        """
        Display the heap.
        Prints all of the values contained on the heap.
        """
        for key in sorted(self.heap.keys()):
            self.parent.printMessage(
                '  %s: %s' % (key, self.parent.format(self.heap[key]))
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
    def __init__(self, format, digits = 4):
        self.defaultFormatter = format.formatter
        self.defaultFormatterTakesUnits = format.formatterTakesUnits
        self.defaultDigits = digits
        self.formatter = format.formatter
        self.formatterTakesUnits = format.formatterTakesUnits
        self.digits = digits

    def setFormatter(self, format):
        self.formatter = format.formatter
        self.formatterTakesUnits = format.formatterTakesUnits

    def setDigits(self, digits):
        self.digits = digits

    def format(self, val):
        num, units = val
        if type(num) == complex:
            real = self.format((num.real, units))
            imag = self.format((num.imag, units))
            zero = self.format((0, units))
            one = self.format((1, units))
            units = ' '+units if units else ''

            # suppress the imaginary if it would display as zero
            if imag == zero:
                return real
            elif imag[0] == '-':
                imag = imag[1:] if imag[1:] != one else units.strip()
                if imag == zero:
                    return real
                if real == zero:
                    return '-j' + imag
                return "%s - j%s" % (real, imag)
            else:
                imag = imag if imag != one else units
                if real == zero:
                    return 'j' + imag
                return "%s + j%s" % (real, imag)

        if self.formatterTakesUnits:
            return self.formatter(num, units, self.digits)
        else:
            number = self.formatter(num, self.digits)
            if units == '$':
                return units + number
            elif units == '':
                return number
            else:
                return number + '' + units

    def clear(self):
        self.formatter = self.defaultFormatter
        self.formatterTakesUnits = self.defaultFormatterTakesUnits
        self.digits = self.defaultDigits

# Action classes {{{1
class Action:
    '''
    Base class for all actions.
    '''
    def __init__(self):
        '''
        Do not instantiate this base class.
        '''
        raise NotImplementedError

    def getName(self, givenName = None):
        '''
        Return the primary name of the action.

        Takes one optional argument:
        givenName: causes this function to return the primary name of the action
            if the value of this argument corresponds to this action (is the
            primary name or an alias), otherwise it returns None.
        '''
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

    def getDescription(self):
        '''
        Returns the description of the action.
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is either 'key' or 'name'.
        '''
        try:
            return self.description if self.description else ''
        except AttributeError:
            return ''

    def getSynopsis(self):
        '''
        Returns the synopsis of the action.
        The synopsis is a brief one line description of how the stack is
        affected by this action.
        '''
        try:
            return self.synopsis if self.synopsis else ''
        except AttributeError:
            return ''

    def getSummary(self):
        '''
        Returns the summary of the action.
        The summary is a complete description of the action.
        '''
        try:
            return self.summary if self.summary else ''
        except AttributeError:
            return ''

    def addAliases(self, aliases):
        '''
        Add an alias or a list of aliases to the action.
        '''
        try:
            self.aliases |= set(aliases)
        except AttributeError:
            self.aliases = set(aliases)

    def getAliases(self):
        '''
        Return the alias(es) associated with this action.
        '''
        try:
            return self.aliases
        except AttributeError:
            return set()

    def addTest(self, stimulus
      , result = None, units = None, text = None
      , error = None, messages = None, warnings = None
    ):
        '''
        Add a regression test.

        stimulus:
            A string that contains the test. It will be fed into the calculator.
            The calculator is initially configured in its default state (trig
            mode, output format and precision).
        result:
            The numerical value expected to be in the x register after the
            stimulus has been executed. The test passes if this number is very
            close to the final result (within a relative tolerance of 1e-9 or an
            absolute tolerance of 1e-13). Ignored if None or not given.
        units:
            The units of the value expected to be in the x register at the
            conclusion of the test. Ignored if None or not given.
        text:
            A string that is expected to be the same as that produce by
            formatting the value in the x register at the conclusion of the
            test. Ignored if None or not given.
        error:
            A string that is expected match the error message generated during
            the execution of the stimulus. If None or not given, no error
            messages are expected.
        messages:
            A string or list of strings that are expected match the messages
            generated during the execution of the stimulus. If None or not
            given, no messages are expected. If True, then a message is expected
            but no constraint is placed on the content of the message.
        warnings:
            A string or list of strings that are expected match the warning
            messages generated during the execution of the stimulus. If None or
            not given, no messages are expected.
        '''

        test = {'stimulus': stimulus}
        if result != None:
            test['result'] = result
        if units != None:
            test['units'] = units
        if text != None:
            test['text'] = text
        if error != None:
            test['error'] = error
        if messages != None:
            test['messages'] = [messages] if type(messages) == str else messages
        if warnings != None:
            test['warnings'] = warnings if type(warnings) == list else [warnings]

        if hasattr(self, 'tests'):
            self.tests += [test]
        else:
            self.tests = [test]

        # assure that the action is contained within the stimulus (otherwise
        # this test is likely placed on the wrong action)
        misplacedTest = 'misplaced test: action=%s, stimulus=%s' % (
            self.getName(), stimulus
        )
        components = Calculator.split(stimulus)
        if hasattr(self, 'key'):
            found = self.key in components
            if not found and hasattr(self, 'aliases'):
                found = set(self.aliases).intersection(set(components))
        elif hasattr(self, 'regex'):
            found = False
            for each in components:
                if self.regex.match(each):
                    found = True
                    break
        assert found, misplacedTest

# Command (pop 0, push 0, match name) {{{2
class Command(Action):
    """
    Operation that is activated by a literal match of a string and does not
    affect the stack.

    It takes the following arguments:
    key:
        The symbol or word used to identify the operator (the user types this
        in to execute the command).
    action:
        A function that is called to perform the command. The function takes one
        argument, calc (the calculator object, used to gain access to calculator
        methods such as toRadians(), fromRadians(), angleUnits(), as well as
        stack, heap and formatter methods (using <calc>.stack, <calc>.heap and
        <calc>.formatter).
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is either 'key' or 'name'.
    synopsis (optional):
        The synopsis is a brief one line description of how the stack is
        affected by this action.
    summary (optional):
        The summary is a complete description of the action.
    aliases (optional):
        An alias or a list of aliases for this action.
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

    def _execute(self, calc):
        self.action(calc)

# Constant (pop 0, push 1, match name) {{{2
class Constant(Action):
    """
    Operation that is activated by a literal match of a string and pushes one
    value onto the stack without removing any values.

    It takes the following arguments:
    key:
        The symbol or word used to identify the operator (the user types this
        in to execute the command).
    action:
        A function that is called to perform the command. The function takes an
        argument if *needCalc* is true. The argument is calc (the calculator
        object, used to gain access to calculator methods such as toRadians(),
        fromRadians(), angleUnits(), as well as stack, heap and formatter
        methods (using <calc>.stack, <calc>.heap and <calc>.formatter).
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is either 'key' or 'name'.
    needCalc (optional):
        Boolean. If true, the calculator object will be passed in as an argument
        to *action*. Otherwise, no arguments are passed to *action*.
    units (optional):
        The units of the value being pushed onto the stack.
    synopsis (optional):
        The synopsis is a brief one line description of how the stack is
        affected by this action.
    summary (optional):
        The summary is a complete description of the action.
    aliases (optional):
        An alias or a list of aliases for this action.
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

    def _execute(self, calc):
        stack = calc.stack
        result = self.action()
        stack.push((result, self.units))

# UnaryOp (pop 1, push 1, match name) {{{2
class UnaryOp(Action):
    """
    Operation that is activated by a literal match of a string and removes one
    value from the stack, replacing it with another.

    It takes the following arguments:
    key:
        The symbol or word used to identify the operator (the user types this
        in to execute the command).
    action:
        A function that is called to perform the operation. The function takes
        one argument, or two if *needCalc* is true. The first argument is the
        contents of the *x* register.  The second argument, if given, is *calc*
        (the calculator object, used to gain access to calculator methods such
        as toRadians(), fromRadians(), angleUnits(), as well as stack, heap and
        formatter methods (using <calc>.stack, <calc>.heap and
        <calc>.formatter).
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is either 'key' or 'name'.
    needCalc (optional):
        Boolean. If true, the calculator object will be passed in as an
        additional argument to *action*. Otherwise, only the operand is passed
        to *action*.
    units (optional):
        The units of the value being pushed onto the stack.
    synopsis (optional):
        The synopsis is a brief one line description of how the stack is
        affected by this action.
    summary (optional):
        The summary is a complete description of the action.
    aliases (optional):
        An alias or a list of aliases for this action.
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

    def _execute(self, calc):
        stack = calc.stack
        x, xUnits = stack.pop()
        if self.needCalc:
            x = self.action(x, calc)
        else:
            x = self.action(x)
        if callable(self.units):
            units = self.units(calc, (xUnits,))
        else:
            units = self.units
        stack.push((x, units))

# BinaryOp (pop 2, push 1, match name) {{{2
class BinaryOp(Action):
    """
    Operation that is activated by a literal match of a string and removes two
    values from the stack, returning one.

    It takes the following arguments:
    key:
        The symbol or word used to identify the operator (the user types this
        in to execute the command).
    action:
        A function that is called to perform the operation. The function takes
        two arguments, or three if *needCalc* is true.  The first two arguments
        are the contents of the *y* and *x* resisters. The third argument, if
        given, is *calc* (the calculator object, used to gain access to
        calculator methods such as toRadians(), fromRadians(), angleUnits(), as
        well as stack, heap and formatter methods (using <calc>.stack,
        <calc>.heap and <calc>.formatter).
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is either 'key' or 'name'.
    needCalc (optional):
        Boolean. If true, the calculator object will be passed in as an
        additional argument to *action*. Otherwise, only the operands are passed
        to *action*.
    units (optional):
        The units of the result. May either be a string or a function that
        returns a string. The function takes the calculator object and a tuple
        containing the units of the x and y registers as arguments.
    synopsis (optional):
        The synopsis is a brief one line description of how the stack is
        affected by this action.
    summary (optional):
        The summary is a complete description of the action.
    aliases (optional):
        An alias or a list of aliases for this action.
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

    def _execute(self, calc):
        stack = calc.stack
        x, xUnits = stack.pop()
        y, yUnits = stack.pop()
        if self.needCalc:
            result = self.action(y, x, calc)
        else:
            result = self.action(y, x)
        if callable(self.units):
            units = self.units(calc, (xUnits, yUnits))
        else:
            units = self.units
        stack.push((result, units))

# BinaryIoOp (pop 2, push 2, match name) {{{2
class BinaryIoOp(Action):
    """
    Operation that is activated by a literal match of a string and removes two
    values from the stack and returns two.

    It takes the following arguments:
    key:
        The symbol or word used to identify the operator (the user types this
        in to execute the command).
    action:
        A function that is called to perform the operation. The function takes
        two arguments, or three if *needCalc* is true.  The first two arguments
        are the contents of the *y* and *x* resisters.  The third argument, if
        given, is *calc* (the calculator object, used to gain access to
        calculator methods such as toRadians(), fromRadians(), angleUnits(), as
        well as stack, heap and formatter methods (using <calc>.stack,
        <calc>.heap and <calc>.formatter).
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is either 'key' or 'name'.
    needCalc (optional):
        Boolean. If true, the calculator object will be passed in as an
        additional argument to *action*. Otherwise, only the operands are passed
        to *action*.
    xUnits (optional):
        The units of the *x* value being pushed onto the stack. May either be a
        string or a function that returns a string. The function takes the
        calculator object and a tuple containing the units of the x and y
        registers as arguments.
    yUnits (optional):
        The units of the *y* value being pushed onto the stack. May either be a
        string or a function that returns a string. The function takes the
        calculator object and a tuple containing the units of the x and y
        registers as arguments.
    synopsis (optional):
        The synopsis is a brief one line description of how the stack is
        affected by this action.
    summary (optional):
        The summary is a complete description of the action.
    aliases (optional):
        An alias or a list of aliases for this action.
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

    def _execute(self, calc):
        stack = calc.stack
        x, xUnits = stack.pop()
        y, yUnits = stack.pop()
        if self.needCalc:
            result = self.action(y, x, calc)
        else:
            result = self.action(y, x)
        if callable(self.xUnits):
            xUnits = self.xUnits(calc, (xUnits, yUnits))
        else:
            xUnits = self.xUnits
        if callable(self.yUnits):
            yUnits = self.yUnits(calc, (xUnits, yUnits))
        else:
            yUnits = self.yUnits
        stack.push((result[1], yUnits))
        stack.push((result[0], xUnits))

# Dup (peek 1, push 1, match name) {{{2
class Dup(Action):
    """
    Operation that is activated by a literal match of a string and first
    observes the most recent value on the stack before pushing on another value.
    If no action is specified, the most recent value of the stack is duplicated.

    It takes the following arguments:
    key:
        The symbol or word used to identify the operator (the user types this
        in to execute the command).
    action:
        A function that is called to perform the operation. The function takes
        one argument, or two if *needCalc* is true. The first argument is the
        contents of the *x* register.  The second argument, if given, is *calc*
        (the calculator object, used to gain access to calculator methods such
        as toRadians(), fromRadians(), angleUnits(), as well as stack, heap and
        formatter methods (using <calc>.stack, <calc>.heap and
        <calc>.formatter).
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is either 'key' or 'name'.
    needCalc (optional):
        Boolean. If true, the calculator object will be passed in as an
        additional argument to *action*. Otherwise, only the operand is passed
        to *action*.
    units (optional):
        The units of the value being pushed onto the stack. May either be a
        string or a function that returns a string. The function takes the
        calculator object and a tuple containing the units of the x register as
        arguments.
    synopsis (optional):
        The synopsis is a brief one line description of how the stack is
        affected by this action.
    summary (optional):
        The summary is a complete description of the action.
    aliases (optional):
        An alias or a list of aliases for this action.
    """
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

    def _execute(self, calc):
        stack = calc.stack
        x, xUnits = stack.peek()
        if self.action:
            if self.needCalc:
                x = self.action(x, calc)
            else:
                x = self.action(x)
            if self.units:
                if callable(self.units):
                    xUnits = self.units(calc, (xUnits,))
                else:
                    xUnits = self.units
        stack.push((x, xUnits))

# Number (pop 0, push 1, match regex) {{{2
class Number(Action):
    """
    Operation that is activated by a pattern match of a string. It takes no
    values from the stack but pushes one onto the stack.

    It takes the following arguments:
    pattern:
        A regular expression pattern that must match for *action* to be called.
    action:
        A function that is called to convert the string to a number and units.
        The function takes one argument, or two if *needCalc* is true. The first
        argument is a tuple containing the values of the match groups defined in
        the pattern.  The second argument, if given, is *calc* (the calculator
        object, used to gain access to calculator methods such as toRadians(),
        fromRadians(), angleUnits(), as well as stack, heap and formatter
        methods (using <calc>.stack, <calc>.heap and <calc>.formatter).  The
        function returns two values in the form of a tuple (*value*, *units*).
    name:
        The symbol or word used to identify the type of number. It is entered by
        the user when getting more information (help) on the number.
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is 'name'.
    needCalc (optional):
        Boolean. If true, the calculator object will be passed in as an
        additional argument to *action*. Otherwise, only the matches are passed
        to *action*.
    synopsis (optional):
        The synopsis is a brief one line description of how the stack is
        affected by this action.
    summary (optional):
        The summary is a complete description of the action.
    """
    def __init__(self, pattern, action, name
      , description = None
      , needCalc = False
      , synopsis = None
      , summary = None
    ):
        self.pattern = pattern
        self.action = action
        self.name = name
        self.description = description
        self.needCalc = needCalc
        self.synopsis = synopsis
        self.summary = summary
        self.regex = re.compile(pattern)

    def _execute(self, matchGroups, calc):
        if self.needCalc:
            num, units = self.action(matchGroups, calc)
        else:
            num, units = self.action(matchGroups)
        calc.stack.push((num, units))

# SetFormat (pop 0, push 0, match regex) {{{2
class SetFormat(Action):
    """
    Operation that is activated by a pattern match of a string and does not
    affect the stack.

    It takes the following arguments:
    pattern:
        A regular expression pattern that must match for *action* to be called.
        May contain one match group, the contents of which will be passed to the
        formatter as the *digits* argument.
    action:
        A function that is called to convert a number into a string. The
        function takes two or three arguments. The first is the number to be
        converted. The second is the units, however this is only passed in if
        *actionTakesUnits* is true. The last is *digits*. For floating point
        numbers, this represents the precision and represents the number of
        digits to the right of the decimal point when using scientific notation.
        When not using scientific notation, equivalent precision should be
        produced. For integers, digits represent the minimum number of digits
        used to represent the number. It is not the field width, so 0 rendered
        in hexadecimal with 4 digits would be 0x0000.
    name:
        The symbol or word used to identify the type of number. It is entered by
        the user when getting more information (help) on the number.
    actionTakesUnits (optional):
        Boolean. If True, *action* is passed the units and is expected to handle
        them properly (specifically, it should place the units behind the number
        unless the units are '$' in which case they should go before the
        number; alternatively it can accept and discard the units, as it would
        likely do for integer formats).  If False, the formatter is assumed to
        be unable to handle units and the calculator itself takes on the
        responsibility.
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is 'name'.
    synopsis (optional):
        The synopsis is a brief one line description of how the stack is
        affected by this action.
    summary (optional):
        The summary is a complete description of the action.
    """
    def __init__(self, pattern, action, name
      , actionTakesUnits = False
      , description = None
      , summary = None
    ):
        self.pattern = pattern
        self.formatter = action
        self.name = name
        self.formatterTakesUnits = actionTakesUnits
        self.description = description
        self.summary = summary
        self.regex = re.compile(pattern)

    def _execute(self, matchGroups, calc):
        calc.formatter.setFormatter(self)
        if matchGroups and matchGroups[0] != None:
            calc.formatter.setDigits(int(matchGroups[0]))

# Help (pop 0, push 0, match regex) {{{2
class Help(Action):
    """
    Operation that is activated by a pattern match of a string. The pattern
    contains a name that corresponds to a help topic, that help topic is
    printed.

    It takes the following arguments:
    pattern:
        A regular expression pattern that must match for *action* to be
        activated.  It must contain a match group. The text in the match group
        specifies a help topic, which is either an action key or name.
    name:
        The symbol or word used to identify the help action. It is entered by
        the user when getting more information (help) on the help action.
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is 'name'.
    summary (optional):
        The summary is a complete description of the action.
    """
    def __init__(self, name = None, description = None, summary = None):
        self.name = name
        self.description = description
        self.summary = summary
        self.regex = re.compile(r'\?(\S+)?')

    def _execute(self, matchGroups, calc):
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
                        calc.printMessage(fill(
                            stripFormatting(
                                action.description % (action.__dict__)
                            )
                          , subsequent_indent='    '
                        ))
                    else:
                        calc.printMessage(found + ':')
                    if summary:
                        calc.printMessage()
                        calc.printMessage(self.formatHelpText(summary))
                    if synopsis or aliases:
                        calc.printMessage()
                    if synopsis:
                        calc.printMessage('stack: %s' % synopsis)
                    if aliases:
                        calc.printMessage(aliases)
                    return
            calc.printWarning("%s: not found.\n" % topic)

        # present the user with the list of available help topics
        topics = [action.getName() for action in calc.actions if action.getName()]
        colWidth = max([len(topic) for topic in topics]) + 3
        topics.sort()
        calc.printMessage("For summary of all topics, use 'help'.")
        calc.printMessage("For help on a particular topic, use '?topic'.")
        calc.printMessage()
        calc.printMessage("Available topics:")
        numCols = 78//colWidth
        numRows = (len(topics) + numCols - 1)//numCols
        cols = []
        for i in range(numCols):
            cols.append(topics[i*numRows:(i+1)*numRows])
        for i in range(len(cols[0])):
            for j in range(numCols):
                try:
                    calc.printMessage(
                        "{0:{width}s}".format(cols[j][i], width=colWidth)
                      , style='fragment'
                    )
                except IndexError:
                    pass
            calc.printMessage()
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
    """
    Operation that is activated by a pattern match of a string. The pattern
    contains a name that corresponds to a variable (a named value in the heap),
    the value of the *x* register is stored into that variable.

    It takes the following arguments:
    pattern:
        A regular expression pattern that must match for *action* to be activated.
        It must contain a match group. The text in the match group specifies a
        variable name.
    name:
        The symbol or word used to identify the store action. It is entered by
        the user when getting more information (help) on the action.
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is 'name'.
    summary (optional):
        The summary is a complete description of the action.
    """
    def __init__(self, name, description = None, synopsis = None, summary = None):
        self.name = name
        self.description = description
        self.synopsis = synopsis
        self.summary = summary
        self.regex = re.compile(r'=([a-z]\w*)', re.I)

    def _execute(self, matchGroups, calc):
        name = matchGroups[0]
        try:
            calc.heap[name] = calc.stack.peek()
        except KeyError:
            raise CalculatorError("%s: reserved, cannot be used as variable name." % name)

# Recall (pop 0, push 1, match regex) {{{2
class Recall(Action):
    """
    Operation that is activated by a pattern match of a string. The pattern
    contains a name that corresponds to a variable (a named value in the heap),
    the value of the variable is pushed into the *x* register.

    It takes the following arguments:
    pattern:
        A regular expression pattern that must match for *action* to be activated.
        It must contain a match group. The text in the match group specifies a
        variable name.
    name:
        The symbol or word used to identify the recall action. It is entered by
        the user when getting more information (help) on the action.
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is 'name'.
    summary (optional):
        The summary is a complete description of the action.
    """
    def __init__(self, name, description = None, synopsis = None, summary = None):
        self.name = name
        self.description = description
        self.synopsis = synopsis
        self.summary = summary
        self.regex = re.compile(r'([a-z]\w*)', re.I)

    def _execute(self, matchGroups, calc):
        name = matchGroups[0]
        if name in calc.heap:
            calc.stack.push(calc.heap[name])
        else:
            raise CalculatorError("%s: variable does not exist" % name)

# SetUnits (pop 1, push 1, match regex) {{{2
class SetUnits(Action):
    """
    Operation that is activated by a pattern match of a string. The pattern
    contains a units that are to be attached to the contents of the *x*
    register.

    It takes the following arguments:
    pattern:
        A regular expression pattern that must match for *action* to be activated.
        It must contain a match group. The text in the match group specifies the
        units to attach to the *x* register.
    name:
        The symbol or word used to identify the units action. It is entered by
        the user when getting more information (help) on the action.
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is 'name'.
    summary (optional):
        The summary is a complete description of the action.
    """
    def __init__(self, name, description = None, synopsis = None, summary = None):
        self.name = name
        self.description = description
        self.synopsis = synopsis
        self.summary = summary
        self.regex = re.compile(r'"(.*)"')

    def _execute(self, matchGroups, calc):
        stack = calc.stack
        units, = matchGroups
        x, xUnits = stack.pop()
        stack.push((x, units))

# Print (pop 0, push (Action)0, match regex) {{{2
class Print(Action):
    """
    Operation that is activated by a pattern match of a string. The pattern
    contains a string that is to be printed out for the user.

    It takes the following arguments:
    pattern:
        A regular expression pattern that must match for *action* to be activated.
        It must contain a match group. The text in the match group specifies the
        text to be printed.
    name:
        The symbol or word used to identify the units action. It is entered by
        the user when getting more information (help) on the action.
    description (optional):
        The description is a brief half line description of the action.
        It may contain '%(attr)s' codes to access the values of attributes of
        the action. Typically *attr* is 'name'.
    summary (optional):
        The summary is a complete description of the action.
    """
    def __init__(self, name, description = None, summary = None):
        self.name = name
        self.description = description
        self.summary = summary
        self.regex = re.compile(r'`(.*)`')
        self.argsRegex = re.compile(r'\${?(\w+|\$)}?')

    def _execute(self, matchGroups, calc):
        # Prints a message after expanding any $codes it contains
        # $N or ${N} are replaced by the contents of a stack register (0=x, ...)
        # $name or ${name} are replaced by the contents of a variable
        # $$ is replaced by $
        text, = matchGroups
        if not text:
            message = calc.format(calc.stack.stack[0])
        else:
            # process newlines and tabs
            text = text.replace(r'\n', '\n')
            text = text.replace(r'\t', '\t')
            components = self.argsRegex.split(text)
            textFrags = components[0::2]
            args = components[1::2]
            formattedArgs = []
            for arg in args:
                try:
                    try:
                        arg = calc.stack.stack[int(arg)]
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

# Category (not an action, merely a header in the help summary) {{{2
class Category(Action):
    """
    Print a category header in the help command.

    It takes the following arguments:
    description (optional):
        The description is a brief one line description of the category.
    """
    def __init__(self, description):
        self.category = description
        self.description = description

# Calculator {{{1
class Calculator:
    '''
    The calculator.

    It takes the following arguments:
    actions:
        The list of actions to support.
    formatter:
        The formatter object, responsible for formatting and displaying the
        results.
    predefinedVariables (optional):
        A dictionary of variables (names and values) that should be predefined
        when the calculator starts.
    backUpStack (optional):
        Boolean. If true, back up the stack before executing any actions and
        restore the stack if there are any errors. This is generally use with
        user interactive sessions.
    messagePrinter (optional):
        Function that takes a string an prints it for the user. A string is
        passed as a second argument. It can take three possible values: 'line'
        indicates a newline should be added to the end of the message,
        'fragment' indicates that a newline should not be added, and 'page'
        indicates that the message is expected to be long and so a pager should
        be used when displaying the message.
    warningPrinter (optional):
        Function that takes a string an prints it for the user as a warning.
    '''
    # before splitting the input, the following regex will be replaced by a
    # space. This allows certain operators to be given abutted to numbers
    operatorSplitRegex = re.compile('''
        (?<=[a-zA-Z0-9])    # alphanum before the split
        (?=([-+*/%!]|\*\*|\|\||//)(\s|\Z)) # selected operators followed by white space or EOL: - + * / % ! ** || //
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
        # Process the actions, pruning out those already seen, assuring that
        # there are no duplicate names, and partitioning the actions into two
        # collections, one with simple names, one with regular expressions.
        alreadySeen = set()
        prunedActions = []
        self.smplActions = {}
        self.regexActions = []
        names = set()
        for action in actions:
            if not action:
                # not an action, skip it
                # this generally occurs for operations that do not exist in
                # earlier versions of the python math library (it is easier
                # to set them to None that to edit them out of the list)
                continue
            elif hasattr(action, 'key'):
                if action.key not in alreadySeen:
                    self.smplActions.update({action.key: action})
                    prunedActions += [action]
                    alreadySeen.add(action.key)
                    assert action.key not in names, '%s: duplicate name' % (
                        action.key
                    )
                    names.add(action.key)
                    for alias in action.getAliases():
                        assert alias not in names, '%s: duplicate name' % alias
                        names.add(alias)
                        self.smplActions.update({alias: action})
            elif hasattr(action, 'regex'):
                if action.regex not in alreadySeen:
                    self.regexActions += [action]
                    prunedActions += [action]
                    alreadySeen.add(action.regex)
                    assert action.name not in self.smplActions, (
                        '%s: duplicate name' % action.name
                    )
                    names.add(action.name)
            else:
                assert hasattr(action, 'category'), 'expected category: %s' % (action.__dict__)
                prunedActions += [action]
        self.actions = prunedActions

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
    @classmethod
    def split(cls, given):
        '''
        Split a command string into tokens.

        Takes a sequence of commands, numbers, operators, and functions (as a
        string) and returns the same sequence as a list. Each command, number,
        operator and function is separated into its own entry in the list.
        '''
        #There are a couple of things that complicate this.
        #First, strings must be kept intact.
        #Second, operators can follow immediately after numbers of words without
        #    a space, such as in '2 3*'. We want to split those.
        #Third, parens, brackets, and braces may butt up against the things they
        #    are grouping, as in '(1.6*)toKm'. In this case the parens should be
        #    split from their contents, so this should be split into ['(', '1.6',
        #    '*', ')toKm'].

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
        Execute a list of actions.

        Will raise a CalculatorError if there is a problem.
        '''
        if self.backUpStack:
            self.prevStack = self.stack.clone()
        try:
            for cmd in given:
                if cmd in self.smplActions:
                    self.smplActions[cmd]._execute(self)
                else:
                    for action in self.regexActions:
                        match = action.regex.match(cmd)
                        if match:
                            action._execute(match.groups(), self)
                            break
                    else:
                        raise CalculatorError("%s: unrecognized." % cmd)
            return self.stack.peek()
        except (ValueError, OverflowError, TypeError) as err:
            if (
                isinstance(err, TypeError) and
                str(err).startswith("can't convert complex to float")
            ):
                raise CalculatorError(
                    "Function does not support a complex argument."
                )
            else:
                raise CalculatorError(str(err))
        except ZeroDivisionError as err:
            raise CalculatorError("division by zero.")

    # utility methods {{{2
    def clear(self):
        '''
        Clear the state of the calculator.
        '''
        self.stack.clear()
        self.prevStack = None
        self.formatter.clear()
        self.heap.clear()
        self.useDegrees()

    def restoreStack(self):
        '''
        Restore stack to its state before the last evaluate.
        Used for recovering from errors.
        '''
        self.stack = self.prevStack
        return self.format(self.stack.peek())

    def format(self, value):
        '''
        Convert a number to a string using the current format settings.
        '''
        return self.formatter.format(value)

    def removeAction(self, key):
        '''
        Remove a named action. Used by heap to override commands and functions
        when a user creates a variable of the same name.
        '''
        del self.smplActions[key]

    def useRadians(self):
        self.trigMode = 'rads'
        self.convertToRadians = 1

    def useDegrees(self):
        self.trigMode = 'degs'
        self.convertToRadians = math.pi/180

    def toRadians(self, arg):
        '''
        Converts a number to radians (affected by trig mode).
        '''
        return arg * self.convertToRadians

    def fromRadians(self, arg):
        '''
        Converts a number from radians (affected by trig mode).
        '''
        return arg / self.convertToRadians

    def angleUnits(self):
        '''
        Converts a number from radians (affected by trig mode).
        '''
        return self.trigMode

    def swap(self):
        stack = self.stack
        x, xUnits = stack.pop()
        y, yUnits = stack.pop()
        stack.push((x, yUnits))
        stack.push((y, yUnits))

    def pop(self):
        self.stack.pop()

    def printMessage(self, message='', style='line'):
        '''
        Prints a message to the user.
        '''
        if self.messagePrinter:
            self.messagePrinter(message, style)
        else:
            if style == 'page':
                pager(message)
            elif style == 'line':
                display(message)
            else:
                assert style == 'fragment'
                display(message, end=' ')

    def printWarning(self, warning):
        '''
        Prints a message to the user in the form of a warning.
        '''
        if self.warningPrinter:
            self.warningPrinter(warning)
        else:
            warn(warning)

    def displayHelp(calc):  # pylint: disable=no-self-argument
        '''
        Print a single line summary of all available actions.
        '''
        lines = []
        for action in calc.actions:
            if action.description:
                if hasattr(action, 'category'):
                    lines += ['\n' + action.description % (action.__dict__)]
                else:
                    aliases = action.getAliases()
                    if aliases:
                        if len(aliases) > 1:
                            aliases = ' (aliases: %s)' % ','.join(aliases)
                        else:
                            aliases = ' (alias: %s)' % ','.join(aliases)
                    else:
                        aliases = ''
                    lines += wrap(
                        stripFormatting(
                            action.description % (action.__dict__)
                        ) + aliases
                      , initial_indent='    '
                      , subsequent_indent='        '
                    )
        calc.printMessage('\n'.join(lines) + '\n', style='page')

    def aboutMsg(calc):  # pylint: disable=no-self-argument
        '''
        Print administrative information about EC.
        '''
        calc.printMessage(dedent("""\
            EC: Engineering Calculator
            Version %s (%s).

            EC was written by Ken Kundert.
            Email your comments and questions to ec@nurdletech.com.
            To get the source, use 'git clone git@github.com:KenKundert/ec.git'.\
        """ % (versionNumber, versionDate)))

    def quit(calc):  # pylint: disable=no-self-argument
        '''
        Quit EC.
        '''
        sys.exit(0)
