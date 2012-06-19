#!/usr/bin/env python
#
# Manpage generator for Engineering Calculator

# Imports {{{1
import re
from textwrap import wrap, fill, dedent
from ec import actionsToUse as actions

# Configuration {{{1
complexNumbers = True

# Globals {{{1
italicsRegex = re.compile(r'#\{([^}]+)\}')
boldRegex = re.compile(r'@\{([^}]+)\}')
document = []

# Classes {{{1
# ManPage base class {{{2
class ManPage():
    def __init__(self, text):
        raise NotImplementedError

    def formatText(self, text):
        # get rid of leading indentation and break into individual lines
        lines = dedent(text).strip().splitlines()
        gatheredLines = []
        for line in lines:
            if line.strip() == r'\verb{':
                # start of verbatim region
                gatheredLines += ['.nf']
            elif line.strip() == '}':
                # end of verbatim region
                gatheredLines += ['.fi']
            else:
                line = italicsRegex.sub(r'\\fI\1\\fP', line)
                line = boldRegex.sub(r'\\fB\1\\fP', line)
                gatheredLines += [line]
        return '\n'.join(gatheredLines)

    def escapeQuotes(self, text):
        return text.replace('"', '""')

# Comment class {{{2
class Comment(ManPage):
    def __init__(self, comment):
        global document
        lines = dedent(comment).strip().splitlines()
        document += [r'\" %s' % line for line in lines]

# Title class {{{2
class Title(ManPage):
    def __init__(self, title, section, date, source=None, manual=None):
        document.append(
            '.TH {title} {section} {date} {source} {manual}'.format(
                title=title
              , section=section
              , date=date
              , source=source if source else ''
              , manual=manual if manual else ''
            )
        )

# Section class {{{2
class Section(ManPage):
    def __init__(self, title):
        document.append('.SH {0}'.format(self.escapeQuotes(title.upper())))

# SubSection class {{{2
class SubSection(ManPage):
    def __init__(self, title):
        document.append('.SS {0}'.format(self.escapeQuotes(title)))

# Text class {{{2
class Text(ManPage):
    def __init__(self, text):
        document.append(self.formatText(text))

# Paragraph class {{{2
class Paragraph(ManPage):
    def __init__(self, text):
        document.append('.PP')
        document.append(self.formatText(text))

# IndentedParagraph class {{{2
class IndentedParagraph(ManPage):
    def __init__(self, title, text):
        if title:
            document.append('.IP "{0}"'.format(
                self.formatText(self.escapeQuotes(title))
            ))
        else:
            document.append('.IP')
        document.append(self.formatText(text))

# Listing class {{{2
class Listing(ManPage):
    def __init__(self, listing):
        document.append('.nf')
        document.append('.RS')
        document.append(self.formatText(listing))
        document.append('.RE')
        document.append('.fi')

# Table class {{{2
class Table(ManPage):
    def __init__(self, table):
        document.append('.TS')
        document.append(self.formatText(table))
        document.append('.TE')

# Email class {{{2
class Email(ManPage):
    def __init__(self, text):
        document.append('.BR "{0}"'.format(self.formatText(text)))

