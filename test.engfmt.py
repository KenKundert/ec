#!/usr/bin/env python

# Imports {{{1
import sys
from engfmt import (
    fromEngFmt, toEngFmt
  , toNumber, isNumber, stripUnits
  , allToEngFmt, allFromEngFmt
)
from runtests import cmdLineOpts, writeSummary
from textcolors import Colors

# Initialization {{{1
fast, printSummary, printTests, printResults, colorize, parent = cmdLineOpts()
testsRun = 0
failures = 0
colors = Colors(colorize)
succeed = colors.colorizer('green')
fail = colors.colorizer('red')
info = colors.colorizer('magenta')
status = colors.colorizer('cyan')

# Test cases {{{1
testCases = [
    (   '1ns'           # input
      , '1e-9'          # fromEngFmt() result with units stripped
      , ('1e-9', 's')   # fromEngFmt() result without units stripped
      , '1ns'           # toNumber() -> toEngFmt() result
      , '1n'            # stripUnits() result
      , True            # isNumber() result
    ),
    (   '10ns'          # input
      , '10e-9'         # fromEngFmt() result with units stripped
      , ('10e-9', 's')  # fromEngFmt() result without units stripped
      , '10ns'          # toNumber() -> toEngFmt() result
      , '10n'           # stripUnits() result
      , True            # isNumber() result
    ),
    (   '100ns'         # input
      , '100e-9'        # fromEngFmt() result with units stripped
      , ('100e-9', 's') # fromEngFmt() result without units stripped
      , '100ns'         # toNumber() -> toEngFmt() result
      , '100n'          # stripUnits() result
      , True            # isNumber() result
    ),
    (   '1MHz'          # input
      , '1e6'           # fromEngFmt() result with units stripped
      , ('1e6', 'Hz')   # fromEngFmt() result without units stripped
      , '1MHz'          # toNumber() -> toEngFmt() result
      , '1M'            # stripUnits() result
      , True            # isNumber() result
    ),
    (   '10MHz'         # input
      , '10e6'          # fromEngFmt() result with units stripped
      , ('10e6', 'Hz')  # fromEngFmt() result without units stripped
      , '10MHz'         # toNumber() -> toEngFmt() result
      , '10M'           # stripUnits() result
      , True            # isNumber() result
    ),
    (   '100MHz'        # input
      , '100e6'         # fromEngFmt() result with units stripped
      , ('100e6', 'Hz') # fromEngFmt() result without units stripped
      , '100MHz'        # toNumber() -> toEngFmt() result
      , '100M'          # stripUnits() result
      , True            # isNumber() result
    ),
    (   '$10K'          # input
      , '10e3'          # fromEngFmt() result with units stripped
      , ('10e3', '$')   # fromEngFmt() result without units stripped
      , '$10K'          # toNumber() -> toEngFmt() result
      , '10K'           # stripUnits() result
      , True            # isNumber() result
    ),
    (   '$10'           # input
      , '10'            # fromEngFmt() result with units stripped
      , ('10', '$')     # fromEngFmt() result without units stripped
      , '$10'           # toNumber() -> toEngFmt() result
      , '10'            # stripUnits() result
      , True            # isNumber() result
    ),
    (   '$10e9'         # input
      , '10e9'          # fromEngFmt() result with units stripped
      , ('10e9', '$')   # fromEngFmt() result without units stripped
      , '$10G'          # toNumber() -> toEngFmt() result
      , '10e9'          # stripUnits() result
      , True            # isNumber() result
    ),
    (   '$0.01'         # input
      , '0.01'          # fromEngFmt() result with units stripped
      , ('0.01', '$')   # fromEngFmt() result without units stripped
      , '$10m'          # toNumber() -> toEngFmt() result
      , '0.01'          # stripUnits() result
      , True            # isNumber() result
    ),
    (   '1.0ns'         # input
      , '1.0e-9'        # fromEngFmt() result with units stripped
      , ('1.0e-9', 's') # fromEngFmt() result without units stripped
      , '1ns'           # toNumber() -> toEngFmt() result
      , '1.0n'          # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+1.034e-029'   # input
      , '+1.034e-029'   # fromEngFmt() result with units stripped
      , ('+1.034e-029', '') # fromEngFmt() result without units stripped
      , '10.34e-30'     # toNumber() -> toEngFmt() result
      , '+1.034e-029'   # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+10.34e-029'   # input
      , '+10.34e-029'   # fromEngFmt() result with units stripped
      , ('+10.34e-029', '') # fromEngFmt() result without units stripped
      , '103.4e-30'     # toNumber() -> toEngFmt() result
      , '+10.34e-029'   # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+103.4e-029'   # input
      , '+103.4e-029'   # fromEngFmt() result with units stripped
      , ('+103.4e-029', '') # fromEngFmt() result without units stripped
      , '1.034e-27'     # toNumber() -> toEngFmt() result
      , '+103.4e-029'   # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+1.034e+029'   # input
      , '+1.034e+029'   # fromEngFmt() result with units stripped
      , ('+1.034e+029', '') # fromEngFmt() result without units stripped
      , '103.4e27'      # toNumber() -> toEngFmt() result
      , '+1.034e+029'   # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+10.34e+029'   # input
      , '+10.34e+029'   # fromEngFmt() result with units stripped
      , ('+10.34e+029', '') # fromEngFmt() result without units stripped
      , '1.034e30'      # toNumber() -> toEngFmt() result
      , '+10.34e+029'   # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+103.4e+029'   # input
      , '+103.4e+029'   # fromEngFmt() result with units stripped
      , ('+103.4e+029', '') # fromEngFmt() result without units stripped
      , '10.34e30'      # toNumber() -> toEngFmt() result
      , '+103.4e+029'   # stripUnits() result
      , True            # isNumber() result
    ),
    (   '.10ns'         # input
      , '.10e-9'        # fromEngFmt() result with units stripped
      , ('.10e-9', 's') # fromEngFmt() result without units stripped
      , '100ps'         # toNumber() -> toEngFmt() result
      , '.10n'          # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+10ns'         # input
      , '+10e-9'        # fromEngFmt() result with units stripped
      , ('+10e-9', 's') # fromEngFmt() result without units stripped
      , '10ns'          # toNumber() -> toEngFmt() result
      , '+10n'          # stripUnits() result
      , True            # isNumber() result
    ),
    (   '10_s'          # input
      , '10'            # fromEngFmt() result with units stripped
      , ('10', 's')     # fromEngFmt() result without units stripped
      , '10s'           # toNumber() -> toEngFmt() result
      , '10'            # stripUnits() result
      , True            # isNumber() result
    ),
    (   '10s'
      , None            # fromEngFmt() result with units stripped
      , None            # fromEngFmt() result without units stripped
      , None            # toNumber() -> toEngFmt() result
      , None            # stripUnits() result
      , False           # isNumber() result
    ),
    (   '10n'           # input
      , '10e-9'         # fromEngFmt() result with units stripped
      , ('10e-9', '')   # fromEngFmt() result without units stripped
      , '10n'           # toNumber() -> toEngFmt() result
      , '10n'           # stripUnits() result
      , True            # isNumber() result
    ),
    (   '10'            # input
      , '10'            # fromEngFmt() result with units stripped
      , ('10', None)    # fromEngFmt() result without units stripped
      , '10'            # toNumber() -> toEngFmt() result
      , '10'            # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+1.034e-029Hz' # input
      , '+1.034e-029'   # fromEngFmt() result with units stripped
      , ('+1.034e-029', 'Hz')   # fromEngFmt() result without units stripped
      , '10.34e-30Hz'   # toNumber() -> toEngFmt() result
      , '+1.034e-029'   # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+10.34e-029Hz' # input
      , '+10.34e-029'   # fromEngFmt() result with units stripped
      , ('+10.34e-029', 'Hz')   # fromEngFmt() result without units stripped
      , '103.4e-30Hz'   # toNumber() -> toEngFmt() result
      , '+10.34e-029'   # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+103.4e-029Hz' # input
      , '+103.4e-029'   # fromEngFmt() result with units stripped
      , ('+103.4e-029', 'Hz')   # fromEngFmt() result without units stripped
      , '1.034e-27Hz'   # toNumber() -> toEngFmt() result
      , '+103.4e-029'   # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+1.034e+029Hz' # input
      , '+1.034e+029'   # fromEngFmt() result with units stripped
      , ('+1.034e+029', 'Hz')   # fromEngFmt() result without units stripped
      , '103.4e27Hz'    # toNumber() -> toEngFmt() result
      , '+1.034e+029'   # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+10.34e+029Hz' # input
      , '+10.34e+029'   # fromEngFmt() result with units stripped
      , ('+10.34e+029', 'Hz')   # fromEngFmt() result without units stripped
      , '1.034e30Hz'    # toNumber() -> toEngFmt() result
      , '+10.34e+029'   # stripUnits() result
      , True            # isNumber() result
    ),
    (   '+103.4e+029Hz' # input
      , '+103.4e+029'   # fromEngFmt() result with units stripped
      , ('+103.4e+029', 'Hz')   # fromEngFmt() result without units stripped
      , '10.34e30Hz'    # toNumber() -> toEngFmt() result
      , '+103.4e+029'   # stripUnits() result
      , True            # isNumber() result
    ),
    (   'inf'           # input
      , 'inf'           # fromEngFmt() result with units stripped
      , ('inf', '')     # fromEngFmt() result without units stripped
      , 'inf'           # toNumber() -> toEngFmt() result
      , 'inf'           # stripUnits() result
      , True            # isNumber() result
    ),
    (   'inf Hz'        # input
      , 'inf'           # fromEngFmt() result with units stripped
      , ('inf', 'Hz')   # fromEngFmt() result without units stripped
      , 'inf Hz'        # toNumber() -> toEngFmt() result
      , 'inf'           # stripUnits() result
      , True            # isNumber() result
    ),
    (   '$inf'          # input
      , 'inf'           # fromEngFmt() result with units stripped
      , ('inf', '$')    # fromEngFmt() result without units stripped
      , '$inf'          # toNumber() -> toEngFmt() result
      , 'inf'           # stripUnits() result
      , True            # isNumber() result
    ),
    (   '-inf'          # input
      , '-inf'          # fromEngFmt() result with units stripped
      , ('-inf', '')    # fromEngFmt() result without units stripped
      , '-inf'          # toNumber() -> toEngFmt() result
      , '-inf'          # stripUnits() result
      , True            # isNumber() result
    ),
    (   '-inf Hz'       # input
      , '-inf'          # fromEngFmt() result with units stripped
      , ('-inf', 'Hz')  # fromEngFmt() result without units stripped
      , '-inf Hz'       # toNumber() -> toEngFmt() result
      , '-inf'          # stripUnits() result
      , True            # isNumber() result
    ),
    (   '$-inf'         # input
      , '-inf'          # fromEngFmt() result with units stripped
      , ('-inf', '$')   # fromEngFmt() result without units stripped
      , '$-inf'         # toNumber() -> toEngFmt() result
      , '-inf'          # stripUnits() result
      , True            # isNumber() result
    ),
    (   'nan'           # input
      , 'nan'           # fromEngFmt() result with units stripped
      , ('nan', '')     # fromEngFmt() result without units stripped
      , 'nan'           # toNumber() -> toEngFmt() result
      , 'nan'           # stripUnits() result
      , True            # isNumber() result
    ),
    (   'nan Hz'        # input
      , 'nan'           # fromEngFmt() result with units stripped
      , ('nan', 'Hz')   # fromEngFmt() result without units stripped
      , 'nan Hz'        # toNumber() -> toEngFmt() result
      , 'nan'           # stripUnits() result
      , True            # isNumber() result
    ),
    (   '$nan'          # input
      , 'nan'           # fromEngFmt() result with units stripped
      , ('nan', '$')    # fromEngFmt() result without units stripped
      , '$nan'          # toNumber() -> toEngFmt() result
      , 'nan'           # stripUnits() result
      , True            # isNumber() result
    ),
    (   'spam'
      , None            # fromEngFmt() result with units stripped
      , None            # fromEngFmt() result without units stripped
      , None            # toNumber() -> toEngFmt() result
      , None            # stripUnits() result
      , False           # isNumber() result
    )
]

