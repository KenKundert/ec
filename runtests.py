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
# use yaml if available, otherwise use pickle
try:
    from yaml import load as loadSummary, dump as dumpSummary
except ImportError:
    from pickle import load as loadSummary, dump as dumpSummary
from textcolors import Colors
from cmdline import commandLineProcessor

# define useful colors  {{{2
colors = Colors()
status = colors.colorizer('blue')
info = colors.colorizer('magenta')
fail = colors.colorizer('red')
succeed = colors.colorizer('green')
exception = colors.colorizer('Red')

# configure the command line processor {{{2
clp = commandLineProcessor()
clp.setDescription('Run Tests', 'Utility for recursively running self tests')
clp.setNumArgs((0,), '[test ...]')
clp.setHelpParams(key='-h', colWidth=14)
opt = clp.addOption(key='fast', shortName='f', longName='fast')
opt.setSummary('take any shortcuts possible to speed testing')
opt = clp.addOption(key='nosummary', shortName='s', longName='nosummary')
opt.setSummary('do not print the summary of test results')
opt = clp.addOption(key='tests', shortName='t', longName='tests')
opt.setSummary('print the test values')
opt = clp.addOption(key='results', shortName='r', longName='results')
opt.setSummary('print the test results')
opt = clp.addOption(key='nocolor', shortName='c', longName='nocolor')
opt.setSummary('do not use color to highlight the results')
opt = clp.addOption(key='coverage', longName='coverage')
opt.setSummary('run coverage analysis')
opt = clp.addOption(key='help', shortName='h', longName='help', action=clp.printHelp)
opt.setSummary('print usage information and exit')
opt = clp.addOption(key='parent', longName='parent')
opt.setNumArgs(1)

# process the command line {{{2
clp.process()

# get the command line options and arguments
opts = clp.getOptions()
args = clp.getArguments()
progName = clp.progName()

# copy options into global variables
fast = 'fast' in opts
printResults = 'results' in opts
printTests = 'tests' in opts or printResults
printSummary = 'nosummary' not in opts or printTests
colorize = 'nocolor' not in opts
coverage = 'coverage' in opts
parent = opts.get('parent', [None])[0]

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
    with open('.%s.sum' % name, 'w') as f:
        dumpSummary({
            'tests': tests
          , 'testFailures': testFailures
          , 'suites': suites
          , 'suiteFailures': suiteFailures
        }, f)

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
    if coverage:
        pythonCmd = 'coverage run -a --branch'
    else:
        pythonCmd = pythonCmd if pythonCmd else 'python'
    pythonPath = ('PYTHONPATH=%s; ' % pythonPath) if pythonPath else ''

    colors.colorize(colorize)
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