# Document {{{1
# Front matter {{{2
from datetime import date
Title(title='ec', section='1', date='%s' % date.today())
Comment("""
ec.1 - the *roff document processor source for the ec manual

Author:
Ken Kundert
ec@shalmirane.com .

You can view a formatted version of this man page using:
   tbl ec.1 | nroff -man | less
or
   pdfroff -t -man ec.1 > ec.pdf
   evince ec.pdf
""")
Section('Name')
Paragraph('ec - An engineering calculator')
Section('Syntax')
Paragraph('@{ec} [#{options}] [#{scripts ...}]')
# Description {{{2
Section('Description')
Paragraph('''
    @{ec} is a stack-based (RPN) engineering calculator with a text-based user 
    interface that is intended to be used interactively.
''')
Paragraph('''
    If run with no arguments, an interactive session is started.  If arguments
    are present, they are tested to see if they are filenames, and if so, the
    files are opened and the contents are executed as a script.  If they are not
    file names, then the arguments themselves are treated as scripts and
    executed directly. The scripts are run in the order they are specified.  In
    this case an interactive session would not normally be started, but if the
    interactive option is specified, it would be started after all scripts have
    been run.
''')
Paragraph('''
    The contents of #{~/.ecrc}, #{./.ecrc}, and the start up file will be run 
    upon start up if they exist, and then the stack is cleared.
''')
# Options {{{2
Section(title='Options')
IndentedParagraph('-i, --interactive', text='''
    Open an interactive session.
''')
IndentedParagraph(title='-x, --printx', text='''
    Print value of x register upon termination, ignored with interactive
    sessions.
''')
IndentedParagraph(title='-s, --startup file', text='''
    Run commands from file to initialize calculator before any script or
    interactive session is run, stack is cleared after it is run.
''')
IndentedParagraph(title='-c, --nocolor', text='''
    Do not use colors in the output.
''')
IndentedParagraph(title='-h, --help', text='''
    Print the usage and exit.
''')
# Stack {{{2
Section(title='Stack')
Paragraph('''
    As you enter numbers they are pushed onto a stack.  The most recent member
    of the stack is referred to as the #{x} register and the second most recent
    is the #{y} register.  All other members of the stack are unnamed.
    Operators consume numbers off the stack to use as operands and then they
    push the results back on the stack.  The operations are performed
    immediately and there is no use of parentheses to group calculations.  Any
    intermediate results are stored on the stack until needed.  For example,
''')
Listing('''
    4
    6
    +
''')
Paragraph('''
    In this case 4 gets pushed on to the stack first to become #{x}. Then 6 gets 
    pushed on to the stack to become #{x}, which makes 4 #{y}. Finally, 
    + pulls both off the stack, sums them, and then pushes the result of 10 back 
    onto the stack. The stack is left with only one number on it, 10.
''')
Paragraph('''
    After each line @{ec} responds by printing the value of the #{x} register.  
    Thus the above example would actually look like this:
''')
Listing('''
    @{0}: 4
    @{4}: 6
    @{6}: +
    @{10}:
''')
Paragraph('''
    The benefit of the stack is that it allows you to easily store temporary
    results while you perform your calculation. For example, to evaluate (34 -
    61)*(23 - 56) you would use:
''')
Listing('''
    @{0}: 34
    @{34}: 61
    @{61}: -
    @{-27}: 23
    @{23}: 56
    @{56}: -
    @{-33}: *
    @{891}:
''')
Paragraph('''
    Notice that you entered the numbers as you saw them in the formula you were
    evaluating, and there was no need to enter parentheses, however the
    operators were rearranged in order to express the precedence of the
    operations.
''')
Paragraph('''
    It is not necessary to type enter after each number or operator. You can
    combine them onto one line and just type enter when you would like to see
    the result:
''')
Listing('''
    @{0}: 34 61 - 23 56 - *
    @{891}:
''')
Paragraph('''
    Furthermore, it is not necessary to type a space between a number and most 
    operators. For example, the above could be entered as:
''')
Listing('''
    @{0}: 34 61- 23 56- *
    @{891}:
''')
Paragraph('''
    You can print the entire stack using #{stack}, and clear it using 
    #{clstack}. For example,
''')
Listing('''
    @{0}: 1 2 3 stack
          3
       #{y}: 2
       #{x}: 1
    @{3}: clstack
    @{0}: stack
    @{0}:
''')
# Real Numbers {{{2
Section('Real Numbers')
Paragraph('''
    Numbers can be entered using normal integer, floating point, and scientific
    notations. For example,
''')
Listing('''
    42
    3.141592
    2.998e8
    13.80651e-24
''')
Paragraph('''
    In addition, you can also use the normal SI scale factors to represent
    either large or small numbers without using scientific notation.
''')
Table('''
    tab(;);
    llcll.
    ;;Y;1e24;yotta
    ;;Z;1e21;zetta
    ;;E;1e18;exa
    ;;P;1e15;peta
    ;;T;1e12;terra
    ;;G;1e9;giga
    ;;M;1e6;mega
    ;;k, K;1e3;kilo
    ;;\&_;unity;1
    ;;m;1e-3;milli
    ;;u;1e-6;micro
    ;;n;1e-9;nano
    ;;p;1e-12;pico
    ;;f;1e-15;fempto
    ;;a;1e-18;atto
    ;;z;1e-21;zepto
    ;;y;1e-24;yocto
''')
Paragraph('''
    For example, 10M represents 1e7 and 8.8p represents 8.8e-12.
''')
Paragraph('''
    Optionally, numbers can be combined with simple units. For example,
''')
Listing('''
    10KHz
    3.16pF
    2.5_V
    4.7e-10F
''')
Paragraph('''
    In this case the units must be simple identifiers (must not contain special 
    characters). For complex units, such as "rads/s", or for numbers that do not 
    have scale factors, it is possible to attach units to a number in the #{x} 
    register by entering a quoted string.
''')
Listing('''
    @{0}: 6.626e-34
    @{662.6e-36}: "J-s"
    @{662.6e-36 J-s}: 5 "V"
    @{5 V}:
''')
Paragraph('''
    The dollar sign ($) is a special unit that is given before the number.
''')
Listing('''
    $100K
''')
Paragraph('''
    @{ec} takes a conservative approach to units. You can enter them and it
    remembers them, but they do not survive any operation where the resulting
    units would be in doubt.  In this way it displays units when it can, but
    should never display incorrect or misleading units. For example:
''')
Listing('''
    @{0}: 100MHz
    @{100 MHz}: 2pi*
    @{628.32M}:
''')
Paragraph('''
    You can display real numbers using one of three available formats, #{fix},
    #{sci}, or #{eng}. These display numbers using fixed point notation (a fixed
    number of digits to the right of the decimal point), scientific notation (a
    mantissa and an exponent), and engineering notation (a mantissa and an SI
    scale factor).  You can optionally give an integer immediately after the
    display mode to indicate the desired precision.  For example,
''')
Listing('''
    @{0}: 1000
    @{1K}: fix2
    @{1000.00}: sci3
    @{1.000e+03}: eng4
    @{1K}: 2pi*
    @{6.2832K}:
''')
Paragraph('''
    Notice that scientific notation always displays the specified number of
    digits whereas engineering notation suppresses zeros at the end of the
    number.
''')
Paragraph('''
    When displaying numbers using engineering notation, @{ec} does not use the
    full range of available scale factors under the assumption that the largest
    and smallest would be unfamiliar to most people. For this reason, @{ec} only
    uses the most common scale factors when outputting numbers (T, G, M, K, m,
    u, n, p, f, a).
''')
# Integers {{{2
Section('Integers')
Paragraph('''
    You can enter integers in either hexadecimal (base 16), decimal (base 10), 
    octal (base 8), or binary (base 2). You can use either programmers notation
    (leading 0) or Verilog notation (leading ') as shown in the examples below:
''')
Table('''
    tab(;);
    lrl.
    ;0xFF;hexadecimal
    ;99;decimal
    ;0o77;octal
    ;0b1101;binary
    ;'hFF;Verilog hexadecimal
    ;'d99;Verilog decimal
    ;'o77;Verilog octal
    ;'b1101;Verilog binary
''')
Paragraph('''
    Internally, @{ec} represents all numbers as double-precision real numbers.
    To display them as decimal integers, use #{fix0}. However, you can display
    the numbers in either base 16 (hexadecimal), base 10 (decimal), base 8
    (octal) or base 2 (binary)  by setting the display mode.  Use either #{hex},
    #{fix0}, #{oct}, #{bin}, #{vhex}, #{vdec}, #{voct}, or #{vbin}. In each of
    these cases the number is rounded to the closest integer before it is
    displayed. Add an integer after the display mode to control the number of
    digits. For example:
''')
Listing('''
    @{0}: 1000
    @{1K}: hex
    @{0x3b8}: hex8
    @{0x000003b8}: hex0
    @{0x3b8}: voct
    @{'o1750}:
''')
# Complex Numbers {{{2
if complexNumbers:
    Section('Complex Numbers')
    Paragraph('''
        @{ec} provides limited support for complex numbers. Two imaginary constants
        are available that can be used to construct complex numbers, #{j} and
        #{j2pi}. In addition, two functions are available for converting complex
        numbers to real, #{mag} returns the magnitude and #{ph} returns the phase.
        They are unusual in that they do not replace the value in the #{x} register
        with the result, instead they simply push either the magnitude of phase into
        the #{x} register, which pushes the original complex number into the #{y}
        register. For example,
    ''')
    Listing('''
        @{0}: 1 j +
        @{1 + j1}: mag
        @{1.4142}: pop
        @{1 + j1}: ph
        @{45 degs}: stack
           #{y}: 45 degs
           #{x}: 1 + j1
        @{45 degs}:
    ''')
    Paragraph('''
        Only a small number of functions actually support complex numbers; currently
        only #{exp} and #{sqrt}. However, most of the basic arithmetic operators
        support complex numbers.
    ''')
