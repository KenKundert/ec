#!/usr/bin/env python3

# Test EC scripting
# Imports {{{1
import sys
from subprocess import Popen, PIPE
from textwrap import dedent
import pytest

# Utilities {{{1
python = 'python%s' % sys.version[0]

# Test cases {{{1
testCases = [
    {   'stimulus': '-s lg0.ec 1KHz lg.ec',
        'output': '''\
            Open loop gain = 63.732
            Feedback factor = 16
            Loop gain = 1.0197k
        ''',
    },
    {   'stimulus': "'88.3u =Kdet 9.07G =Kvco 2 =M 8 =N 2 =F 1KHz' lg.ec",
        'output': '''
            Open loop gain = 63.732
            Feedback factor = 16
            Loop gain = 1.0197k
        ''',
    },
    {   'stimulus': "'88.3u =Kdet' '9.07G =Kvco' '2 =M' '8 =N' '2 =F' '1KHz' lg.ec",
        'output': '''
            Open loop gain = 63.732
            Feedback factor = 16
            Loop gain = 1.0197k
        '''
    },
    {   'stimulus': r"""'88.3u =Kdet 9.07G =Kvco 2 =M 8 =N 2 =F 1KHz =freq 2pi* "rads/s" =omega Kdet Kvco* omega/ M/ =a N F * =f a f* =T `Open loop gain = $a\nFeedback factor = $f\nLoop gain = $T` quit'""",
        'output': '''
            Open loop gain = 63.732
            Feedback factor = 16
            Loop gain = 1.0197k
        ''',
    },
    {   'stimulus': r"""'(2pi* "rads/s")tw (2pi/ "Hz")tf 100MHz tw tf'""",
        'output': '100 MHz'
    },
    {   'stimulus': "compute-zo",
        'output': 'Zo = 15.166 Ω ∠ -72.343 degs @ 10 MHz.'
    },
]


# Test scripting {{{1
def test_scripting():
    for index, case in enumerate(testCases):
        stimulus = ' '.join(['ec', case['stimulus']])
        expectedResult = dedent(case['output']).strip()

        pipe = Popen(stimulus, shell=True, bufsize=-1, stdout=PIPE)
        pipe.wait()
        result = dedent(pipe.stdout.read().decode()).strip()
        assert result == expectedResult, stimulus


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
