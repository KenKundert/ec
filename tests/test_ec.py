#!/usr/bin/env python3
# encoding: utf8

# Test EC
# Imports {{{1
from engineering_calculator.calculator import Calculator, Display, CalculatorError
from engineering_calculator.actions import (
    allActions, predefinedVariables, defaultFormat, defaultDigits, detailedHelp
)
import pytest

# Utility functions {{{1
messages = []
def grab_messages(message, style=None):
    global messages
    messages += [message]

warnings = []
def grab_warnings(warning):
    global warnings
    warnings += [warning]

reltol=1e-9
abstol = 1e-13
def close(result, expected):
    return abs(result-expected) <= (reltol*abs(expected)+abstol)

# test_built_ins() {{{1
def test_built_ins():
    global messages
    global warnings

    testCases = []
    alreadySeen = set([
        None,                  # skip categories
        detailedHelp.getName() # skip detailed help for now
    ])
    for action in allActions:
        if not action:
            continue
        actionName = action.getName()
        if actionName not in alreadySeen:
            alreadySeen.add(actionName)
            # Same action may show up several times because it is in several
            # different personalities. Just test it the first time it is seen.
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
        dict(stimulus = '-failure', error = "-failure: unrecognized.")
    ]

    calc = Calculator(
        allActions,
        Display(defaultFormat, defaultDigits),
        predefinedVariables = predefinedVariables,
        messagePrinter = grab_messages,
        warningPrinter = grab_warnings,
        backUpStack = True
    )

    # Run tests {{{1
    for index, case in enumerate(testCases):
        messages = []
        warnings = []
        stimulus = case['stimulus']
        expectedResult = case.get('result', None)
        expectedUnits = case.get('units', None)
        expectedFormattedResult = case.get('text', None)
        expectedError = case.get('error', None)
        expectedMessages = case.get('messages', [])
        expectedWarnings = case.get('warnings', [])
        calc.clear()

        try:
            result, units = calc.evaluate(calc.split(stimulus))
            if expectedMessages == True:
                if messages:
                    messages = True

            if expectedResult:
                assert close(result, expectedResult), stimulus
            if expectedFormattedResult:
                assert calc.format((result, units)) == expectedFormattedResult, stimulus
            if expectedUnits:
                assert units == expectedUnits, stimulus
            assert not expectedError

            assert messages == expectedMessages, stimulus
            assert warnings == expectedWarnings, stimulus
        except CalculatorError as e:
            calc.restoreStack()
            assert expectedError == e.getMessage(), stimulus


# main {{{1
if __name__ == '__main__':
    # As a debugging aid allow the tests to be run on their own, outside pytest.
    # This makes it easier to see and interpret and textual output.

    defined = dict(globals())
    for k, v in defined.items():
        if callable(v) and k.startswith('test_'):
            print()
            print('Calling:', k)
            print((len(k)+9)*'=')
            v()
