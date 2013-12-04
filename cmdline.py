# Command Line Processor
# TODO {{{1
# 1. Implement man page creation
# 2. Provide support for numbered and bulleted lists in descriptions. (See
#    check-claims)
# 3. Return options as a list of objects rather than a dictionary so that options
#    can be repeated
# 4. Help sorts on the key rather than the name. Should probably fix that.
#
# Henry requested that the options be allowed to follow the arguments.  That
# would be done in _processCommand(), but doing so introduces an inconsistency.
# The user would only be able to specify options after arguments for the
# commands, and not for the base command.  If they also wanted to do it for the
# base command, then there would be an ambiguity for options at the end, are
# they for the last command or the base command.
#
# It would be nice to have a restructuredText to restructuredText converter,
# meaning that it would be nice to have a method that takes a string a very
# restricted from of restructuredText (paragraphs, titles, lists) and formats
# it for the output to a terminal (largely just calls textwrap on the various
# pieces to convert it to the right width).
#
# It might also be nice to have a method installOptions() that would take the
# dictionary of the calling context and install variable for all of the various
# options.

# Description {{{1
# Privacy Policy
# From outside module, access only classes and their methods that do not begin
# with an underscore.  Even then, Options and Commands are not intended to be
# accessed directly, but rather through the option and command methods of
# CommandLineProcessor.  Do not directly access any object attributes or global
# variables other than methods.

