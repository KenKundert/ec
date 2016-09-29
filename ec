#!/usr/bin/env python
#
# An RPN calculator that supports numbers with SI scale factors and units.

# Description {{{1
"""
Engineering Calculator

A stack-based (RPN) engineering calculator with a text-based user interface that
is intended to be used interactively.

If run with no arguments, an interactive session is started. If arguments are
present, they are tested to see if they are filenames, and if so, the files are
opened and the contents are executed as a script.  If they are not file names,
then the arguments themselves are treated as scripts and executed directly. The
scripts are run in the order they are specified.  In this case an interactive
session would not normally be started, but if the interactive option is
specified, it would be started after all scripts have been run.

The contents of ~/.ecrc, ./.ecrc, and the start up file will be run upon start
up if they exist, and then the stack is cleared.

Usage: ec [options] [<script>...]

Options:
    -i, --interactive   Open an interactive session.
    -x, --printx        Print value of x register upon termination, ignored with
                        interactive sessions.
    -s, --startup file  Run commands from file to initialize calculator before
                        any script or interactive session is run, stack is
                        cleared after it is run.
    -c, --nocolor       Do not color the output.
    -v, --verbose       Narrate the execution of any scripts.
    -h, --help          Print usage information.
"""

# License {{{1
#
# Copyright (C) 2013-16 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].

# Imports {{{1
from __future__ import division
from actions import (
    actionsToUse, predefinedVariables, defaultFormat, defaultDigits
)
from calculator import Calculator, Display, CalculatorError
from docopt import docopt
from inform import Color, display, error, fatal, Inform, warn
from os.path import expanduser
import sys, os

# Read command line {{{1
cmdline = docopt(__doc__)
args = cmdline['<script>']
colorscheme = None if cmdline['--nocolor'] else 'dark'
startUpFile = [cmdline['--startup']] if cmdline['--startup'] else []
interactiveSession = cmdline['--interactive'] or not args
printXuponTermination = cmdline['--printx']
verbose = cmdline['--verbose']
Inform(prog_name=False, colorscheme=colorscheme)

# Define utility functions {{{1
highlight = Color('magenta', colorscheme)

def evaluateLine(calc, line, prompt):
    try:
        result = calc.evaluate(
            calc.split(line)
        )
        prompt = calc.format(result)
    except CalculatorError as err:
        if interactiveSession:
            error(err.message)
            prompt = calc.restoreStack()
        else:
            fatal(err.message)
    return prompt

# Create calculator {{{1
calc = Calculator(
    actionsToUse
  , Display(format=defaultFormat, digits=defaultDigits)
  , predefinedVariables
  , backUpStack=interactiveSession
  , warningPrinter=warn
)
prompt = '0'

# Run start up files {{{1
rcFiles = ['%s/.ecrc' % each for each in ['~', '.']]
for each in rcFiles + startUpFile:
    lineno = None
    try:
        cmdFile = expanduser(each)
        with open(cmdFile) as pFile:
            for lineno, line in enumerate(pFile):
                prompt = evaluateLine(calc, line, prompt)
                if verbose:
                    display("%s %s: %s ==> %s" % (
                        cmdFile, lineno, line.strip(), prompt
                    ))
    except IOError as err:
        if err.errno != 2 or each not in rcFiles:
            sys.exit('%s%s: %s: %s' % (
                each
              , ('.%s' % lineno+1) if lineno != None else ''
              , err.filename
              , err.strerror
            ))
calc.stack.clear()
prompt = '0'

# Run scripts {{{1
for arg in args:
    try:
        cmdFile = expanduser(arg)
        if os.path.exists(cmdFile):
            with open(cmdFile) as pFile:
                for lineno, line in enumerate(pFile):
                    loc = '%s.%s: ' % (cmdFile, lineno+1)
                    prompt = evaluateLine(calc, line, prompt)
                    if verbose:
                        display("%s %s: %s ==> %s" % (
                            cmdFile, lineno, line.strip(), prompt
                        ))
        else:
            loc = ''
            prompt = evaluateLine(calc, arg, prompt)
            if verbose:
                display("%s ==> %s" % (line, prompt))
    except IOError as err:
        if err.errno != 2:
            fatal('%s: %s' % (err.filename, err.strerror))

# Interact with user {{{1
if (interactiveSession):
    while(True):
        try:
            entered = raw_input('%s: ' % highlight(prompt)) # python 2
        except (EOFError, KeyboardInterrupt):
            display()
            sys.exit(0)
        except NameError:
            try:
                entered = input('%s: ' % highlight(prompt)) # python 3
            except (EOFError, KeyboardInterrupt):
                display()
                sys.exit(0)
        prompt = evaluateLine(calc, entered, prompt)
elif printXuponTermination:
    display(prompt)
sys.exit(0)
