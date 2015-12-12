#!/usr/bin/env python3

# Test EC
# Imports {{{1
from runtests import (
    cmdLineOpts, writeSummary, succeed, fail, info, status
)
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
        print(status('Trying %d:' % index), stimulus)

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
            print("%s:" % fail('Failure detected (%s):' % failures))
            print("%s: %s" % (info('    Given'), stimulus))
            print("%s: %s" % (
                info('    Result  ')
              , ', '.join([str(result), calc.format((result, units)), units])
            ))
            print("%s: %s" % (
                info('    Expected')
              , ', '.join([
                    str(expectedResult)
                  , str(expectedFormattedResult)
                  , str(expectedUnits)
                ])
            ))
            if messages != expectedMessages:
                if expectedMessages == True:
                    print(info('    Expected message is missing.'))
                else:
                    for message in messages:
                        if message not in expectedMessages:
                            print("%s: %s" % (
                                info('    Message not expected'), message)
                            )
                    for message in expectedMessages:
                        if message not in messages:
                            print("%s: %s" % (
                                info(
                                    '    Expected message not received')
                                  , message
                                )
                            )
            if warnings != expectedWarnings:
                for warning in warnings:
                    if warning not in expectedWarnings:
                        print("%s: %s" % (
                            info('    Warning not expected'), warning)
                        )
                for warning in expectedWarnings:
                    if warning not in warnings:
                        print("%s: %s" % (
                            info('    Expected warning not received'), warning
                        ))

        elif printResults:
            print("%s: %s" % (succeed('    Result'), result))
            try:
                for message in messages:
                    print("%s: %s" % (succeed('    Message received'), message))
            except TypeError:
                pass  # occurs if messages is True
            for warning in warnings:
                print("%s: %s" % (succeed('    Warning received'), warning))
    except CalculatorError as err:
        calc.restoreStack()
        if expectedError != err.getMessage():
            failures += 1
            print("%s:" % fail('Failure detected (%s)' % failures))
            print("%s: %s" % (info('    Given'), stimulus))
            print("%s: %s" % (info('    Result  '), err.message))
            print("%s: %s" % (info('    Expected'), expectedError))
        elif printResults:
            print("%s: %s" % (succeed('    Result'), result))

# Print test summary {{{1
numTests = len(testCases)
assert testsRun == numTests, "%s of %s tests run" % (testsRun, numTests)
if printSummary:
    print('%s: %s tests run, %s failures detected.' % (
        fail('FAIL') if failures else succeed('PASS'), testsRun, failures
    ))

writeSummary(testsRun, failures)
sys.exit(int(bool(failures)))