# Constants {{{2
Section('Constants')
Paragraph('''
    @{ec} provides several useful mathematical and physical constants that are
    accessed by specifying them by name. The physical constants are given in MKS
    units. The available constants include:
''')
Table('''
    tab(;);
    lrl.
    ;pi;3.141592...
    ;2pi;6.283185...
    ;rt2;square root of two: 1.4142...
    ;j;the imaginary unit, sqrt(-1)
    ;j2pi;j6.283185...
    ;h;Plank's contant: 6.6260693e-34 J-s
    ;k;Boltzmann's contant: 1.3806505e-23 J/K
    ;q;charge of an electron: 1.60217653e-19 Coul
    ;c;speed of light in a vacuum: 2.99792458e8 m/s
    ;0C;0 Celsius in Kelvin: 273.15 K
    ;eps0;permittivity of free space: 8.854187817e-12 F/m
    ;mu0;permeability of free space: 4e-7*pi N/A^2
''')
Paragraph('''
    As an example of using the predefined constants, consider computing the
    thermal voltage, kT/q.
''')
Listing('''
    @{0}: k 27 0C + * q/
    @{25.865m}:
''')
# Variables {{{2
Section('Variables')
Paragraph('''
    You can store the contents of the #{x} register to a variable by using an 
    equal sign followed immediately by the name of the variable. To recall it, 
    simply use the name. For example,
''')
Listing('''
    @{0}: 100MHz =freq
    @{100 MHz}: 2pi* "rads/s" =omega
    @{628.32 Mrads/s}: 1pF =cin
    @{1 pF}: 1 omega cin* /
    @{1.5915K}:
''')
Paragraph('''
    You can display all known variables using #{vars}. If you did so immediately 
    after entering the lines above, you would see:
''')
Listing('''
    @{1.5915K}: vars
      #{Rref}: 50 Ohms
      #{cin}: 1 pF
      #{freq}: 100 MHz
      #{omega}: 628.32 Mrads/s
''')
Paragraph('''
    Choosing a variable name that is the same as a one of a built-in command or
    constant causes the built-in name to be overridden. Be careful when doing
    this as once a built-in name is overridden it can no longer be accessed. 
''')
Paragraph('''
    Notice that a variable #{Rref} exists that you did not create. This is a
    predefined variable that is used in dBm calculations. You are free to change
    its value if you like.
''')
# Operators, Functions, Numbers and Commands {{{2
Section('Operators, Functions, Numbers and Commands')
Paragraph('''
    In the following descriptions, optional values are given in brackets ([])
    and values given in angle brackets (<>) are not to be taken literally (you
    are expected to choose a suitable value). For example "fix[<#{N}>]" can
    represent "fix" or "fix4", but not "fixN".
''')
for action in actions:
    if action.description:
        if hasattr(action, 'category'):
            SubSection(action.description % (action.__dict__))
        else:
            summary = action.getSummary()
            synopsis = action.getSynopsis()
            aliases = action.getAliases()
            if aliases:
                if len(aliases) > 1:
                    aliases = 'aliases: %s' % ', '.join(aliases)
                else:
                    aliases = 'alias: %s' % ', '.join(aliases)
            else:
                aliases = ''
            IndentedParagraph(action.description % (action.__dict__), summary)
            if synopsis:
                IndentedParagraph(None, 'synopsis: %s' % synopsis)
            if aliases:
                IndentedParagraph(None, aliases)

