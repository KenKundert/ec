#!/usr/bin/env python

# Test Command Line Processor

# Imports {{{1
import sys
from textcolors import Colors
from runtests import cmdLineOpts, writeSummary
from cmdline import CommandLineProcessor, _Error
from StringIO import StringIO

# Initialization {{{1
# read the command lines
fast, printSummary, printTests, printResults, colorize, parent = cmdLineOpts()

# initialize the colors
colors = Colors(colorize)
succeed = colors.colorizer('green')
fail = colors.colorizer('red')
info = colors.colorizer('magenta')
status = colors.colorizer('cyan')

# Test cases {{{1
testCases = [
    {   'stimulus' : ['foo']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', '--flag']
      , 'options'  : {'bool': []}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', '-f123']
      , 'options'  : {'bool1': [], 'bool': [], 'bool3': [], 'bool2': []}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', 'arg']
      , 'options'  : {}
      , 'arguments': ['arg']
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', 'arg1', 'arg2']
      , 'options'  : {}
      , 'arguments': ['arg1']
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : None
      , 'error'    : 'foo: arg2: too many arguments.'
    }

  , {   'stimulus' : ['foo', '-f', 'arg1', 'arg2']
      , 'options'  : {'bool': []}
      , 'arguments': ['arg1']
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : None
      , 'error'    : 'foo: arg2: too many arguments.'
    }

  , {   'stimulus' : ['foo', 'arg1', '-f', 'arg2']
      , 'options'  : {}
      , 'arguments': ['arg1']
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'      : None
      , 'error' : 'foo: -f: unrecognized option.'
    }

  , {   'stimulus' : ['foo', '-f123', 'arg1']
      , 'options'  : {'bool1': [], 'bool': [], 'bool3': [], 'bool2': []}
      , 'arguments': ['arg1']
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', 'a', 'b']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [
            {'key': 'cmda', 'opts': {}, 'args': []}
          , {'key': 'b', 'opts': {}, 'args': []}
        ]
      , 'prereqs'  : set(['pre1', 'pre3', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', '-h', 'b']
      , 'options'  : {'help': ['b']}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : '''\
<<<<<<<<<
Command B
>>>>>>>>>
This is the B command.  It does things related to
B.  Use this command if you want to do B related
things.

Usage: foo [<global options>] b

Use 'foo help' for information on the global
options.
'''
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', '--help']
      , 'options'  : {'help': []}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : '''\
<<<<<<<<<<<<<<<<<<<<
CmdLine Test Program
>>>>>>>>>>>>>>>>>>>>
This is a test program for cmdline.  It really
does not do anything at all.

Usage: foo [options] <args> <command ...>

Commands:
    help <cmd>
             Print help about using this program.
    cmda, a  this is a summary of command A
    b        this is a summary of command B
    cmdc, c  this is a summary of command C

Use 'foo help <cmd>' for more detailed information
on a specific command.

Options:
    -h, --help <cmd>
             use this to print usage information
    --lcv L.C:V L.C:V
             lib, cell, view
    -f, --flag
             boolean flag
    -1       boolean flag 1
    -2       boolean flag 2
    -3       boolean flag 3

'''
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', '--help', 'a']
      , 'options'  : {'help': ['a']}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : '''\
<<<<<<<<<
Command A
>>>>>>>>>
This is the A command.  It does things related to
A.  Use this command if you want to do A related
things.

Usage: foo [<global options>] cmda [<command options>]

Aliases: cmda, a

Command Options:
    -x, --extra <args>
             this is an extra option

Use 'foo help' for information on the global
options.
'''
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', 'help']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [None]
      , 'prereqs'  : set([])
      , 'stdout'   : '''\
<<<<<<<<<<<<<<<<<<<<
CmdLine Test Program
>>>>>>>>>>>>>>>>>>>>
This is a test program for cmdline.  It really
does not do anything at all.

Usage: foo [options] <args> <command ...>

Commands:
    help <cmd>
             Print help about using this program.
    cmda, a  this is a summary of command A
    b        this is a summary of command B
    cmdc, c  this is a summary of command C

Use 'foo help <cmd>' for more detailed information
on a specific command.

Options:
    -h, --help <cmd>
             use this to print usage information
    --lcv L.C:V L.C:V
             lib, cell, view
    -f, --flag
             boolean flag
    -1       boolean flag 1
    -2       boolean flag 2
    -3       boolean flag 3

'''
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', 'help', '-s']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [None]
      , 'prereqs'  : set([])
      , 'stdout'   : '''\
<<<<<<<<<<<<<<<<<<<<
CmdLine Test Program
>>>>>>>>>>>>>>>>>>>>
This is a test program for cmdline.  It really
does not do anything at all.

Usage: foo [options] <args> <command ...>

Commands:
    b        this is a summary of command B
    cmda, a  this is a summary of command A
    cmdc, c  this is a summary of command C
    help <cmd>
             Print help about using this program.

Use 'foo help <cmd>' for more detailed information
on a specific command.

Options:
    -f, --flag
             boolean flag
    -1       boolean flag 1
    -2       boolean flag 2
    -3       boolean flag 3
    -h, --help <cmd>
             use this to print usage information
    --lcv L.C:V L.C:V
             lib, cell, view

'''
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', 'help', '--sort']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [None]
      , 'prereqs'  : set([])
      , 'stdout'   : '''\
<<<<<<<<<<<<<<<<<<<<
CmdLine Test Program
>>>>>>>>>>>>>>>>>>>>
This is a test program for cmdline.  It really
does not do anything at all.

Usage: foo [options] <args> <command ...>

Commands:
    b        this is a summary of command B
    cmda, a  this is a summary of command A
    cmdc, c  this is a summary of command C
    help <cmd>
             Print help about using this program.

Use 'foo help <cmd>' for more detailed information
on a specific command.

Options:
    -f, --flag
             boolean flag
    -1       boolean flag 1
    -2       boolean flag 2
    -3       boolean flag 3
    -h, --help <cmd>
             use this to print usage information
    --lcv L.C:V L.C:V
             lib, cell, view

'''
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', 'help', 'a']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [None]
      , 'prereqs'  : set([])
      , 'stdout'   : '''\
<<<<<<<<<
Command A
>>>>>>>>>
This is the A command.  It does things related to
A.  Use this command if you want to do A related
things.

Usage: foo [<global options>] cmda [<command options>]

Aliases: cmda, a

Command Options:
    -x, --extra <args>
             this is an extra option

Use 'foo help' for information on the global
options.
'''
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', '--doesnotexist']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'      : None
      , 'error' : 'foo: --doesnotexist: unknown option.'
    }

  , {   'stimulus' : ['foo', '--lcv', 'lib1.cell1:view1']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'      : None
      , 'error' : 'foo: --lcv: too few arguments, expected at least 2.'
    }

  , {   'stimulus' : ['foo', '--lcv', 'lib1.cell1:view1', 'lib2.cell2:view2']
      , 'options'  : {'lcv': ['lib1.cell1:view1', 'lib2.cell2:view2']}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : "This is LCV option: ['lib1.cell1:view1', 'lib2.cell2:view2']"
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', '--lcv', 'lib1.cell1:view1', 'lib2.cell2:view2', 'lib3.cell3:view3']
      , 'options'  : {'lcv': ['lib1.cell1:view1', 'lib2.cell2:view2']}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : "This is LCV option: ['lib1.cell1:view1', 'lib2.cell2:view2']"
      , 'error'    : "foo: argument 'lib3.cell3:view3' has the wrong form, expected an identifier."
    }

  , {   'stimulus' : ['foo', '--lcv', 'lib1:cell1.view1', 'lib2.cell2:view2']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : None
      , 'error'    : "foo: --lcv: argument 'lib1:cell1.view1' has the wrong form, expected '<lib>.<cell>:<view>'."
    }

  , {   'stimulus' : ['foo', 'cmda', '-x']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [
            {'key': 'cmda', 'opts': {'xtra': []}, 'args': []}
        ]
      , 'prereqs'  : set(['pre1', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', 'cmda', '--extra']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [
            {'key': 'cmda', 'opts': {'xtra': []}, 'args': []}
        ]
      , 'prereqs'  : set(['pre1', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', 'cmda', '--extra', 'lib1.cell1:view1']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [
            {'key': 'cmda', 'opts': {'xtra': ['lib1.cell1:view1']}, 'args': []}
        ]
      , 'prereqs'  : set(['pre1', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : [
            'foo'
          , 'cmda'
          , '--extra'
          , 'lib1.cell1:view1'
          , 'lib2.cell2:view2'
        ]
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [
            {   'key': 'cmda'
              , 'opts': {'xtra': ['lib1.cell1:view1', 'lib2.cell2:view2']}
              , 'args': []
            }
        ]
      , 'prereqs'  : set(['pre1', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : [
            'foo'
          , 'cmda'
          , '--extra'
          , 'lib1.cell1:view1'
          , 'lib2.cell2:view2'
          , 'lib3.cell3:view3'
        ]
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [
            {   'key': 'cmda'
              , 'opts': {
                    'xtra': [
                        'lib1.cell1:view1'
                      , 'lib2.cell2:view2'
                      , 'lib3.cell3:view3'
                    ]
                }
              , 'args': []
            }
        ]
      , 'prereqs'  : set(['pre1', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : [
            'foo'
          , 'cmda'
          , '--extra'
          , 'lib1.cell1:view1'
          , 'lib2.cell2:view2'
          , 'lib3.cell3:view3'
          , 'lib4.cell4:view4'
        ]
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [
            {   'key': 'cmda'
              , 'opts': {
                    'xtra': [
                        'lib1.cell1:view1'
                      , 'lib2.cell2:view2'
                      , 'lib3.cell3:view3'
                      , 'lib4.cell4:view4'
                    ]
                }
              , 'args': []
            }
        ]
      , 'prereqs'  : set(['pre1', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : [
            'foo'
          , 'cmda'
          , '--extra'
          , 'lib1:cell1.view1'
          , 'lib2.cell2:view2'
        ]
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set(['pre1', 'pre2'])
      , 'stdout'   : None
      , 'error'    : "foo: --extra: argument 'lib1:cell1.view1' has the wrong form, expected '<lib>.<cell>:<view>'."
    }

  , {   'stimulus' : ['foo', 'cmdc']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [{'key': 'cmdc', 'opts': {}, 'args': []}]
      , 'prereqs'  : set(['pre3', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', 'c', 'lib1.cell1:view1']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [{'key': 'cmdc', 'opts': {}, 'args': ['lib1.cell1:view1']}]
      , 'prereqs'  : set(['pre3', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', 'cmdc', 'lib1.cell1:view1', 'lib2.cell2:view2']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [
            {   'key': 'cmdc'
              , 'opts': {}
              , 'args': ['lib1.cell1:view1', 'lib2.cell2:view2']
            }
        ]
      , 'prereqs'  : set(['pre3', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : [
            'foo'
          , 'cmdc'
          , 'lib1.cell1:view1'
          , 'lib2.cell2:view2'
          , 'lib3.cell3:view3'
        ]
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [
            {   'key': 'cmdc'
              , 'opts': {}
              , 'args': ['lib1.cell1:view1', 'lib2.cell2:view2']
            }
        ]
      , 'prereqs'  : set(['pre3', 'pre2'])
      , 'stdout'      : None
      , 'error' : "foo: argument 'lib3.cell3:view3' has the wrong form, expected an identifier."
    }

  , {   'stimulus' : ['foo', 'c', 'lib1.cell1:view1', '-', 'b']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [
            {   'key': 'cmdc'
              , 'opts': {}
              , 'args': ['lib1.cell1:view1']
            }
          , {   'key': 'b'
              , 'opts': {}
              , 'args': []
            }
        ]
      , 'prereqs'  : set(['pre1', 'pre3', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : [
            'foo'
          , 'cmdc'
          , '--extra'
          , 'lib1.cell1:view1'
          , '-'
          , 'lib2.cell2:view2'
          , 'lib3.cell3:view3'
          , 'b'
        ]
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [
            {   'key': 'cmdc'
              , 'opts': {'xtra': ['lib1.cell1:view1']}
              , 'args': ['lib2.cell2:view2', 'lib3.cell3:view3']
            }
          , {'key': 'b', 'opts': {}, 'args': []}
        ]
      , 'prereqs'  : set(['pre1', 'pre3', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : [
            'foo'
          , '-f123'
          , 'cmdc'
          , '--extra'
          , 'lib1.cell1:view1'
          , '-'
          , 'lib2.cell2:view2'
          , 'lib3.cell3:view3'
          , 'b'
          , 'arg'
        ]
      , 'options'  : {'bool1': [], 'bool': [], 'bool3': [], 'bool2': []}
      , 'arguments': ['arg']
      , 'commands' : [
            {   'key': 'cmdc'
              , 'opts': {'xtra': ['lib1.cell1:view1']}
              , 'args': ['lib2.cell2:view2', 'lib3.cell3:view3']
            }
          , {'key': 'b', 'opts': {}, 'args': []}
        ]
      , 'prereqs'  : set(['pre1', 'pre3', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', 'cmda', '-']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [{'key': 'cmda', 'opts': {}, 'args': []}]
      , 'prereqs'  : set(['pre1', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', '-']
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : [
            'foo'
          , 'cmdc'
          , '-xy'
          , 'lib1.cell1:view1'
          , '-'
          , 'fux'
          , '-'
          , 'lib2.cell2:view2'
          , 'lib3.cell3:view3'
          , 'b'
        ]
      , 'options'  : {}
      , 'arguments': []
      , 'commands' : [
            {   'key': 'cmdc'
              , 'opts': {
                    'xtra': ['lib1.cell1:view1']
                  , 'yetanother': ['fux']
                }
              , 'args': ['lib2.cell2:view2', 'lib3.cell3:view3']
            }
          , {'key': 'b', 'opts': {}, 'args': []}
        ]
      , 'prereqs'  : set(['pre1', 'pre3', 'pre2'])
      , 'stdout'   : None
      , 'error'    : None
    }

  , {   'stimulus' : ['foo', '-f11']
      , 'options'  : {'bool1': [], 'bool': []}
      , 'arguments': []
      , 'commands' : []
      , 'prereqs'  : set([])
      , 'stdout'   : "foo: option '-f11' specified again, ignored.\n"
      , 'error'    : None
    }

#  At some point we should allow the options and arguments to be intermixed or
#  at least allow the arguments to proceed the options.  When we do, these two
#  cases can help test this new capability.
#  , {   'stimulus' : ['foo', 'cmdc', '-x', '-', 'a1', 'a2']
#      , 'options'  : {}
#      , 'arguments': []
#      , 'commands' : [
#            {'key': 'cmdc', 'opts': {'xtra': []}, 'args': ['a1', 'a2']}
#        ]
#      , 'prereqs'  : set(['pre3', 'pre2'])
#      , 'stdout'   : None
#      , 'error'    : None
#    }
#
#  , {   'stimulus' : ['foo', 'cmdc', 'a1', 'a2', '-x']
#      , 'options'  : {}
#      , 'arguments': []
#      , 'commands' : [
#            {'key': 'cmdc', 'opts': {'xtra': []}, 'args': ['a1', 'a2']}
#        ]
#      , 'prereqs'  : set(['pre3', 'pre2'])
#      , 'stdout'   : None
#      , 'error'    : None
#    }
]

# Build representative command line processor  {{{1
# define a few things that we will need during the command line processing
def cmdAfunc(key, opts, args):
    assert key == 'cmda'
    return {'key': key, 'opts': opts, 'args': args}

def cmdBfunc(key, opts, args):
    assert key == 'b'
    return {'key': key, 'opts': opts, 'args': args}

def cmdCfunc(key, opts, args):
    assert key == 'cmdc'
    return {'key': key, 'opts': opts, 'args': args}

def optLCVfunc(key, args):
    assert key == 'lcv'
    print 'This is LCV option:', args,

class Error(Exception):
    def __init__(self, progName, msg, helpKey):
        self.progName = progName
        self.msg = msg
        self.helpKey = helpKey

clp = CommandLineProcessor()
clp.setDescription('CmdLine Test Program' , """
    This is a test program for cmdline.  
    It really does not do anything at all.
""")
clp.setNumArgs((0,1), '<args>')
clp.setHelpParams(
    key='help'
  , sortKey='Sort'
  , colWidth=7
  , pageWidth=50
  , shouldExit=False
  , titleDecoration='><'
)
clp.setArgFilter(r"\A[a-z_]+[a-z0-9_]*\Z", 'an identifier')
clp.setErrorHandler(Error)
optHelp = clp.addOption('help', 'h', 'help', clp.printHelp)
optHelp.setNumArgs((0,1), '<cmd>')
optHelp.setSummary('use this to print usage information')
optLCV = clp.addOption('lcv', longName='lcv', action=optLCVfunc)
optLCV.setSummary('lib, cell, view')
optLCV.setNumArgs(2, 'L.C:V L.C:V')
optLCV.setArgFilter(
    r"\A(([a-z_]+[a-z0-9_]*)\.)?([a-z_]+[a-z0-9_]*)(:([a-z_]+[a-z0-9_]*))?\Z",
    "'<lib>.<cell>:<view>'"
)
optFlag = clp.addOption('bool', 'f', 'flag')
optFlag.setSummary('boolean flag')
optFlag1 = clp.addOption('bool1', '1')
optFlag1.setSummary('boolean flag 1')
optFlag2 = clp.addOption('bool2', '2')
optFlag2.setSummary('boolean flag 2')
optFlag3 = clp.addOption('bool3', '3')
optFlag3.setSummary('boolean flag 3')
cmdHelp = clp.addCommand(['help'], clp.printHelp)
cmdHelp.setSummary('Print help about using this program.')
cmdHelp.setDescription('Help' , """
    This is the help command.  It is an alternative implementation to providing
    help.  (the other being --help).  This is a bit more flexible because you
    can use the helpSortKey to allow the user to specify that the lists should
    be sorted.
""")
cmdHelp.setNumArgs((0,1), "<cmd>")
optSort = cmdHelp.addOption('Sort', 's', 'sort')
cmdA = clp.addCommand(['cmda', 'a'], cmdAfunc, ['pre1', 'pre2'])
cmdA.setDescription('Command A' , """
    This is the A command.  It does things related to A.  Use this command if 
    you want to do A related things.
""")
cmdA.setSummary('this is a summary of command A')
optAX = cmdA.addOption('xtra', 'x', 'extra')
optAX.setSummary('this is an extra option')
optAX.setNumArgs((0,), '<args>')
optAX.setArgFilter(
    r"\A(([a-z_]+[a-z0-9_]*)\.)?([a-z_]+[a-z0-9_]*)(:([a-z_]+[a-z0-9_]*))?\Z",
    "'<lib>.<cell>:<view>'"
)
cmdB = clp.addCommand('b', cmdBfunc, ['pre1', 'pre3'])
cmdB.setDescription('Command B' , """
    This is the B command.  It does things related to B.  Use this command if 
    you want to do B related things.
""")
cmdB.setSummary('this is a summary of command B')
cmdC = clp.addCommand(['cmdc', 'c'], cmdCfunc, ['pre2', 'pre3'])
cmdC.setDescription('Command C' , """
    This is the C command.  It does things related to C.  Use this command if 
    you want to do C related things.
""")
cmdC.setSummary('this is a summary of command C')
cmdC.setNumArgs((0, 2))
cmdC.setArgFilter(
    r"\A(([a-z_]+[a-z0-9_]*)\.)?([a-z_]+[a-z0-9_]*)(:([a-z_]+[a-z0-9_]*))?\Z",
    "'<lib>.<cell>:<view>'"
)
optCX = cmdC.addOption('xtra', 'x', 'extra')
optCX.setSummary('this is an extra option')
optCX.setNumArgs((0, 2))
optCX.setArgFilter(
    r"\A(([a-z_]+[a-z0-9_]*)\.)?([a-z_]+[a-z0-9_]*)(:([a-z_]+[a-z0-9_]*))?\Z",
    "'<lib>.<cell>:<view>'"
)
optCX = cmdC.addOption('yetanother', 'y', 'yetanother')
optCX.setSummary('this is an yet another option')
optCX.setNumArgs((0, 2))

# Run cases {{{1
testsRun = 0
failures = 0
trueStdout = sys.stdout
trueStderr = sys.stderr
fauxStderr = StringIO()
for index, case in enumerate(testCases):
    testsRun += 1

    # copy stimulus/response information into local variables
    stimulus = case.get('stimulus', [])
    expectedOptions = case.get('options', {})
    expectedArguments = case.get('arguments', [])
    expectedCommands = case.get('commands', [])
    expectedPrereqs = case.get('prereqs', set([]))
    expectedStdout = case.get('stdout', None)
    expectedError = case.get('error', None)
    if expectedStdout == None:
        expectedStdout = ''

    # apply stimulus to command line processor
    if printTests:
        print status('Trying %d:' % index), ' '.join(stimulus)
    try:
        # redirect stdout & stderr to strings so I can capture and compare them
        sys.stdout = StringIO()
        sys.stderr = fauxStderr

        # process the command line
        options, arguments, commands, prereqs = clp.process(stimulus)
        commandsInfo = []
        for cmd in commands:
            commandsInfo += [cmd.process()]

        # grab output sent to stdout and reattach it to true stream
        stdout = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = trueStdout
        sys.stderr = trueStderr
        assert fauxStderr.getvalue() == ''

        if (
            options != expectedOptions
            or arguments != expectedArguments
            or commandsInfo != expectedCommands
            or prereqs != expectedPrereqs
            or stdout != expectedStdout
        ):
            failures += 1
            print fail('Failure detected (%s):' % failures)
            print info('    Given:'), stimulus
            if options != expectedOptions:
                print info('    Options  :'), options
                print info('    Expected :'), expectedOptions
            if arguments != expectedArguments:
                print info('    Arguments:'), arguments
                print info('    Expected :'), expectedArguments
            if commandsInfo != expectedCommands:
                print info('    Commands :'), commandsInfo
                print info('    Expected :'), expectedCommands
            if prereqs != expectedPrereqs:
                print info('    Prereqs  :'), prereqs
                print info('    Expected :'), expectedPrereqs
            if stdout != expectedStdout:
                print info('    Response :'), stdout
                print info('    Expected :'), expectedStdout
        elif printResults:
            print succeed('    Options  :'), options
            print succeed('    Arguments:'), arguments
            print succeed('    Commands :'), commands
            print succeed('    Prereqs  :'), prereqs
            print succeed('    Stdout   :'), stdout
    except Error, err:
        # reattach true stdout & stderr streams
        response = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = trueStdout
        sys.stderr = trueStderr
        assert fauxStderr.getvalue() == ''

        # process the error
        src = '%s: ' % err.progName if err.progName else ''
        error = '%s%s.' % (src, err.msg)
        if not expectedError:
            failures += 1
            print fail('Error detected (%s):' % failures)
            print info('    Given:'), stimulus
            print info('    Error:'), error
        elif error != expectedError:
            failures += 1
            print fail('Failure detected (%s):' % failures)
            print info('    Given:'), stimulus
            print info('    Error    :'), error
            print info('    Expected :'), expectedError
        elif printResults:
            print succeed('    Error:'), error

# Generate summary {{{1
assert testsRun == len(testCases)
if printSummary:
    if failures:
        print fail('FAIL:'),
    else:
        print succeed('PASS:'),
    print '%s tests run, %s failures detected.' % (testsRun, failures)

# Write summary to Yaml file
writeSummary(testsRun, failures)
exit(int(bool(failures)))
