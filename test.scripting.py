#!/usr/bin/env python3

# Test ec
# Imports {{{1
from __future__ import print_function
from runtests import cmdLineOpts, writeSummary, succeed, fail, info, status
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

python = 'python%s' % sys.version[0]

# Test cases {{{1
testCases = [
    {   'stimulus': '-s lg0.ec 1KHz lg.ec'
      , 'output': '''\
openloop gain = 63.732
feedback factor = 16
loopgain = 1.0197k
'''
    }
  , {   'stimulus': "'88.3u =Kdet 9.07G =Kvco 2 =M 8 =N 2 =F 1KHz' lg.ec"
      , 'output': '''\
openloop gain = 63.732
feedback factor = 16
loopgain = 1.0197k
'''
    }
  , {   'stimulus': "'88.3u =Kdet' '9.07G =Kvco' '2 =M' '8 =N' '2 =F' '1KHz' lg.ec"
      , 'output': '''\
openloop gain = 63.732
feedback factor = 16
loopgain = 1.0197k
'''
    }
  , {   'stimulus': r"""'88.3u =Kdet 9.07G =Kvco 2 =M 8 =N 2 =F 1KHz =freq 2pi* "rads/s" =omega Kdet Kvco* omega/ M/ =a N F * =f a f* =T `openloop gain = $a\nfeedback factor = $f\nloopgain = $T`'"""
      , 'output': '''\
openloop gain = 63.732
feedback factor = 16
loopgain = 1.0197k
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
    allActions
  , Display(defaultFormat, defaultDigits)
  , messagePrinter=grabMessages
  , warningPrinter=grabWarnings
)
for index, case in enumerate(testCases):
    messages = []
    warnings = []
    testsRun += 1
    stimulus = ' '.join([python, 'ec.py', case['stimulus']])
    expectedResult = case['output']
    if printTests:
        print(status('Trying %d:' % index), stimulus)

    calc.clear()
    pipe = Popen(stimulus, shell=True, bufsize=-1, stdout=PIPE)
    pipe.wait()
    result = pipe.stdout.read().decode()
    if pipe.returncode != 0:
        failures += 1
        print(fail('Failure detected (%s):' % failures))
        print(info('    Given:'), stimulus)
        print(info('    Result  : invalid return code:'), pipe.returncode)
    elif expectedResult != result:
        failures += 1
        print(fail('Failure detected (%s):' % failures))
        print(info('    Given:'), stimulus)
        print(info('    Result  :'), '\n' + result)
        print(info('    Expected:'))
        for r, e in zip(result, expectedResult):
            if r == e:
                print(e, end='')
            else:
                print(fail(e), end='')
        print()

    elif printResults:
        print(succeed('    Result:'), result)
        for message in messages:
            print(succeed('    Message received:'), message)
        for warning in warnings:
            print(succeed('    Warning received:'), warning)

# Print test summary {{{1
numTests = len(testCases)
assert testsRun == numTests, "%s of %s tests run" % (testsRun, numTests)
if printSummary:
    print('%s: %s tests run, %s failures detected.' % (
        fail('FAIL') if failures else succeed('PASS'), testsRun, failures
    ))

writeSummary(testsRun, failures)
sys.exit(int(bool(failures)))