# Help {{{2
Section('Help')
Paragraph('''
   You can use help to get a summary of the various features available in EC
   along with a short summary of each feature. For more detailed information,
   you can use '?'.  If you use '?' you will get a list of all available help
   topics. If you use '?<#{topic}>' where #{topic} us either a symbol or a
   name, you will get a detailed description of that topic.
''')

# Initialization {{{2
Section('Initialization')
Paragraph('''
At start up @{ec} reads and executes commands from files.  It first tries
'~/.ecrc' and runs any commands it contains if it exists.  It then tries
'./.ecrc' if it exists.  Finally it runs the startup file specified on the
command line (with the @{-s} or @{--startup} option).  It is common to put your
generic preferences in '~/.exrc'.  For example, if your are a physicist with a
desire for high precision results, you might use:
''')
Listing('''
eng6
h 2pi / "J-s" =hbar
''')
Paragraph('''
    This tells @{ec} to use 6 digits of resolution and predefines #{hbar} as a
    constant.  After all of the startup files have been processed, the stack is
    cleared.
''')

# Scripting {{{2
Section('Scripting')
Paragraph('''
    Command line arguments are used as scripts. If the argument corresponds to
    an existing file, the file is opened its contents are executed. Otherwise,
    the argument itself is executed (often it needs to be quoted to protect its
    contents from being interpreted by the shell). The arguments are executed in
    the order given. When arguments are given the calculator by default does not
    start an interactive session and does not produce output.  If you wish to
    use an interactive session after scripts have been evaluated, use the @{-i}
    or #{--interactive} command line options. If you wish to produce output,
    which you certainly will if you are not using the interactive session, you
    must add print commands to your script, which is a double-quoted string. For
    example,
''')
Listing('''
    @{0}: `Hello world!`
    Hello world!
    @{0}:
''')
Paragraph('''
    You can add the values of registers and variables to your print statements.
    #{$N} prints out the value of register #{N}, where 0 is the #{x} register,
    1 is the #{y} register, etc. #{$name} will print the value of a variable
    with the given name. Alternatively, you can use #{${N}} and #{${name}} to
    disambiguate the name or number. To print a dollar sign, use #{$$}.  To
    print a newline or a tab, use #{\en} and #{\et}. For example,
''')
Listing('''
    @{0}: 100MHz =freq
    @{100 MHz}: 2pi* "rads/s"
    @{628.32 Mrads/s}: `$freq corresponds to $0.`
    100 MHz corresponds to 628.32 Mrads/s.
    @{628.32 Mrads/s}:
''')
Paragraph('''
    To illustrate the use of a script, assume that a file named #{lg} exists and
    contains a calculation for the loop gain of a PLL,
''')
Listing('''
    =freq
    88.3u "V/per" =Kdet
    9.07G "Hz/V" =Kvco
    2 =M
    8 =N
    2 =F
    freq 2pi* "rads/s" =omega
    Kdet Kvco* omega/ M/ =a
    N F* =f
    a f* =T
    `Open loop gain = $a\enFeedback factor = $f\enLoop gain = $T`
''')
Paragraph('''
    Notice that it starts by saving the value in the #{x} register to the
    variable #{freq}. This script would be run as:
''')
Listing('''
    > ec 1KHz lg
    Open loop gain = 63.732
    Feedback factor = 16
    Loop gain = 1.0197K
''')
Paragraph('''
    The first argument does not correspond to a file, so it is executed as a
    script.  It simply pushes 1KHz onto the stack. The second argument does
    correspond to a file, so its contents are executed. The script ends with a
    print command, so the results are printed to standard output as the script
    terminates.
''')
Paragraph('''
    Generally if you do not issue a print command in a script, there is no
    output.  However, if you specify the @{-x} or @{--printx} command line
    option the value of the #{x} register is printed upon termination. An
    example of how this could be useful is:
''')
Listing('''
    > ec -x 1.52e-11F
    15.2 pF
''')
Paragraph('''
    In this example, @{ec} is used simply to convert a number into the more
    readable engineering notation.
''')
Paragraph('''
    One issue with command line scripting that you need to be careful of is that
    if an argument is a number with a leading minus sign it will be mistaken to
    be a command line option. To avoid this issue, specify the number without
    the minus sign and follow it with #{chs}. For example,
''')
Listing('''
    > ec -x -30 dbmv 
    ec: -30 dbmv: unknown option.
    > ec -x 30 chs dbmv 
    10 mV
''')