toEngTestCases = [
    (   'Pass @ 2.0000e-04s: supply current: 0.000e+00A < 2.500e-05A < 1.000e-03A.'
      , 'Pass @ 200us: supply current: 0A < 25uA < 1mA.'
    )
  , (   "1e-3Z @ .2.0000e-04s: supply current: foo0.000e+00A < 'h4e5 < foo+1.000e-03A."
      , "1mZ @ .2.0000e-04s: supply current: foo0.000e+00A < 'h4e5 < foo+1mA."
    )
]

fromEngTestCases = [
    (   'Pass @ 200us: supply current: 0A < 25uA < 1mA.'
      , 'Pass @ 200e-6s: supply current: 0A < 25e-6A < 1e-3A.'
    )
  , (   '1E2, 1E-2, 1E+2. +1.034e-029Hz, 1mA'
      , '1E2, 1E-2, 1E+2. +1.034e-029Hz, 1e-3A'
    )
]

# Run tests {{{1
for index, case in enumerate(testCases):
    stimulus = case[0]
    expectedResultWithoutUnits = case[1]
    expectedResultWithUnits = case[2]
    expectedResult = case[3]
    expectedResultUnitsStripped = case[4]
    expectedResultIsNumber = case[5]
    testsRun += 4
    if printTests:
        print status('Trying %d:' % index), stimulus

    resultWithoutUnits = fromEngFmt(stimulus, stripUnits=True)
    if resultWithoutUnits != expectedResultWithoutUnits:
        failures += 1
        print fail('Failure detected in fromEngFmt(stripUnits) (%s):' % failures)
        print info('    Given:'), stimulus
        print info('    Result  :'), resultWithoutUnits
        print info('    Expected:'), expectedResultWithoutUnits
    elif printResults:
        print succeed('    From engineering format result (without units):'), resultWithoutUnits

    resultWithUnits = fromEngFmt(stimulus, stripUnits=False)
    if resultWithUnits != expectedResultWithUnits:
        failures += 1
        print fail('Failure detected in fromEngFmt (%s):' % failures)
        print info('    Given:'), stimulus
        print info('    Result  :'), resultWithUnits
        print info('    Expected:'), expectedResultWithUnits
    elif printResults:
        print succeed('    From engineering format result (with units):'), resultWithUnits

    result = toNumber(stimulus)
    if result != None:
        (number, units) = result
        result = toEngFmt(number, units)
    if result != expectedResult:
        failures += 1
        print fail('Failure detected in toNumber (%s):' % failures)
        print info('    Given:'), stimulus
        print info('    Result  :'), result
        print info('    Expected:'), expectedResult
    elif printResults:
        print succeed('    From and to engineering format result::'), result

    result = stripUnits(stimulus)
    if result != expectedResultUnitsStripped:
        failures += 1
        print fail('Failure detected in stripUnits (%s):' % failures)
        print info('    Given:'), stimulus
        print info('    Result  :'), result
        print info('    Expected:'), expectedResultUnitsStripped
    elif printResults:
        print succeed('    Strip Units Result:'), result

    result = isNumber(stimulus)
    if result != expectedResultIsNumber:
        failures += 1
        print fail('Failure detected in isNumber (%s):' % failures)
        print info('    Given:'), stimulus
        print info('    Result  :'), result
        print info('    Expected:'), expectedResultIsNumber
    elif printResults:
        print succeed('    Is Number Result:'), result