r"""Command Line Processor

Implements a command-line processor that supports options and commands.  The
options and commands may both have arguments, and the commands may themselves
have options.  The arguments may be constrained in their form (by providing a
regular expression that they must match), and in their number (by providing a
lower and/or upper bound).  A method (printHelp) is provided that can be called
to print a usage message.  To simplify access to options, options are only
allowed to be given once on a command line.

Command lines consist of four types of items: the name of the program as
invoked, options, arguments and commands.  The name of the program is always
the first item in the command line.  An option is a item that begins with either
'-' or '--'.  An argument is a relatively unconstrained item that may be
associated with an option or a command.  A command is name from a predefined
list of names.  For example, this is a typical linux command line:
    ls -l /tmp
In this case, 'ls' is the program name, '-l' is an option, and '/tmp' is an
argument.  Several of the short form option names can be combined into a single
option, such as
    tar -zcvf cmdline.tgz cmdline
More and more these days command lines are using commands.  For example,
    hg status -q
Here, 'status' is a command and '-q' is an option to that command.

This command line processor interprets command lines that consist of options
and commands, and it allows the options to have arguments and the commands to
have both options and arguments.  A global option (one that is not associated
with a command) precedes any command on the command line.  For example, in
    prog -a act --xyz
the '-a' option is global and the '--xyz' option is associated with the 'act'
command.  An option can take one or more arguments.
    prog -d ./census.dat
Here './census.dat' is an argument to the '-d' option.  The number of arguments
need not be constrained a priori.  In this case it may be ambiguous when the
argument list ends.  In this case an empty option, '-', can be used to terminate
the argument list.
    prog -d ./census1.dat ./census2.dat ./census3.dat - report
In this case, without the '-', 'report' would have been interpreted as another
argument to '-d'.  Like options, commands also take arguments, and like
options, you would use an empty option ('-') to terminate an argument list.
This is possible when the length of the argument list is not fixed and if there
is the possibility of an ambiguity.  For example, you would not use an empty
option to terminate the argument list of an option that takes either one or two
arguments for with two arguments were specified.

The 'CommandLineProcessor' class is used to create a command line processor.  In
most cases, there is only one command line to process, sys.argv, and a
CommandLineProcessor object is created automatically and preloaded with
sys.argv upon startup, so it is unnecessary to directly create a
CommandLineProcessor object.  Instead, you would call the commandLineProcessor
function, which returns the currently active command line processor.

The first step is to describe the structure of an acceptable command line to
the command line processor.  You do this by calling methods of the command line
processor object to describe options, commands, arguments, and properties.  For
example, to configure the command line processor with a textual description of
the underlying program and tell it to accept one argument you would use:
    clp = commandLineProcessor()
    clp.setDescription('Waveform plotter', '''
        Plots all the waveforms in a file.
    ''')
    clp.setNumArgs(1)
    clp.process()
    args = clp.getArguments()

Now consider doing the same thing, but this time pass we will pass the name of
the waveform file in as and option and the names of the waveforms to plot as
arguments.
    clp = commandLineProcessor()
    clp.setDescription( ... )
    clp.setNumArgs((1,), '<waveform> [ ... ]')
    clp.setArgFilter(r"\A[a-z_]+[a-z0-9_]*\Z", expected='an identifier')
    opt = clp.addOption(key='file', shortName='f', longName='file')
    opt.setSummary('the waveform file')
    opt.setNumArgs(1, "<filename>.wav")
    opt.setArgFilter(r"\A.*\.wav\Z", expected="'<filename>.wav'")
    opt = clp.addOption(key='help', shortName='h', longName='help', action=clp.printHelp)
    opt.setSummary('print usage information')
    clp.process()
    args = clp.getArguments()
    opts = clp.getOptions()
In this example a tuple was passed into setNumArgs() to specify the lower and
upper bound on the number of arguments accepted.  A description of the arguments
was also given as an aid to the end user.  The convention use here and in most
command line descriptions is that brackets ([]) are used to indicate an
optional argument and angles (<>) are used to indicate a substitution (it acts
as a guide rather than being something that should be typed literally).  Since
the upper bound was not given, there is no upper bound.  An argument filter was
given for the command line processor, which limits the global arguments to
simple identifiers.  Two options were created, one takes a file argument and one
that handles the usage message generation.  The first takes one argument that is
constrained to have a .wav file extension.  The second is passes a function
(actually in this case it is a method) that is called as soon as the option is
encountered.  In this case the built-in usage message generator (printHelp) is
used.  Thus, options can be handled using two different mechanisms, either using
the action function or by accessing the dictionary of objects encountered using
clp.getOptions().  The action function takes one required argument 'key', which
is the option key, and one optional argument 'args', which is a list of
arguments specified by the user for the option.  The value for the options
returned by getOptions() is the list of arguments specified by the user.
If you only expected a single argument, you may access it with
    optValue = opts.get(key, [default])[0]

The only major feature left to describe is commands.  You would use
    cmdConvert = clp.addCommand('convert', action=convertFileType)
to create a command, in this case 'convert'.  You can give the command aliases
by providing a list of names rather than a single name as the first argument.
In this case, the first name in the list is the primary name that is used later
to identify the command as a key.  Command objects support option, setSummary,
setDescription, setNumArgs, and setArgFilter methods.  The action function, if
given, is expected to take three arguments: 'key' is the primary name of the
command, 'opts' is a dictionary that contains the options specified for the
command and their values, and 'args' is the list of command arguments.
Alternatively you can use clp.getCommands() to get a list of command items,
each of which has three attributes: 'key', 'opts', and 'args'.
"""

# Preliminaries {{{1
# Imports {{{2
from __future__ import print_function
import sys
import os.path
import re
from copy import copy
import textwrap

# Globals {{{2
_ActiveCLP = None

# Utilities {{{2

# Exceptions {{{2
class _Error(Exception):
    def __init__(self, msg):
        clp = commandLineProcessor()
        progName = clp.progName()
        if clp.errorHandler:
            raise clp.errorHandler(progName, msg, clp.helpKey)
        src = '%s: ' % progName if progName else ''
        msg = '%s%s.' % (src, msg)
        self.msg = msg
        if clp.helpKey:
            msg += "\nUse '%s %s' for help on the use of this command." % (
                progName, clp.helpKey
            )
        sys.stderr.write(msg + '\n')
        # is it a mild unix convention that command line errors cause an exit
        # with status code 2.
        sys.exit(2)

