#!/usr/bin/env python

# Test PyCalc
# Imports {{{1
from runtests import cmdLineOpts, writeSummary
from textcolors import Colors
from calculator import Calculator, Display, CalculatorError
from actions import allActions, defaultFormat, defaultDigits
import math, sys
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
    {   'stimulus': '-s lg0.ec 1KHz lg.ec'
      , 'output': '''\
openloop gain = 63.732
feedback factor = 16
loopgain = 1.0197K
'''
    }
  , {   'stimulus': "'88.3u =Kdet 9.07G =Kvco 2 =M 8 =N 2 =F 1KHz' lg.ec"
      , 'output': '''\
openloop gain = 63.732
feedback factor = 16
loopgain = 1.0197K
'''
    }
  , {   'stimulus': "'88.3u =Kdet' '9.07G =Kvco' '2 =M' '8 =N' '2 =F' '1KHz' lg.ec"
      , 'output': '''\
openloop gain = 63.732
feedback factor = 16
loopgain = 1.0197K
'''
    }
  , {   'stimulus': r"""'88.3u =Kdet 9.07G =Kvco 2 =M 8 =N 2 =F 1KHz =freq 2pi* "rads/s" =omega Kdet Kvco* omega/ M/ =a N F * =f a f* =T `openloop gain = $a\nfeedback factor = $f\nloopgain = $T`'"""
      , 'output': '''\
openloop gain = 63.732
feedback factor = 16
loopgain = 1.0197K
'''
    }
  , {   'stimulus': '-v regress.ec < /dev/null > /dev/null'
      , 'output': ''
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
    allActions
  , Display(defaultFormat, defaultDigits)
  , messagePrinter=grabMessages
  , warningPrinter=grabWarnings
)
for index, case in enumerate(testCases):
    messages = []
    warnings = []
    testsRun += 1
    stimulus = 'python ec.py ' + case['stimulus']
    expectedResult = case['output']
    if printTests:
        print status('Trying %d:' % index), stimulus

    calc.clear()
    pipe = Popen(stimulus, shell=True, bufsize=-1, stdout=PIPE)
    pipe.wait()
    result = pipe.stdout.read()
    if pipe.returncode != 0:
        failures += 1
        print fail('Failure detected (%s):' % failures)
        print info('    Given:'), stimulus
        print info('    Result  : invalid return code:'), pipe.returncode
    elif expectedResult != result:
        failures += 1
        print fail('Failure detected (%s):' % failures)
        print info('    Given:'), stimulus
        print info('    Result  :'), '\n' + result
        print info('    Expected:'), '\n' + expectedResult

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
sys.exit(testsRun != numTests)
