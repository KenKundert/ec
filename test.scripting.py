#!/usr/bin/env python

# Test PyCalc
# Imports {{{1
from runtests import cmdLineOpts, writeSummary
from textcolors import Colors
from pycalc import Calculator, Actions, Display, CalculatorError
import math
from subprocess import Popen, PIPE

# Initialization {{{1
fast, printSummary, printTests, printResults, colorize, parent = cmdLineOpts()
testsRun = 0
failures = 0
reltol=1e-9
abstol = 1e-12

colors = Colors(colorize)
succeed = colors.colorizer('green')
fail = colors.colorizer('red')
info = colors.colorizer('magenta')
status = colors.colorizer('cyan')

# Test cases {{{1
testCases = [
    {   'stimulus': "-s lg0.ec '1KHz' lg.ec"
      , 'output': '''\
openloop gain = 4.535M
feedback factor = 16
loopgain = 72.56M
'''
    }
]

# Run tests {{{1
messages = []
warnings = []
def grabMessages(message):
    global messages
    messages += [message]
def grabWarnings(warning):
    global warnings
    warnings += [warning]

calc = Calculator(
    Actions
  , Display('eng', 4)
  , messagePrinter=grabMessages
  , warningPrinter=grabWarnings
)
for index, case in enumerate(testCases):
    messages = []
    warnings = []
    testsRun += 1
    stimulus = 'pycalc ' + case['stimulus']
    expectedResult = case['output']
    if printTests:
        print status('Trying %d:' % index), stimulus

    calc.clear()
    pipe = Popen(stimulus, shell=True, bufsize=-1, stdout=PIPE).stdout
    result = pipe.read()
    if expectedResult != result:
        failures += 1
        print fail('Failure detected (%s):' % failures)
        print info('    Given:'), stimulus
        print info('    Result  :'), result, calc.format((result, units)), units
        print info('    Expected:'), expectedResult, expectedFormattedResult, expectedUnits

    elif printResults:
        print succeed('    Result:'), result
        for message in messages:
            print succeed('    Message received:'), message
        for warning in warnings:
            print succeed('    Warning received:'), warning

# Print test summary {{{1
numTests = len(testCases)
assert testsRun == numTests
if printSummary:
    if failures:
        print fail('FAIL:'),
    else:
        print succeed('PASS:'),
    print '%s tests run, %s failures detected.' % (testsRun, failures)

writeSummary(testsRun, failures)
exit(0 if testsRun == numTests else 0)