# Item Class (private) {{{1
# A class used to hold the values of options and commands
class _Item:
    def __init__(self, key, args, opts = None, action = None):
        self.key = key
        self.args = args
        if opts != None:
            self.opts = opts
        if action != None:
            self.action = action

    # return summary of item
    def summary(self):
        """
        Simple summary of this item.

        returns a string that contains the key name and the arguments
        contained in this item.
        """
        sum = [self.key]
        #try:
        #    for key, val in self.opts.iteritems():
        #        sum += [key] + val
        #except AttributeError:
        #    pass
        for arg in self.args:
            sum += [arg]
        return ' '.join(sum)

    # process item
    def process(self, **info):
        if self.action:
            if hasattr(self, 'opts'):
                return self.action(key=self.key, opts=self.opts, args=self.args, **info)
            else:
                return self.action(key=self.key, args=self.args, **info)
        else:
            # object for now, but probably want to just continue silently
            raise NotImplementedError

# Argument Base Class (private) {{{1
# A base class for arguments (global, option, and command)
class _Generic:
    def __init__():
        raise NotImplementedError

    def setSummary(self, sum):
        """Provide a summary description.

        Use this to provide a succinct (half line) description of the object
        (option or command).
        """
        self.sum = sum

    # an option has been found, save it and any arguments it may have
    def _processOption(self, clp, name):
        assert name[0] == '-'
        if name[1] == '-':
            # long form, process one option, possibly with arguments
            opt = self.optionLongNames[name[2:]]
            args = opt._processArguments(clp, name)
            if opt.key in self.optionsGiven:
                print("%s: option '%s' specified again, ignored." % (clp.invokedAs, name))
            else:
                self.optionsGiven.update({opt.key: args})
            if opt.action:
                opt.action(key=opt.key, args=args)
        else:
            # short form, process one or more option, each possibly with arguments
            for each in name[1:]:
                opt = self.optionShortNames[each]
                args = opt._processArguments(clp, '-'+each)
                if opt.key in self.optionsGiven:
                    print("%s: option '%s' specified again, ignored." % (clp.invokedAs, name))
                else:
                    self.optionsGiven.update({opt.key: args})
                if opt.action:
                    opt.action(key=opt.key, args=args)

class _Argument(_Generic):
    def __init__():
        raise NotImplementedError

    def setNumArgs(self, numArgs, desc = None):
        """Specify the number of arguments.

        Use this to indicate how many arguments an object is expecting.  If you
        do not specify the number of arguments, the object will not accept any
        arguments.  If you specify the number as a simple integer, it will
        expect exactly that many arguments.  Otherwise, you set the minimum and
        maximum number of arguments accepted using a tuple of the form (min,
        max), where min and max are both integers.  If max is not given, then
        there is no limit to how many arguments the object will accept.
        """
        if type(numArgs) == int:
            self.minArgs = numArgs
            self.maxArgs = numArgs
        elif type(numArgs) == tuple:
            if len(numArgs) == 1:
                self.minArgs, = numArgs
                self.maxArgs = None
            elif len(numArgs) == 2:
                self.minArgs, self.maxArgs = numArgs
            else:
                raise AssertionError
            if self.maxArgs != None:
                assert self.minArgs <= self.maxArgs
        else:
            raise AssertionError
        self.argDesc = desc

    def setArgFilter(self, filter, expected = None):
        """Specify the form of the arguments.

        Use this method to specify the form of the arguments by providing a
        regular expression (uncompiled) to 'filter' (a string).  The optional
        'expected' argument (string) would take a very short example of the
        form that is expected that is printed in the error message if the
        argument provided by the user is not of the expected form.
        """
        self.argFilter = re.compile(filter)
        self.argForm = expected

    def _processArguments(self, clp, name = ''):
        if name:
            name += ': '
        args = []
        while self.maxArgs == None or len(args) < self.maxArgs:
            # if maxArgs == None, there is no limit to the number of arguments.
