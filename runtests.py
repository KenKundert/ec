# Utility for Recursively Running Self Tests
# TODO {{{1
# Support for coverage is weak because the coverage tool needs to be run
#     hiearchically from the current working directory whereas this tool walks the
#     hierarchy running tests. Probably need a different tool for coverage.
# Consider adding support for functional and unit tests
# Consider adding the number of suites expected in the test script and complain
#     if the number of suites run is not right. This might be annoying to
#     maintain as if you add a test suite at the deepest level, all test files
#     above it would need to be modified.
# Provide a quiet option. Make it default when running hierarically.
# Provide the equivalent to the av summarize command, so that once a quiet run
#     is complete, the summarize command can generate the output as if quiet
#     were not specified, and both the test and the result is available in the
#     summary file so that I can run summary with either -r or -t.
# This could be a warm up to implementing hierarchical testing in AV.

# Description {{{1
"""
Run Tests

Run tests in the current working directory and subdirectories
Expected to be called from a very minimal python test file such as:
    #!/usr/bin/env python
    import runtests

    tests = ['test1', 'test2', ...]
    runtests.runTests(tests) 

The tests will be run and a summary produced. The tests can either be files,
which are expected to be python files (without the .py suffix) or directories,
which are expected to contain another such file named 'test'.

Each test is expected to produce a summary file that will be read to determine
the number of tests and failures that occurred during that test. The summary
file for a python script should be named './.test.name.sum'. The summary file
for a directory should be named './dir/.test.sum'. The invocation of runTests
will create a file in the current working directory named './.test.sum'. These
summary files should contain a dictionary with keys: 'tests', 'failures'.
"""

# preliminaries {{{1
# imports {{{2
import os, sys
# use json if available, otherwise use pickle
try:
    from json import load as loadSummary, dump as dumpSummary
except ImportError:
    from pickle import load as loadSummary, dump as dumpSummary
from textcolors import Colors, isTTY
import argparse

# define useful colors  {{{2
colors = Colors()
status = colors.colorizer('blue')
info = colors.colorizer('magenta')
fail = colors.colorizer('red')
succeed = colors.colorizer('green')
exception = colors.colorizer('Red')

# configure command line processor
progName = os.path.split(sys.argv[0])[1]
cmdline_parser = argparse.ArgumentParser(
    add_help=False, description="Utility for recursively running tests.")
cmdline_parser.add_argument(
    'tests', nargs='*', default=None, help="test name", metavar='<test>')
cmdline_parser.add_argument(
    '-f', '--fast', action='store_true',
    help="take any shortcuts possible to speed testing")
cmdline_parser.add_argument(
    '-s', '--nosummary', action='store_false',
    help="do not print the summary of test results")
cmdline_parser.add_argument(
    '-t', '--test-values', action='store_true', help="print the test values")
cmdline_parser.add_argument(
    '-r', '--results', action='store_true', help="print the test results")
cmdline_parser.add_argument(
    '-c', '--nocolor', action='store_false',
    help="do not use color to highlight test results")
cmdline_parser.add_argument(
    '--coverage', action='store_true', help="run coverage analysis")
cmdline_parser.add_argument(
    '-h', '--help', action='store_true', help="print usage information and exit")
cmdline_parser.add_argument('--parent', nargs='?', default=None)

# process the command line {{{2
cmdline_args = cmdline_parser.parse_args()
if cmdline_args.help:
    cmdline_parser.print_help()
    sys.exit()

# copy options into global variables
fast = cmdline_args.fast
printResults = cmdline_args.results
printTests = cmdline_args.test_values or printResults
printSummary = cmdline_args.nosummary or printTests
colorize = cmdline_args.nocolor
coverage = cmdline_args.coverage
parent = cmdline_args.parent
args = cmdline_args.tests

# cmdLineOpts {{{1
def cmdLineOpts():
    """
    get command line options using something like:
        fast, printSummary, printTests, printResults, colorize, parent = runtests.cmdLineOpts()
    """
    if coverage and not parent:
        print("coverage analysis not performed on %s." % progName)
    return (fast, printSummary, printTests, printResults, colorize, parent)

# writeSummary {{{1
def writeSummary(tests, testFailures, suites = 1, suiteFailures = None):
    """
    write summary file
    """
    # name becomes program names as invoked with .py stripped off
    name = progName if progName[-3:] != '.py' else progName[0:-3]
    if suiteFailures == None and suites == 1:
        suiteFailures = 1 if testFailures else 0
    assert tests >= testFailures
    assert suites >= suiteFailures
    try:
        with open('.%s.sum' % name, 'w') as f:
            dumpSummary({
                'tests': tests
              , 'testFailures': testFailures
              , 'suites': suites
              , 'suiteFailures': suiteFailures
            }, f)
    except IOError as err:
        sys.exit(
            exception(
                "%s: summary file '%s': %s." % (
                    progName, err.filename, err.strerror
                )
            )
        )

