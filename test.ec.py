#!/usr/bin/env python

# Test EC
# Imports {{{1
from runtests import cmdLineOpts, writeSummary
from textcolors import Colors
from ec import Calculator, actions, Display, CalculatorError
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
    {   'stimulus': '1 1 +'
      , 'value': 1+1
      , 'units': ''
      , 'text': '2'
    }
  , {   'stimulus': '2 2 *'
      , 'value': 2*2
      , 'units': ''
      , 'text': '4'
    }
  , {   'stimulus': "25MHz 2pi * 'rads/s'"
      , 'value': 2*25e6*math.pi
      , 'units': 'rads/s'
      , 'text': '157.08 Mrads/s'
    }
  , {   'stimulus': '1 2 /'
      , 'value': 0.5
      , 'units': ''
      , 'text': '500m'
    }
  , {   'stimulus': '5 2 //'
      , 'value': 2
      , 'units': ''
      , 'text': '2'
    }
  , {   'stimulus': '5 2 %'
      , 'value': 1
      , 'units': ''
      , 'text': '1'
    }
  , {   'stimulus': '10 10.5 %chg'
      , 'value': 5
      , 'units': ''
      , 'text': '5'
    }
  , {   'stimulus': '4 recip'
      , 'value': 0.25
      , 'units': ''
      , 'text': '250m'
    }
  , {   'stimulus': '6 !'
      , 'value': 720
      , 'units': ''
      , 'text': '720'
    }
  , {   'stimulus': '10 exp ln'
      , 'value': 10
      , 'units': ''
      , 'text': '10'
    }
  , {   'stimulus': '10 pow10 log'
      , 'value': 10
      , 'units': ''
      , 'text': '10'
    }
  , {   'stimulus': '500 2 ** sci'
      , 'value': 500**2
      , 'units': ''
      , 'text': '2.5000e+05'
    }
  , {   'stimulus': "3.5 chs ceil"
      , 'value': -3
      , 'units': ''
      , 'text': "-3"
    }
  , {   'stimulus': "3.5 chs floor"
      , 'value': -4
      , 'units': ''
      , 'text': "-4"
    }
  , {   'stimulus': '100 100 ||'
      , 'value': 50
      , 'units': ''
      , 'text': '50'
    }
  , {   'stimulus': '2 sqrt sqr'
      , 'value': 2.0
      , 'units': ''
      , 'text': '2'
    }
  , {   'stimulus': "0x1f 0x01 +"
      , 'value': 32
      , 'units': ''
      , 'text': '32'
    }
#  , {   'stimulus': "'h1f 'h01 +"
#      , 'value': 32
#      , 'units': ''
#      , 'text': '32'
#    }
#  , {   'stimulus': "'d10 'd01 +"
#      , 'value': 11
#      , 'units': ''
#      , 'text': '11'
#    }
  , {   'stimulus': "010 001 +"
      , 'value': 9
      , 'units': ''
      , 'text': '9'
    }
#  , {   'stimulus': "'o10 'o01 +"
#      , 'value': 9
#      , 'units': ''
#      , 'text': '9'
#    }
#  , {   'stimulus': "'b10 'b01 +"
#      , 'value': 3
#      , 'units': ''
#      , 'text': '3'
#    }
  , {   'stimulus': '2pi eng7'
      , 'value': 2*math.pi
      , 'units': 'rads'
      , 'text': '6.2831853 rads'
    }