#            if len(args) < self.minArgs:
#                # in this special case, argument may begin with a -
#                if clp._tokensLeft():
#                    args += [clp._nextToken()]
#                else:
#                    break
#            else:
            if clp._nextTokenIsArg():
                args += [clp._nextToken()]
            else:
                # found an option, terminate this list
                if clp._nextTokenIsEmpty():
                    # found the empty option, discard this token
                    clp._nextToken()
                break
        if len(args) < self.minArgs:
            raise _Error("%stoo few arguments, expected at least %d" % (name, self.minArgs))
        if self.argFilter:
            for each in args:
                if not self.argFilter.match(each):
                    msg = "%sargument '%s' has the wrong form" % (name, each)
                    if self.argForm:
                        raise _Error("%s, expected %s" % (msg, self.argForm))
                    else:
                        raise _Error(msg)

        return args

# CommandLineProcessor class {{{1
class CommandLineProcessor(_Argument):
    """Create a command line processor.

    Use this to describe the commands and options that are to be accepted on the
    command line.  Also use it to process a list of arguments.  User provided
    functions are called as global options and commands are recognized.  Any
    error in the command line causes exit() to be called, which prints a helpful
    message to stderr.
    """
    def __init__(self, args = None):
        """The constructor.

        'args' is a list of strings containing the command line arguments.  It
        almost always is simply passed sys.argv.  You can pass it in here, or
        into the process() method.
        """
        self.commandNames = []
        self.commandDefs = {}
        self.optionDefs = []
        self.optionShortNames = {}
        self.optionLongNames = {}
        if args:
            self.args = copy(args)
        else:
            self.args = None
        self.minArgs = 0
        self.maxArgs = 0
        self.argDesc = None
        self.argFilter = None
        self.argForm = None
        self.desc = None
        self.helpKey = None
        self.helpSortKey = None
        self.helpColWidth = 12
        self.helpPageWidth = 80
        self.helpTitleDecoration = '=='
        self.helpAlwaysSort = 12
        self.helpShouldExit = True
        self.errorHandler = None
        activateCLP(self)

    # addCommand {{{2
    def addCommand(self, names, action = None, prereqs=set()):
        """Define a new command.

        Takes three arguments. 'names' is a string or a list of strings that
        contains the name or names of the command.  The first name in this list
        is considered the primary command name. 'action' is a function that
        implements the command.  If None the function will not be called.
        'prereqs' is a list of strings that is used to indication which
        initializations are required for this command.
        
        When using the _Item
        The action function is expected to take at least three arguments.  First
        is 'key', a string that contains the primary name of the command.  The
        second is 'opts'.  It is a dictionary that contains the primary name of
        the command options specified by the user along with their values (a
        list).  The third is 'args', it is a list of values for the commands
        arguments.  Beyond these three arguments, 
        """
        return Command(self, names, action, prereqs)

    # Command class calls this to add the name into the list of command names
    def _addCommandName(self, name):
        self.commandNames += [name]

    # Command class calls this to add the command into the list of commands
    def _addCommand(self, name, cmd):
        self.commandDefs.update({name: cmd})

    # addOption {{{2
    # user calls this to define a new global option
    def addOption(self, key, shortName = None, longName = None, action = None):
        """Define a new global option.

        'key' is the dictionary key you will use to access the value of this
        option. 'shortName' and 'longName' are the short and long forms of the
        option name, without any leading dashes.  The short name must be a
        single character.  'action' is a function that is called when the
        option has been found in the command line.  This function is expected to
        take a two arguments.  The first, 'key', is the key for the option.  The
        second is 'args'.  It is a list of the values given for this option.
        """
        return Option(self, key, shortName, longName, action)

    # Option class calls this to add the option into the list of options
    def _addOption(self, key, shortName, longName, opt):
        assert key not in self.optionDefs
        self.optionDefs += [(key, opt)]
        if shortName:
            assert shortName not in self.optionShortNames
            self.optionShortNames.update({shortName: opt})
        if longName:
            assert longName not in self.optionLongNames
            self.optionLongNames.update({longName: opt})

    # progName {{{2
    # return the name that the program was invoked as
    def progName(self):
        """Return the name of the running program as invoked.

        Returns the value of the first element of the list handed to the
        constructor, stripped of the leading path information.  Typically, the
        list is argv, so this function returns a trimmed version of argv[0],
        which is name of the program as invoked by the user. 
        """
        return self.invokedAs

    # setDescription {{{2
    def setDescription(self, title, desc):
        """Provide a detailed description.

        Use this to provide a detailed description of the command.  It is printed
        when the user asks for help specifically on this command.  The title
        will be highlighted when printed.  The description (desc) will be
        dedented before printing.  If a line in desc ends with a white space, it
        will be joined to the next line.  Each resulting line will be wrapped
        before it is printed.
        """
        self.title = title
        self.desc = desc

    # setErrorHandler {{{2
    def setErrorHandler(self, handler):
        """Provide an error handler.

        Any error in the command line will cause this error handler to be
        called.  It receives three arguments, the program name, the error
        message, and the help key.  If None is provided as the handler, the
        command line processor reverts to its default behavior, which it to
        print the message to stderr and exit.
        """
        self.errorHandler = handler

    # Private token methods {{{2
    # are any command line arguments left?
    def _tokensLeft(self):
        return len(self.args)

    # get the next command line argument
    def _nextToken(self):
        return self.args.pop(0)

    # is there another command line argument that is an option
    def _nextTokenIsOpt(self):
        return self._tokensLeft() and self.args[0][0] == '-'

    # is there another command line argument that is not an option
    def _nextTokenIsArg(self):
        return self._tokensLeft() and self.args[0][0] != '-'

    # is there another command line argument that is empty (just '-')
    # this signals the end of a command, when found it should be discarded
    def _nextTokenIsEmpty(self):
        return self._tokensLeft() and self.args[0] == '-'

    # push an argument to the front of the list of arguments remaining to be
    # processed
    def _pushToken(self, arg):
        return self.args.insert(0, arg)

    # process {{{2
    def process(self, args = None):
        """Process the command line.

        Runs through the command line calling the appropriate action functions
        whenever it identifies a global option or command.  The command line is
        given by 'args', which may either be specified here or on the
        constructor.
        """
        if args:
            self.args = copy(args)
        # the command line (args) must be specified either here or in constructor
        assert self.args != None
        (invokedPath, self.invokedAs) = os.path.split(self.args.pop(0))
        self.optionsGiven = {}
        self.argumentsGiven = []
        self.commandsGiven = []
        self.prereqs = set()

        processedACommand = False
        while self._tokensLeft():
            if self._nextTokenIsOpt() and not self._nextTokenIsEmpty():
                # process an option
                opt = self._nextToken()
                if processedACommand:
                    raise _Error("%s: options must be given before arguments" % opt)
                try:
                    self._processOption(self, opt)
                except KeyError:
                    raise _Error("%s: unknown option" % opt)
            else:
                arg = self._nextToken()
                if arg in self.commandDefs:
                    # process a command
                    cmd = self.commandDefs[arg]
                    cmd._processCommand(self, arg)
                    processedACommand = True
                else:
                    # not a command, must be an argument
                    # first push the argument back onto the list
                    self._pushToken(arg)
                    # then process the arguments
                    self.argumentsGiven = self._processArguments(self)
                    break
        # that should have consumed all tokens
        if self._tokensLeft():
            badToken = self._nextToken()
            if badToken[0] == '-':
                raise _Error("%s: unrecognized option" % badToken)
            elif len(self.argumentsGiven) or not len(self.commandDefs):
                raise _Error("%s: too many arguments" % badToken)
            else:
                raise _Error("%s: no such command" % badToken)
        if len(self.argumentsGiven) < self.minArgs:
            raise _Error("too few arguments, expected at least %d" % (self.minArgs))
        return (self.optionsGiven, self.argumentsGiven, self.commandsGiven, self.prereqs)

    # getOptions {{{2
    def getOptions(self):
        """Return the global options.

        Returns a dictionary that contains the values of all global options
        specified on the command line.  The key is the primary name for the
        option (the first name given).  The value is a list that contains the
        option arguments.  An empty list signifies that the option was given,
        but without arguments.
        """
        return self.optionsGiven

    # getArguments {{{2
    def getArguments(self):
        """Return the global arguments.

        Returns a list that contains the values of all global arguments
        specified on the command line.
        """
        return self.argumentsGiven

    # getCommands {{{2
    def getCommands(self):
        """Return the commands.

        Returns a list the commands that were specified by the user in the
        order specified.  Each item in the list is an object with three
        attributes: 'key', 'opts', and 'args'. 'key' is the primary name of the
        command. 'opts' is a dictionary containing the key and arguments for
        each option specified.  Finally, 'args' is the list of arguments
        specified for the command.
        """
        return self.commandsGiven

    # getPrereqs {{{2
    def getPrereqs(self):
        """Return the prerequisites.

        Returns the union of prerequisites for all of the commands specified
        on the command line.
        """
        return self.prereqs

    # setHelpParams {{{2
    def setHelpParams(self
        , key = None
        , sortKey = None
        , colWidth = None
        , pageWidth = None
        , alwaysSort = False
        , shouldExit = True
        , titleDecoration = None
    ):
        """Set parameters to adjust behavior of printHelp.

        Use this function to adjust the behavior of printHelp.  'key' is the key
        used by the user to ask for usage information.  Typically it would
        either be '--help' (if help is an option) or 'help' (if help is a
        command).  'colWidth' is the width of the name column.  If the name
        column is wider than this, it will generate a newline before printing
        the summary.  titleDecoration is a string with one or two characters.
        The first is used to underline the title, the second is used to overline
        the title.  If the character for a line is a space, the line is not
        printed.
        """
        self.helpKey = key
        self.helpSortKey = sortKey
        if colWidth:
            self.helpColWidth = colWidth
        if pageWidth:
            self.helpPageWidth = pageWidth
        if titleDecoration:
            self.helpTitleDecoration = titleDecoration
        self.helpAlwaysSort = alwaysSort
        self.helpShouldExit = shouldExit

    # printHelp {{{2
    def printHelp(self, key, opts={}, args=None, **extra):
        """Print usage information.

        Use this function as the action function to either the command or global
        option that is used to give user usage information about the program.
        Typically the global option would be ['--help', '-h'] or the command
        would be 'help'.
        """
        def printTitleAndDescription(self, obj):
            titleDecor = self.helpTitleDecoration
            if obj.title:
                if len(titleDecor) >= 2 and titleDecor[1]:
                    print(titleDecor[1]*len(obj.title))
                print(obj.title)
                if len(titleDecor) >= 1 and titleDecor[0]:
                    print(titleDecor[0]*len(obj.title))

            if obj.desc:
                out = []
                for line in textwrap.dedent(obj.desc).strip().split('\n'):
                    out += [line]
                    if len(line) == 0 or line[-1] != ' ':
                        # last character is not a space
                        # print accumulated line and start a new one
                        print(textwrap.fill(
                            ''.join(out)
                          , width=self.helpPageWidth
                        ))
                        out = []
                print(textwrap.fill(''.join(out), width=self.helpPageWidth))

        wrapper = textwrap.TextWrapper(
            width=self.helpPageWidth
          , subsequent_indent=(self.helpColWidth+6)*' '
        )
        def printSummary(names, argDesc, optDesc):
            tokens = ', '.join(names)
            if argDesc:
                tokens += ' ' + argDesc
            width = len(tokens)
            # may want to enhance this to take a list for the option
            # description, and if a list is given, then each item in list is
            # wrapped separately.
            if width > self.helpColWidth:
                print('    %s' % (tokens))
                print(wrapper.fill('    %s  %s' % (self.helpColWidth*' ', optDesc)))
            else:
                print(wrapper.fill(
                    '    %*s  %s' % (-self.helpColWidth, tokens, optDesc)
                ))

        def printOptions(optionDefs, sort):
            if sort:
                options = sorted(optionDefs)
            else:
                options = optionDefs
            for key, opt in options:
                # skip hidden options (those that do not have summaries)
                if not opt.sum:
                    continue
                names = []
                if opt.shortName:
                    names += ['-' + opt.shortName]
                if opt.longName:
                    names += ['--' + opt.longName]
                printSummary(names, opt.argDesc, opt.sum)

        sort = self.helpAlwaysSort or (opts and self.helpSortKey in opts)
        if args:
            for arg in args:
                # process a command
                try:
                    cmd = self.commandDefs[arg]
                except KeyError:
                    raise _Error("%s: unknown command" % arg)
                else:
                    printTitleAndDescription(self, cmd)

                    items = [self.invokedAs]
                    if len(self.optionDefs) > 0:
                        items += ['[<global options>]']
                    items += [cmd.names[0]]
                    if len(cmd.optionDefs) > 0:
                        items += ['[<command options>]']
                    if cmd.maxArgs > 0 or cmd.maxArgs == None:
                        if cmd.argDesc:
                            items += [cmd.argDesc]
                        elif cmd.minArgs == 0:
                            items += ['[<arguments>]']
                        else:
                            items += ['<arguments>']
                    print("Usage: %s\n" % ' '.join(items))

                    if len(cmd.names) > 1:
                        print("Aliases: %s\n" % ', '.join(cmd.names))

                    if len(cmd.optionDefs) > 0:
                        print("Command Options:")
                        printOptions(cmd.optionDefs, sort)
                        print('')

                    if len(self.optionDefs) > 0 and self.helpKey:
                        print(textwrap.fill(
                            ' '.join([
                                "Use '%s %s'" % (self.invokedAs, self.helpKey)
                              , 'for information on the global options.'
                            ])
                          , width=self.helpPageWidth
                        ))
        else:
            printTitleAndDescription(self, self)

            items = [self.invokedAs]
            if len(self.optionDefs) > 0:
                items += ['[options]']
            if self.maxArgs is None or self.maxArgs > 0:
                if self.argDesc:
                    items += [self.argDesc]
                elif self.minArgs == 0:
                    items += ['[<arguments>]']
                else:
                    items += ['<arguments>']
            if len(self.commandDefs) > 0:
                items += ['<command ...>']
            print("Usage: %s" % ' '.join(items))

            if len(self.commandDefs) > 0:
                print("\nCommands:")
                if sort:
                    commandNames = sorted(self.commandNames)
                else:
                    commandNames = self.commandNames
                for cmdName in commandNames:
                    cmd = self.commandDefs[cmdName]
                    printSummary(cmd.names, cmd.argDesc, cmd.sum)
                if self.helpKey:
                    print('')
                    print(textwrap.fill(
                        ' '.join([
                            "Use '%s %s <cmd>'" % (self.invokedAs, self.helpKey)
                          , 'for more detailed information on a specific command.'
                        ])
                      , width=self.helpPageWidth
                    ))

            if len(self.optionDefs) > 0:
                print("\nOptions:")
                printOptions(self.optionDefs, sort)
                print('')
        if self.helpShouldExit:
            sys.exit()