# Diagnostics {{{2
Section('Diagnostics')
Paragraph('''
    If an error occurs on a line, an error message is printed and the stack is
    restored to the values it had before the line was entered. So it is almost
    as if you never typed the line in at all.  The exception being that any
    variables or modes that are set on the line before the error occurred are
    retained.  For example,
''')
Listing('''
    @{0}: 1KOhms =r
    @{1 KOhms}: 100MHz =freq 1pF = c
    =: unrecognized
    @{1 KOhms}: stack
      #{x}: 1 KOhms
    @{1 KOhms}: vars
      #{Rref}: 50 Ohms
      #{freq}: 100MHz
      #{r}: 1 KOhms
''')
Paragraph('''
    The error occurred when trying to assign a value to #{c} because a space was
    accidentally left between the equal sign and the variable name.  Notice that
    100MHz was saved to the variable #{freq}, but the stack was restored to the
    state it had before the offending line was entered.
''')

# Author {{{2
Section('Author')
Paragraph('''
    Ken Kundert
''')
Paragraph('''
    Send bug reports and enhancement requests to:
''')
Email('''
    ec@shalmirane.com
''')

# Print the document {{{2
try:
    with open('ec.1', 'w') as fp:
        fp.write('\n'.join(document) + '\n')
except (IOError, OSError), err:
    exit("%s: %s." % (err.filename, err.strerror))