#  , {   'stimulus': "'h1f 'h01 + hex"
#      , 'value': 32
#      , 'units': ''
#      , 'text': "0x0020"
#    }
#  , {   'stimulus': "'h1f 'h01 + vhex"
#      , 'value': 32
#      , 'units': ''
#      , 'text': "'h0020"
#    }
  , {   'stimulus': "90 sin"
      , 'value': 1
      , 'units': ''
      , 'text': "1"
    }
  , {   'stimulus': "rads pi 2 / sin"
      , 'value': 1
      , 'units': ''
      , 'text': "1"
    }
  , {   'stimulus': "degs 90 sin"
      , 'value': 1
      , 'units': ''
      , 'text': "1"
    }
  , {   'stimulus': "degs 90 sin asin"
      , 'value': 90
      , 'units': 'degs'
      , 'text': "90 degs"
    }
  , {   'stimulus': "180 cos"
      , 'value': -1
      , 'units': ''
      , 'text': "-1"
    }
  , {   'stimulus': "rads pi cos"
      , 'value': -1
      , 'units': ''
      , 'text': "-1"
    }
  , {   'stimulus': "degs 180 cos"
      , 'value': -1
      , 'units': ''
      , 'text': "-1"
    }
  , {   'stimulus': "degs 180 cos acos"
      , 'value': 180
      , 'units': 'degs'
      , 'text': "180 degs"
    }
  , {   'stimulus': "45 tan"
      , 'value': math.tan(math.pi/4)
      , 'units': ''
      , 'text': "1"
    }
  , {   'stimulus': "rads pi 4 / tan"
      , 'value': math.tan(math.pi/4)
      , 'units': ''
      , 'text': "1"
    }
  , {   'stimulus': "degs 45 tan"
      , 'value': math.tan(math.pi/4)
      , 'units': ''
      , 'text': "1"
    }
  , {   'stimulus': "degs 45 tan atan"
      , 'value': 45
      , 'units': 'degs'
      , 'text': "45 degs"
    }
  , {   'stimulus': "0 1 degs atan2"
      , 'value': 0
      , 'units': 'degs'
      , 'text': "0 degs"
    }
  , {   'stimulus': "1 0 degs atan2"
      , 'value': 90
      , 'units': 'degs'
      , 'text': "90 degs"
    }
  , {   'stimulus': "0 -1 degs atan2"
      , 'value': 180
      , 'units': 'degs'
      , 'text': "180 degs"
    }
  , {   'stimulus': "-1 0 degs atan2"
      , 'value': -90
      , 'units': 'degs'
      , 'text': "-90 degs"
    }
  , {   'stimulus': "-1 -1 degs atan2"
      , 'value': -135
      , 'units': 'degs'
      , 'text': "-135 degs"
    }
  , {   'stimulus': "3 4 hypot"
      , 'value': 5
      , 'units': ''
      , 'text': "5"
    }
  , {   'stimulus': "3 4 rtop"
      , 'value': 5
      , 'units': ''
      , 'text': "5"
    }
  , {   'stimulus': "4 4 degs rtop swap"
      , 'value': 45
      , 'units': 'degs'
      , 'text': "45 degs"
    }
  , {   'stimulus': "4 4 rads rtop swap 4 *"
      , 'value': math.pi
      , 'units': ''
      , 'text': "3.1416"
    }
  , {   'stimulus': "45 2 sqrt degs ptor"
      , 'value': 1
      , 'units': ''
      , 'text': "1"
    }
  , {   'stimulus': "45 2 sqrt degs ptor swap"
      , 'value': 1
      , 'units': ''
      , 'text': "1"
    }
  , {   'stimulus': "pi 4/ 2 sqrt rads ptor"
      , 'value': 1
      , 'units': ''
      , 'text': "1"
    }
  , {   'stimulus': "pi 4/ 2 sqrt rads ptor swap"
      , 'value': 1
      , 'units': ''
      , 'text': "1"
    }
  , {   'stimulus': "4 4 degs rtop swap"
      , 'value': 45
      , 'units': 'degs'
      , 'text': "45 degs"
    }
  , {   'stimulus': "4 4 rads rtop swap"
      , 'value': math.pi/4
      , 'units': 'rads'
      , 'text': "785.4 mrads"
    }
  , {   'stimulus': "1 sinh"
      , 'value': math.sinh(1)
      , 'units': ''
      , 'text': "1.1752"
    }
  , {   'stimulus': "1 sinh asinh"
      , 'value': 1
      , 'units': ''
      , 'text': "1"
    }
  , {   'stimulus': "1 cosh"
      , 'value': math.cosh(1)
      , 'units': ''
      , 'text': "1.5431"
    }
  , {   'stimulus': "1 cosh acosh"
      , 'value': 1
      , 'units': ''
      , 'text': "1"
    }
  , {   'stimulus': "1 tanh"
      , 'value': math.tanh(1)
      , 'units': ''
      , 'text': "761.59m"
    }
  , {   'stimulus': "1 tanh atanh"
      , 'value': 1
      , 'units': ''
      , 'text': "1"
    }
#  , {   'stimulus': "'hABCDEF hex"
#      , 'value': 11259375
#      , 'units': ''
#      , 'text': "0xabcdef"
#    }
#  , {   'stimulus': "'hABCDEF vhex"
#      , 'value': 11259375
#      , 'units': ''
#      , 'text': "'habcdef"
#    }
#  , {   'stimulus': "'d1234567890 vdec"
#      , 'value': 1234567890
#      , 'units': ''
#      , 'text': "'d1234567890"
#    }
  , {   'stimulus': "012345670 oct"
      , 'value': 2739128
      , 'units': ''
      , 'text': "012345670"
    }
