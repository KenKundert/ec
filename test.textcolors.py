#!/usr/bin/env python

# Test Colorizer
# Imports {{{1
from runtests import cmdLineOpts, writeSummary
from textcolors import Colors, stripColors, _BaseColors, _colorRegex
import sys

# Initialization {{{1
fast, printSummary, printTests, printResults, colorize, parent = cmdLineOpts()
testsRun = 0
failures = 0

# simple names are required for colors to support color replacements
for each in _BaseColors:
    assert _colorRegex.match('<%s>' % each)

color = Colors()
color.addAlias('error', 'red')
color.addAlias('fails', 'Red')
color.addAlias('warning', 'yellow')
color.addAlias('okay', 'Green')
color.addAlias('passes', 'green') # cannot use pass as that is a keyword
color.addAlias('narrate', 'cyan')
color.addAlias('info', 'Magenta')
color.addAlias('hot', 'red')
color.addAlias('cold', 'Cyan')
testColors = Colors(colorize)
status = testColors.colorizer('cyan')
succeed = testColors.colorizer('green')
fail = testColors.colorizer('red')

# Test cases {{{1
colorResultTemplate = '\033[%d;3%dmthis is %%s\033[0m, this is not.'
noColorResultTemplate = '\033[0mthis is %s\033[0m, this is not.'
testColors = [
    ('black',   colorResultTemplate % (0, 0))
  , ('red',     colorResultTemplate % (0, 1))
  , ('green',   colorResultTemplate % (0, 2))
  , ('yellow',  colorResultTemplate % (0, 3))
  , ('blue',    colorResultTemplate % (0, 4))
  , ('magenta', colorResultTemplate % (0, 5))
  , ('cyan',    colorResultTemplate % (0, 6))
  , ('white',   colorResultTemplate % (0, 7))
  , ('Black',   colorResultTemplate % (1, 0))
  , ('Red',     colorResultTemplate % (1, 1))
  , ('Green',   colorResultTemplate % (1, 2))
  , ('Yellow',  colorResultTemplate % (1, 3))
  , ('Blue',    colorResultTemplate % (1, 4))
  , ('Magenta', colorResultTemplate % (1, 5))
  , ('Cyan',    colorResultTemplate % (1, 6))
  , ('White',   colorResultTemplate % (1, 7))
  , ('hot',     colorResultTemplate % (0, 1))
  , ('cold',    colorResultTemplate % (1, 6))
  , ('error',   colorResultTemplate % (0, 1))
  , ('fails',   colorResultTemplate % (1, 1))
  , ('warning', colorResultTemplate % (0, 3))
  , ('okay',    colorResultTemplate % (1, 2))
  , ('passes',  colorResultTemplate % (0, 2))
  , ('narrate',  colorResultTemplate % (0, 6))
  , ('info',    colorResultTemplate % (1, 5))
  , ('none',    noColorResultTemplate)
]
testCases = [
    (   "color['%s']"
      , "color['%s'] + 'this is %s' + color['none'] + ', this is not.'"
      , False
    )
  , (   "color.%s"
      , "color.%s + 'this is %s' + color.none + ', this is not.'"
      , False
    )
  , (   "color('%s', ...)"
      , "color('%s', 'this is %s') + ', this is not.'"
      , False
    )
  , (   "color('... {%s} ...')"
      , "color('<%s>this is %s<none>, this is not.')"
      , True
    )
  , (   "%s(...)"
      , "%s('this is %s') + ', this is not.'"
      , False
    )
]

# Create colorizers
for clr, expected in testColors:
    exec("%s = color.colorizer('%s')" % (clr, clr))

# Run tests {{{1
for wantColor in [None, True, False]:
    if wantColor != None:
        color.colorize(wantColor)
    for Name, Case, extraNone in testCases:
        for clr, expected in testColors:
            expected = expected % clr
            if extraNone:
                expected += color.none
            if wantColor == False:
                expected = stripColors(expected)
            testsRun += 1
            case = Case % (clr, clr)
            name = Name % (clr)
            if printTests:
                print(status('Trying %s:' % (name)))
            result = eval(case)
            if result != expected:
                print("%s: %s ==> %s; expected: %s" % (
                    color('error', "ERROR"), case, result, expected
                ))
                failures += 1

# Print test summary {{{1
numTests = 3 * len(testColors) * len(testCases)
assert testsRun == numTests
if printSummary:
    print('%s: %s tests run, %s failures detected.' % (
        fail('FAIL') if failures else succeed('PASS'), testsRun, failures
    ))

writeSummary(testsRun, failures)
sys.exit(testsRun != numTests)
