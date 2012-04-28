#!/usr/bin/env python

# Test PyCalc
# Imports {{{1
from runtests import cmdLineOpts, writeSummary
from textcolors import Colors
from ec import Calculator, Actions, Display
import math

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
    ('1 1 +', 1+1, '', '2')
  , ('2 2 *', 2*2, '', '4')
  , ('25MHz 2pi * "rads/s"', 2*25e6*math.pi, 'rads/s', '157.08 Mrads/s')
  , ('1 2 /', 0.5, '', '500m')
  , ('5 2 //', 2, '', '2')
  , ('5 2 %', 1, '', '1')
  , ('10 10.5 %chg', 5, '', '5')
  , ('4 recip', 0.25, '', '250m')
  , ('6 !', 720, '', '720')
  , ('10 exp ln', 10, '', '10')
  , ('10 pow10 log', 10, '', '10')
  , ('500 2 ** sci', 500**2, '', '2.5000e+05')
  , ("3.5 chs ceil", -3, '', "-3")
  , ("3.5 chs floor", -4, '', "-4")
  , ('100 100 ||', 50, '', '50')
  , ('2 sqrt sqr', 2.0, '', '2')
  , ("0x1f 0x01 +", 32, '', '32')
  , ("'h1f 'h01 +", 32, '', '32')
  , ("'d10 'd01 +", 11, '', '11')
  , ("010 001 +", 9, '', '9')
  , ("'o10 'o01 +", 9, '', '9')
  , ("'b10 'b01 +", 3, '', '3')
  , ('2pi eng7', 2*math.pi, 'rads', '6.2831853 rads')
  , ("'h1f 'h01 + hex", 32, '', "0x0020")
  , ("'h1f 'h01 + vhex", 32, '', "'h0020")
  , ("90 sin", 1, '', "1")
  , ("rads pi 2 / sin", 1, '', "1")
  , ("degs 90 sin", 1, '', "1")
  , ("degs 90 sin asin", 90, 'degs', "90 degs")
  , ("180 cos", -1, '', "-1")
  , ("rads pi cos", -1, '', "-1")
  , ("degs 180 cos", -1, '', "-1")
  , ("degs 180 cos acos", 180, 'degs', "180 degs")
  , ("45 tan", math.tan(math.pi/4), '', "1")
  , ("rads pi 4 / tan", math.tan(math.pi/4), '', "1")
  , ("degs 45 tan", math.tan(math.pi/4), '', "1")
  , ("degs 45 tan atan", 45, 'degs', "45 degs")
  , ("0 1 degs atan2", 0, 'degs', "0 degs")
  , ("1 0 degs atan2", 90, 'degs', "90 degs")
  , ("0 -1 degs atan2", 180, 'degs', "180 degs")
  , ("-1 0 degs atan2", -90, 'degs', "-90 degs")
  , ("-1 -1 degs atan2", -135, 'degs', "-135 degs")
  , ("3 4 hypot", 5, '', "5")
  , ("3 4 rtop", 5, '', "5")
  , ("4 4 degs rtop swap", 45, 'degs', "45 degs")
  , ("4 4 rads rtop swap 4 *", math.pi, '', "3.1416")
  , ("45 2 sqrt degs ptor", 1, '', "1")
  , ("45 2 sqrt degs ptor swap", 1, '', "1")
  , ("pi 4/ 2 sqrt rads ptor", 1, '', "1")
  , ("pi 4/ 2 sqrt rads ptor swap", 1, '', "1")
  , ("4 4 degs rtop swap", 45, 'degs', "45 degs")
  , ("4 4 rads rtop swap", math.pi/4, 'rads', "785.4 mrads")
  , ("1 sinh", math.sinh(1), '', "1.1752")
  , ("1 sinh asinh", 1, '', "1")
  , ("1 cosh", math.cosh(1), '', "1.5431")
  , ("1 cosh acosh", 1, '', "1")
  , ("1 tanh", math.tanh(1), '', "761.59m")
  , ("1 tanh atanh", 1, '', "1")
  , ("'hABCDEF hex", 11259375, '', "0xabcdef")
  , ("'hABCDEF vhex", 11259375, '', "'habcdef")
  , ("'d1234567890 vdec", 1234567890, '', "'d1234567890")
  , ("012345670 oct", 2739128, '', "012345670")
  , ("'o12345670 voct", 2739128, '', "'o12345670")
  , ("rt2 sci4", math.sqrt(2), '', "1.4142e+00")
  , ("h sci4", 6.6260693e-34, 'J-s', "6.6261e-34")
  , ("k sci4", 1.3806505e-23, 'J/K', "1.3807e-23")
  , ("q sci4", 1.60217653e-19, 'Coul', "1.6022e-19")
  , ("c sci4", 2.99792458e8, 'm/s', "2.9979e+08")