#  , {   'stimulus': "'o12345670 voct"
#      , 'value': 2739128
#      , 'units': ''
#      , 'text': "'o12345670"
#    }
  , {   'stimulus': "rt2 sci4"
      , 'value': math.sqrt(2)
      , 'units': ''
      , 'text': "1.4142e+00"
    }
  , {   'stimulus': "h sci4"
      , 'value': 6.6260693e-34
      , 'units': 'J-s'
      , 'text': "6.6261e-34"
    }
  , {   'stimulus': "k sci4"
      , 'value': 1.3806488e-23
      , 'units': 'J/K'
      , 'text': "1.3806e-23"
    }
  , {   'stimulus': "q sci4"
      , 'value': 1.602176565e-19
      , 'units': 'C'
      , 'text': "1.6022e-19"
    }
  , {   'stimulus': "c sci4"
      , 'value': 2.99792458e8
      , 'units': 'm/s'
      , 'text': "2.9979e+08"
    }
#  , {   'stimulus': "G sci4"
#      , 'value': 6.6746e-11
#      , 'units': ''
#      , 'text': "6.6746e-11"
#    }
  , {   'stimulus': "0C sci4"
      , 'value': 273.15
      , 'units': 'K'
      , 'text': "2.7315e+02"
    }
  , {   'stimulus': "eps0 sci4"
      , 'value': 8.854187817e-12
      , 'units': 'F/m'
      , 'text': "8.8542e-12"
    }
  , {   'stimulus': "mu0 sci4"
      , 'value': 4e-7*math.pi
      , 'units': 'N/A^2'
      , 'text': "1.2566e-06"
    }
  , {   'stimulus': "100 db"
      , 'value': 40
      , 'units': ''
      , 'text': "40"
    }
  , {   'stimulus': "100 db adb"
      , 'value': 100
      , 'units': ''
      , 'text': "100"
    }
  , {   'stimulus': "100 db10"
      , 'value': 20
      , 'units': ''
      , 'text': "20"
    }
  , {   'stimulus': "100 db10 adb10"
      , 'value': 100
      , 'units': ''
      , 'text': "100"
    }
  , {   'stimulus': "1MHz =freq 10us =time 2pi * * time freq *"
      , 'value': 10
      , 'units': ''
      , 'text': "10"
    }
  , {   'stimulus': "2.437GHz 100MHz+"
      , 'value': 2.537e9
      , 'units': 'Hz'
      , 'text': "2.537 GHz"
    }
  , {   'stimulus': '$1000 $843-'
      , 'value': 157
      , 'units': '$'
      , 'text': '$157'
    }
  , {   'stimulus': "1.52e-11F"
      , 'value': 1.52e-11
      , 'units': 'F'
      , 'text': "15.2 pF"
    }
  , {   'stimulus': "1e+6 =freq 10e-6 =time 2pi * * time freq *"
      , 'value': 10
      , 'units': ''
      , 'text': "10"
    }
  , {   'stimulus': "2.437e9"
      , 'value': 2.437e9
      , 'units': ''
      , 'text': "2.437G"
    }
  , {   'stimulus': "1 vdbm"
      , 'value': 10
      , 'units': ''
      , 'text': "10"
    }
  , {   'stimulus': "10 dbmv"
      , 'value': 1
      , 'units': 'V'
      , 'text': "1 V"
    }
  , {   'stimulus': "0.1 vdbm"
      , 'value': -10
      , 'units': ''
      , 'text': "-10"
    }
  , {   'stimulus': "-10 dbmv"
      , 'value': 0.1
      , 'units': 'V'
      , 'text': "100 mV"
    }
  , {   'stimulus': "20m idbm"
      , 'value': 10
      , 'units': ''
      , 'text': "10"
    }
  , {   'stimulus': "10 dbmi"
      , 'value': 0.02
      , 'units': 'A'
      , 'text': "20 mA"
    }
  , {   'stimulus': "2m idbm"
      , 'value': -10
      , 'units': ''
      , 'text': "-10"
    }
  , {   'stimulus': "-10 dbmi"
      , 'value': 0.002
      , 'units': 'A'
      , 'text': "2 mA"
    }
  , {   'stimulus': "16 log2"
      , 'value': 4
      , 'units': ''
      , 'text': "4"
    }
  , {   'stimulus': "0.25 log2"
      , 'value': -2
      , 'units': ''
      , 'text': "-2"
    }
  , {   'stimulus': "1MHz 2pF swap"
      , 'value': 1e6
      , 'units': 'Hz'
      , 'text': "1 MHz"
    }
  , {   'stimulus': "1MHz 2pF pop"
      , 'value': 1e6
      , 'units': 'Hz'
      , 'text': "1 MHz"
    }
  , {   'stimulus': "1MHz dup 2pF swap pop pop"
      , 'value': 1e6
      , 'units': 'Hz'
      , 'text': "1 MHz"
    }
  , {   'stimulus': "4 j * sqrt"
      , 'value': math.sqrt(2) + 1j*math.sqrt(2)
      , 'units': ''
      , 'text': "1.4142 + j1.4142"
    }
  , {   'stimulus': "1pF =c pop c"
      , 'value': 1e-12
      , 'units': 'F'
      , 'text': "1 pF"
      , 'warnings': ['c: variable has overridden built-in.']
    }
  , {   'stimulus': "1 j+ 'V' mag"
      , 'value': math.sqrt(2)
      , 'units': 'V'
      , 'text': "1.4142 V"
    }
  , {   'stimulus': "1 j+ 'V' mag pop"
      , 'value': 1 + 1j
      , 'units': 'V'
      , 'text': "1 V + j1 V"
    }
  , {   'stimulus': "1 j+ 'V' ph"
      , 'value': 45
      , 'units': 'degs'
      , 'text': "45 degs"
    }
  , {   'stimulus': "1 j+ 'V' ph pop"
      , 'value': 1 + 1j
      , 'units': 'V'
      , 'text': "1 V + j1 V"
    }
  , {   'stimulus': '2 1 0 "Hello world!"'
      , 'value': 0
      , 'units': ''
      , 'text': "0"
      , 'messages': ["Hello world!"]
    }
  , {   'stimulus': '2 1 0 "$0"'
      , 'value': 0
      , 'units': ''
      , 'text': "0"
      , 'messages': ["0"]
    }
  , {   'stimulus': '2 1 0 "$0 is x"'
      , 'value': 0
      , 'units': ''
      , 'text': "0"
      , 'messages': ["0 is x"]
    }
  , {   'stimulus': '2 1 0 "x is $0"'
      , 'value': 0
      , 'units': ''
      , 'text': "0"
      , 'messages': ["x is 0"]
    }
  , {   'stimulus': '2 1 0 "x is $0, y is $1"'
      , 'value': 0
      , 'units': ''
      , 'text': "0"
      , 'messages': ["x is 0, y is 1"]
    }
  , {   'stimulus': '2 1 0 "x is $0, y is $1, z = $2"'
      , 'value': 0
      , 'units': ''
      , 'text': "0"
      , 'messages': ["x is 0, y is 1, z = 2"]
    }
  , {   'stimulus': '2 1 0 "x is $0, y is $1, z = $2, t is $3"'
      , 'value': 0
      , 'units': ''
      , 'text': "0"
      , 'messages': ["x is 0, y is 1, z = 2, t is $?3?"]
      , 'warnings': ["$3: unknown."]
    }
  , {   'stimulus': '"I have $R, you have $$50"'
      , 'value': 0
      , 'units': ''
      , 'text': "0"
      , 'messages': ["I have 50 Ohms, you have $50"]
    }
  , {   'stimulus': '"I have $Q, you have $$50"'
      , 'value': 0
      , 'units': ''
      , 'text': "0"
      , 'messages': ["I have $?Q?, you have $50"]
      , 'warnings': ["$Q: unknown."]
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
    actions
  , Display('eng', 4)
  , messagePrinter=grabMessages
  , warningPrinter=grabWarnings
)
for index, case in enumerate(testCases):
    messages = []
    warnings = []
    testsRun += 1
    stimulus = case['stimulus']
    expectedResult = case['value']
    expectedUnits = case['units']
    expectedFormattedResult = case['text']
    expectedError = case.get('error', None)
    expectedMessages = case.get('messages', [])
    expectedWarnings = case.get('warnings', [])
    if printTests:
        print status('Trying %d:' % index), stimulus

    calc.clear()
    try:
        result, units = calc.evaluate(calc.split(stimulus))
        error = abs(result - expectedResult)
        failure = (
            error > (reltol*abs(expectedResult) + abstol) or
            calc.format((result, units)) != expectedFormattedResult or
            units != expectedUnits or
            expectedError or
            messages != expectedMessages or
            warnings != expectedWarnings
        )
        if failure:
            failures += 1
            print fail('Failure detected (%s):' % failures)
            print info('    Given:'), stimulus
            print info('    Result  :'), result, calc.format((result, units)), units
            print info('    Expected:'), expectedResult, expectedFormattedResult, expectedUnits
            if messages != expectedMessages:
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
        if expectedError != err.message:
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
exit(0 if testsRun == numTests else 0)
