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
from os.path import expanduser

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
        actionsToUse
      , Display(format=defaultFormat, digits=defaultDigits)
      , predefinedVariables
      , backUpStack=interactiveSession
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
