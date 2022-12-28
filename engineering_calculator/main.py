#!/usr/bin/env python
# encoding: utf8
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
    -s, --startup file  Run commands from file to initialize calculator before
                        any script or interactive session is run, stack is
                        cleared after it is run.
    -c, --nocolor       Do not color the output.
    -v, --verbose       Narrate the execution of any scripts.
    -V, --version       Print the ec version information.
    -h, --help          Print usage information.
"""

# License {{{1
#
# Copyright (C) 2013-2022 Kenneth S. Kundert
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
from .actions import (
    actionsToUse,
    defaultFormat,
    defaultDigits,
    defaultSpacer,
    predefinedVariables,
)
from .calculator import Calculator, Display, CalculatorError, __version__, __released__
from docopt import docopt
from inform import Color, display, error, fatal, Inform, os_error, warn, terminate
from os.path import expanduser
import sys, os

# Read command line {{{1
def main():
    cmdline = docopt(__doc__)
    args = cmdline["<script>"]
    colorscheme = None if cmdline["--nocolor"] else "dark"
    startUpFile = [cmdline["--startup"]] if cmdline["--startup"] else []
    interactiveSession = cmdline["--interactive"] or not args
    verbose = cmdline["--verbose"]
    Inform(prog_name=False, colorscheme=colorscheme)
    if cmdline["--version"]:
        display("ec version: {} ({})".format(__version__, __released__))
        terminate()

    # Define utility functions {{{1
    highlight = Color("magenta", scheme=colorscheme)

    def evaluateLine(calc, line, prompt):
        try:
            result = calc.evaluate(calc.split(line))
            prompt = calc.format(result)
        except CalculatorError as e:
            if interactiveSession:
                error(e.message)
                prompt = calc.restoreStack()
            else:
                fatal(e.message)
        return prompt

    # Create calculator {{{1
    calc = Calculator(
        actions = actionsToUse,
        formatter = Display(
            formatter=defaultFormat, digits=defaultDigits, spacer=defaultSpacer
        ),
        predefinedVariables = predefinedVariables,
        backUpStack = interactiveSession,
        warningPrinter = lambda warning: None,
            # Disable the warning printer initially to suppress warnings from
            # scripts.  Will add true warning printer before starting
            # interactive session.  This allows users to override built in
            # constants without seeing warnings.
    )
    prompt = "0"

    # Run start up files {{{1
    rcFiles = [f"{d}/.ecrc" for d in ["~", "."]]
    for each in rcFiles + startUpFile:
        lineno = None
        try:
            cmdFile = expanduser(each)
            with open(cmdFile) as pFile:
                for lineno, line in enumerate(pFile):
                    prompt = evaluateLine(calc, line, prompt)
                    if verbose:
                        display(
                            f"{cmdFile} {lineno}: {line.strip()} ==> {prompt}"
                        )
        except OSError as e:
            if each not in rcFiles:
                fatal(os_error(e), culprit=(each, lineno))

    calc.stack.clear()
    prompt = "0"

    # Run scripts {{{1
    for arg in args:
        try:
            cmdFile = expanduser(arg)
            if os.path.exists(cmdFile):
                with open(cmdFile) as pFile:
                    for lineno, line in enumerate(pFile):
                        loc = f"{cmdFile}s.{lineno + 1}: "
                        prompt = evaluateLine(calc, line, prompt)
                        if verbose:
                            display(
                                f"{cmdFile} {lineno}: {line.strip()} ==> {prompt}"
                            )
            else:
                loc = ""
                prompt = evaluateLine(calc, arg, prompt)
                if verbose:
                    display(f"{arg} ==> {prompt}")
        except OSError as e:
            fatal(os_error(e), culprit=(each, lineno))

    # Interact with user {{{1
    if interactiveSession:
        # turn on warnings
        calc.warningPrinter = warn

        while True:
            try:
                entered = input(f"{highlight(prompt)}: ")
            except (EOFError, KeyboardInterrupt, SystemError):
                display()
                terminate()
            prompt = evaluateLine(calc, entered, prompt)

    display(prompt)
    terminate()