# Option Class (private) {{{1
class Option(_Argument):
    """Create an option.

    Options are command line arguments that start with '-'.

    Do not create objects of this class directly.  Option objects are created
    for you using the option() method of command or command line processor
    objects.  If called as a method of the command line processor itself, it
    creates a global option.  If called as a method of a command, it creates an
    option of that command.
    """
    def __init__(self, parent, key, shortName = None, longName = None, action = None):
        if shortName:
            assert shortName[0] != '-'
            assert len(shortName) == 1
        if longName:
            assert longName[0] != '-'
        else:
            assert shortName
        parent._addOption(key, shortName, longName, self)
        self.key = key
        self.shortName = shortName
        self.longName = longName
        if action:
            assert callable(action)
        self.action = action
        self.sum = ''
        self.minArgs = 0
        self.maxArgs = 0
        self.argDesc = None
        self.argFilter = None
        self.argForm = None

    def _processOption(*args):
        raise NotImplementedError

    def names(self):
        """
        Return names as a list.

        Useful for generating messages.  For example:
            print("Must not use %s on a full moon." % (' or '.join(opt.names()))
        """
        return [
            nm
            for nm in ['--'+self.longName, '-'+self.shortName]
            if nm != None
        ]

# Command Class (private) {{{1
class Command(_Argument):
    """Create an command.

    Do not create objects of this class directly.  Command objects are created
    for you using the addCommand() method of command line processor objects.
    """
    def __init__(self, clp, names, action, prereqs):
        if type(names) == str:
            names = [names]
        self.names = names
        for name in names:
            # command names must not begin with '-'
            assert name[0] != '-'
            assert name not in clp.commandDefs
            clp._addCommand(name, self)
        clp._addCommandName(names[0])
        self.clp = clp
        if action:
            assert callable(action)
        self.action = action
        self.prereqs = prereqs
        self.sum = ''
        self.desc = ''
        self.optionDefs = []
        self.optionShortNames = {}
        self.optionLongNames = {}
        self.minArgs = 0
        self.maxArgs = 0
        self.argDesc = None
        self.argFilter = None
        self.argForm = None

    def setDescription(self, title, desc):
        """Provide a Detailed Description

        Use this to provide a detailed description of the command.  It is
        printed when the user asks for help specifically on this command.  The
        title will be highlighted when printed.  The description (desc) will be
        dedented before printing.  If a line in desc ends with a white space, it
        will be joined to the next line.  Each resulting line will be wrapped
        before it is printed.
        """
        self.title = title
        self.desc = desc

    # user calls this to define a new option to this command
    def addOption(self, key, shortName = None, longName = None):
        """Define a new command option.

        'key' is the dictionary key you will use to access the value
        of this option, 'shortName' and 'longName' are the short and long forms
        of the option name, without any leading dashes.  The short name must be
        a single character.
        """
        return Option(self, key, shortName, longName, action=None)

    # Option class calls this to add the option into the list of options
    def _addOption(self, key, shortName, longName, opt):
        assert key not in self.optionDefs
        self.optionDefs += [(key, opt)]
        if shortName:
            self.optionShortNames.update({shortName: opt})
        if longName:
            self.optionLongNames.update({longName: opt})

    # a command has been found
    def _processCommand(self, clp, name):
        clp.prereqs.update(self.prereqs)
        self.optionsGiven = {}

        # first, process any options to this command
        while clp._nextTokenIsOpt() and not clp._nextTokenIsEmpty():
            arg = clp._nextToken()
            try:
                self._processOption(self.clp, arg)
            except KeyError:
                raise _Error("%s: unknown option for command '%s'" % (arg, name))

        # then, process the arguments to the command
        args = self._processArguments(clp, name)

        if clp._nextTokenIsEmpty():
            # empty option ('-') signifies end of this command, discard it and move on
            clp._nextToken()
        clp.commandsGiven += [_Item(
            key=self.names[0],
            opts=self.optionsGiven,
            args=args,
            action=self.action
        )]

# Active Command Line Processor {{{1
def activateCLP(clp):
    """Activate a command line processor.

    This function is only needed when more than one command line processor has
    been created and the calls to the command line processors are distributed
    widely throughout a program.  In this situation, you would activate the
    command line processor you would like to use.  It then becomes globally
    available through commandLineProcessor().  Subsequent calls to activateCLP()
    will deactivate the prior command line processor.  It can still be used; it
    is simply no longer available from the commandLineProcessor() function.
    """
    global _ActiveCLP
    _ActiveCLP = clp

def commandLineProcessor():
    """Return the active command line processor.

    This function is convenient when the calls to the command line processor
    are distributed widely throughout a program.  It returns the currently
    active command line processor object.
    """
    global _ActiveCLP
    return _ActiveCLP

# Create the default command line processor
activateCLP(CommandLineProcessor(sys.argv))