for index, case in enumerate(toEngTestCases):
    stimulus = case[0]
    expectedResult = case[1]
    testsRun += 1
    if printTests:
        print status('Trying allToEngFmt %d:' % index), stimulus

    result = allToEngFmt(stimulus)
    if result != expectedResult:
        failures += 1
        print fail('Failure detected in allToEngFmt() (%s):' % failures)
        print info('    Given:'), stimulus
        print info('    Result  :'), result
        print info('    Expected:'), expectedResult
    elif printResults:
        print succeed('    Result:'), result

for index, case in enumerate(fromEngTestCases):
    stimulus = case[0]
    expectedResult = case[1]
    testsRun += 1
    if printTests:
        print status('Trying allFromEngFmt %d:' % index), stimulus

    result = allFromEngFmt(stimulus)
    if result != expectedResult:
        failures += 1
        print fail('Failure detected in allToEngFmt() (%s):' % failures)
        print info('    Given:'), stimulus
        print info('    Result  :'), result
        print info('    Expected:'), expectedResult
    elif printResults:
        print succeed('    Result:'), result

# Print summary {{{1
assert testsRun == (
    len(testCases)*4  # each case represents 4 tests
  + len(toEngTestCases)
  + len(fromEngTestCases)
)
if printSummary:
    if failures:
        print fail('FAIL:'),
    else:
        print succeed('PASS:'),
    print '%s tests run, %s failures detected.' % (testsRun, failures)

writeSummary(testsRun, failures)
exit(bool(failures))