# runTests {{{1
def runTests(tests, pythonCmd=None, pythonPath=None, testKey='test'):
    """
    run tests

    tests is a list of strings that contains the names of the tests to be
        run. If the test is a local python file, then it should be named
        <testKey>.<test>.py. If it is a directory, it should be named <test>.
    pythonCmd is the full python command to be used to run the test files. This
        can be used to specify optimization flags to python or the desired
        python version.
    pythonPath is the python path to be set when running the test files.
    testKey is used for two things. First, it is appended to the name of each
        test file. The idea is that each test file would be paired up with the
        file it tests. If the file being tested is spam.py then the test file
        would be <testKey>.spam.py. By separating the test code from the code
        it tests, we make the initial reading of the code faster when it is not
        being tested. Second, when testing the directory, the test script is
        expected to be named ./<test>/<testKey> (notice that there is no .py
        extension even though this would also be a python file).
    """
    pythonCmd = pythonCmd if pythonCmd else 'python'
    if coverage:
        pythonCmd = '%s /usr/bin/coverage run -a --branch' % pythonCmd
    pythonPath = ('PYTHONPATH=%s; ' % pythonPath) if pythonPath else ''

    colors.colorize(colorize and isTTY())
    global args
    if len(args) == 0:
        args = tests

    failures = False
    numTests = 0
    numTestFailures = 0
    numSuites = 0
    numSuiteFailures = 0
    for test in args:
        name = '%s/%s' % (parent, test) if parent else test
        if os.path.isdir(test):
            summaryFileName = './%s/.%s.sum' % (test, testKey)
            _deleteYamlFile(summaryFileName)
            cmd = 'cd %s; ./%s %s' % (test, testKey, _childOpts(test))
            error = _invoke(cmd)
        elif os.path.isfile('%s.%s.py' % (testKey, test)):
            summaryFileName = './.%s.%s.sum' % (testKey, test)
            _deleteYamlFile(summaryFileName)
            if printSummary:
                sys.stdout.write(status('%s: ' % name))
                sys.stdout.flush()
            cmd = pythonPath + '%s %s.%s.py %s' % (
                pythonCmd, testKey, test, _childOpts(test)
            )
            error = _invoke(cmd)
        else:
            print(exception(
                '%s: cannot find test %s, skipping.' % (
                    progName, name
                )
            ))
            numSuites += 1
            numSuiteFailures += 1
            continue
        if error:
            if not coverage:
                # return status of coverage seems broken (sigh)
                print(fail('Failures detected in %s tests.' % name))
                failures = True
        try:
            with open(summaryFileName) as f:
                results = loadSummary(f)
                numTests += results['tests']
                numTestFailures += results['testFailures']
                numSuites += results['suites']
                numSuiteFailures += results['suiteFailures']
        except KeyError:
            sys.exit(
                    exception(
                    '%s: invalid summary file: %s' % (
                        progName, summaryFileName
                    )
                )
            )
        except IOError as err:
            if error:
                numSuites += 1
                numSuiteFailures += 1
            else:
                sys.exit(
                    exception(
                        "%s: summary file '%s': %s." % (
                            progName, summaryFileName, err.strerror
                        )
                    )
                )

    if printSummary and not parent and len(args) > 1:
        preamble = info('Composite results')
        synopsis = '%s of %s test suites failed, %s of %s tests failed.' % (
            numSuiteFailures, numSuites, numTestFailures, numTests
        )
        if numSuiteFailures or numTestFailures:
            print("%s: %s" % (preamble, fail("FAIL: %s" % synopsis)))
        else:
            print("%s: %s" % (preamble, succeed("PASS: %s" % synopsis)))

    try:
        writeSummary(numTests, numTestFailures, numSuites, numSuiteFailures)
    except IOError as err:
        sys.exit(
            exception(
                "%s: summary file '%s': %s." % (
                    progName, summaryFileName, err.strerror
                )
            )
        )

    sys.exit(bool(failures))

# utilities {{{1
# _childOpts {{{2
# create command line options for the children
def _childOpts(test):
    opts = sys.argv[1:]
    opts = []
    if fast: opts += ['-f']
    if not printSummary: opts += ['-s']
    if printTests: opts += ['-t']
    if printResults: opts += ['-r']
    if not colorize: opts += ['-c']
    if parent:
        newParent = '%s/%s' % (parent, test)
    else:
        newParent = test
    opts += ['--parent', newParent]
    return ' '.join(opts)

# _invoke {{{2
# invoke a shell command
def _invoke(cmd):
    try:
        return os.system(cmd)
    except OSError as err:
        sys.exit(
            exception(
                '\n'.join([
                    "%s: when running '%s':" % (sys.argv[0], cmd)
                  , "%s: " % ((err.filename)) if err.filename else ''
                      + "%s." % (err.strerror)
                ])
            )
        )

# _deleteYamlFile {{{2
# delete a summary file (need to do this to assure we don't pick up a
# stale one if the test program fails to generate a new one). 
def _deleteYamlFile(filename):
    if os.path.isfile(filename):
        try:
            os.remove(filename)
        except IOError as err:
            sys.exit(
                exception(
                    "%s: summary file '%s': %s." % (
                        sys.argv[0], filename, err.strerror
                    )
                )
            )
