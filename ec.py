#!/usr/bin/env python
#
# Engineering Calculator
#
# An RPN calculator that supports numbers with SI scale factors and units.

# Imports {{{1
from __future__ import division
from actions import (
    actionsToUse, predefinedVariables, defaultFormat, defaultDigits
)
from calculator import Calculator, Display, CalculatorError
from cmdline import commandLineProcessor
from os.path import expanduser
import sys, os

# Configure the command line processor {{{1
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
opt = clp.addOption(key='verbose', shortName='v', longName='verbose')
opt.setSummary('Narrate the execution of any scripts.')
opt = clp.addOption(
    key='help', shortName='h', longName='help', action=clp.printHelp
)
opt.setSummary('Print usage information.')

# Process the command line {{{1
clp.process()

# get the command line options and arguments
opts = clp.getOptions()
args = clp.getArguments()
progName = clp.progName()
colorize = 'nocolor' not in opts
startUpFile = opts.get('startup', [])
interactiveSession = 'interactive' in opts or not args
printXuponTermination = 'printx' in opts
verbose = 'verbose' in opts

# Import and configure the text colorizer {{{1
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

# Define utility functions {{{1
def printWarning(message):
    print("%s: %s" % (warning('Warning'), message))

def evaluateLine(calc, line, prompt):
    try:
        result = calc.evaluate(
            calc.split(line)
        )
        prompt = calc.format(result)
    except CalculatorError as err:
        if interactiveSession:
            print(error(err.message))
            prompt = calc.restoreStack()
        else:
            sys.exit(error(err.message))
    return prompt

# Create calculator {{{1
calc = Calculator(
    actionsToUse
  , Display(format=defaultFormat, digits=defaultDigits)
  , predefinedVariables
  , backUpStack=interactiveSession
  , warningPrinter=printWarning
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
                    print("%s %s: %s ==> %s" % (
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
                        print("%s %s: %s ==> %s" % (
                            cmdFile, lineno, line.strip(), prompt
                        ))
        else:
            loc = ''
            prompt = evaluateLine(calc, arg, prompt)
            if verbose:
                print("%s ==> %s" % (line, prompt))
    except IOError as err:
        if err.errno != 2:
            sys.exit('%s: %s' % (err.filename, err.strerror))

# Interact with user {{{1
if (interactiveSession):
    while(True):
        try:
            entered = raw_input('%s: ' % highlight(prompt)) # python 2
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(1)
        except NameError:
            try:
                entered = input('%s: ' % highlight(prompt)) # python 3
            except (EOFError, KeyboardInterrupt):
                print()
                sys.exit(1)
        prompt = evaluateLine(calc, entered, prompt)
elif printXuponTermination:
    print(prompt)
sys.exit(0)