#  , ("G sci4", 6.6746e-11, '', "6.6746e-11")
  , ("0C sci4", 273.15, 'K', "2.7315e+02")
  , ("eps0 sci4", 8.854187817e-12, 'F/m', "8.8542e-12")
  , ("mu0 sci4", 4e-7*math.pi, 'N/A^2', "1.2566e-06")
  , ("100 db", 40, '', "40")
  , ("100 db adb", 100, '', "100")
  , ("100 db10", 20, '', "20")
  , ("100 db10 adb10", 100, '', "100")
  , ("1MHz =freq 10us =time 2pi * * time freq *", 10, '', "10")
  , ("2.437GHz", 2.437e9, 'Hz', "2.437 GHz")
  , ("1e+6 =freq 10e-6 =time 2pi * * time freq *", 10, '', "10")
  , ("2.437e9", 2.437e9, '', "2.437G")
  , ("1 vdbm", 10, '', "10")
  , ("10 dbmv", 1, 'V', "1 V")
  , ("0.1 vdbm", -10, '', "-10")
  , ("-10 dbmv", 0.1, 'V', "100 mV")
  , ("20m idbm", 10, '', "10")
  , ("10 dbmi", 0.02, 'A', "20 mA")
  , ("2m idbm", -10, '', "-10")
  , ("-10 dbmi", 0.002, 'A', "2 mA")
  , ("16 log2", 4, '', "4")
  , ("0.25 log2", -2, '', "-2")
  , ("1MHz 2pF swap", 1e6, 'Hz', "1 MHz")
  , ("1MHz 2pF pop", 1e6, 'Hz', "1 MHz")
  , ("1MHz dup 2pF swap pop pop", 1e6, 'Hz', "1 MHz")
  , ("4 j * sqrt", math.sqrt(2) + 1j*math.sqrt(2), '', "1.4142 + j1.4142")
  , ("1pF =c pop c", 1e-12, 'F', "1 pF")
  , ("1 j+ 'V' mag", math.sqrt(2), 'V', "1.4142 V")
  , ("1 j+ 'V' mag pop", 1 + 1j, 'V', "1 V + j1 V")
  , ("1 j+ 'V' ph", 45, 'degs', "45 degs")
  , ("1 j+ 'V' ph pop", 1 + 1j, 'V', "1 V + j1 V")
]

# Run tests {{{1
calc = Calculator(Actions, Display('eng', 4), warnings=False)
for index, case in enumerate(testCases):
    testsRun += 1
    stimulus = case[0]
    expectedResult = case[1]
    expectedUnits = case[2]
    expectedFormattedResult = case[3]
    if printTests:
        print status('Trying %d:' % index), stimulus

    calc.clear()
    result, units = calc.evaluate(calc.split(stimulus))
    error = abs(result - expectedResult)
    failure = (
        error > (reltol*abs(expectedResult) + abstol) or
        calc.format((result, units)) != expectedFormattedResult or
        units != expectedUnits
    )
    if failure:
        failures += 1
        print fail('Failure detected (%s):' % failures)
        print info('    Given:'), stimulus
        print info('    Result  :'), result, calc.format((result, units)), units
        print info('    Expected:'), expectedResult, expectedFormattedResult, expectedUnits
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
exit(0 if testsRun == numTests else 0)
