#!/usr/bin/env python

# Test EC
# Imports {{{1
from runtests import cmdLineOpts, writeSummary
from textcolors import Colors
from calculator import Calculator, Display, CalculatorError
from actions import (
    allActions, predefinedVariables, defaultFormat, defaultDigits, detailedHelp
)
import math, sys

# Initialization {{{1
fast, printSummary, printTests, printResults, colorize, parent = cmdLineOpts()
testsRun = 0
failures = 0
reltol=1e-9
abstol = 1e-13

colors = Colors(colorize)
succeed = colors.colorizer('green')
fail = colors.colorizer('red')
info = colors.colorizer('magenta')
status = colors.colorizer('cyan')

# Test cases {{{1
testCases = []
alreadySeen = set([
    None                   # skip categories
  , detailedHelp.getName() # skip detailed help for now
])
for action in allActions:
    if not action:
        continue
    actionName = action.getName()
    if actionName not in alreadySeen:
        alreadySeen.add(actionName)
        if hasattr(action, 'tests'):
            testCases += action.tests
        # Also exercise the detailed help for this action
        detailedHelp.addTest(
            stimulus='?%s' % actionName
          , messages=True
        )

# Add detailedHelp tests (the originals specified with the action, plus the ones
# we just added above)
testCases += detailedHelp.tests

# Finally, you man manually specify additional tests not tied to any particular
# action here
testCases += [
    {   'stimulus': '-failure'
      , 'error': "-failure: unrecognized"
    }
]

# Run tests {{{1
messages = []
warnings = []
def grabMessages(message, style=None):
    global messages
    messages += [message]
def grabWarnings(warning):
    global warnings
    warnings += [warning]

for index, case in enumerate(testCases):
    messages = []
    warnings = []
    testsRun += 1
    stimulus = case['stimulus']
    expectedResult = case.get('result', None)
    expectedUnits = case.get('units', None)
    expectedFormattedResult = case.get('text', None)
    expectedError = case.get('error', None)
    expectedMessages = case.get('messages', [])
    expectedWarnings = case.get('warnings', [])
    if printTests:
        print status('Trying %d:' % index), stimulus

    calc = Calculator(
        allActions
      , Display(defaultFormat, defaultDigits)
      , predefinedVariables=predefinedVariables
      , messagePrinter=grabMessages
      , warningPrinter=grabWarnings
      , backUpStack=True
    )
    try:
        result, units = calc.evaluate(calc.split(stimulus))
        if expectedMessages == True:
            if messages:
                messages = True
        failure = (
            expectedResult != None and (
                abs(result-expectedResult) > (reltol*abs(expectedResult)+abstol)
            ) or
            expectedFormattedResult != None and (
                calc.format((result, units)) != expectedFormattedResult
            ) or
            expectedUnits != None and (units != expectedUnits) or
            expectedError or
            messages != expectedMessages or
            warnings != expectedWarnings
        )
        if failure:
            failures += 1
            print fail('Failure detected (%s):' % failures)
            print info('    Given:'), stimulus
            print info('    Result  :'), ', '.join([
                str(result), calc.format((result, units)), units
            ])
            print info('    Expected:'), ', '.join([
                str(expectedResult)
              , str(expectedFormattedResult)
              , str(expectedUnits)
            ])
            if messages != expectedMessages:
                if expectedMessages == True:
                    print info('    Expected message is missing.')
                else:
                    for message in messages:
                        if message not in expectedMessages:
                            print info('    Message not expected:'), message
                    for message in expectedMessages:
                        if message not in messages:
                            print info('    Expected message not received:'), message
            if warnings != expectedWarnings:
                for warning in warnings:
                    if warning not in expectedWarnings:
                        print info('    Warning not expected:'), warning
                for warning in expectedWarnings:
                    if warning not in warnings:
                        print info('    Expected warning not received:'), warning

        elif printResults:
            print succeed('    Result:'), result
            for message in messages:
                print succeed('    Message received:'), message
            for warning in warnings:
                print succeed('    Warning received:'), warning
    except CalculatorError, err:
        calc.restoreStack()
        if expectedError != err.getMessage():
            failures += 1
            print fail('Failure detected (%s):' % failures)
            print info('    Given:'), stimulus
            print info('    Result  :'), err.message
            print info('    Expected:'), expectedError
        elif printResults:
            print succeed('    Result:'), result

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
