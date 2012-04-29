"""Engineering Notation

Provides support for producing, reading, and translating numbers into and out of
engineering format.

Examples:
    Numbers in engineering notation:
        1MHz
        2.4G
        1uF
    Numbers in traditional notation:
        1e6
        2.4e9
        1e-6
"""

from string import atof, atoi
import re as RE

# define regular expressions use to identify numbers of various forms
_NumWithScaleFactorAndTrailingUnits = \
    RE.compile(r'\A([-+]?[0-9]*\.?[0-9]+)(([YZEPTGMKk_munpfazy])([a-zA-Z_]*))?\Z')
_NumWithExpAndTrailingUnits = \
    RE.compile(r'\A([-+]?[0-9]*\.?[0-9]+[eE][-+]?[0-9]+)([a-zA-Z_]*)\Z')
_NumWithScaleFactorAndLeadingUnits = \
    RE.compile(r'\A(\$)([-+]?[0-9]*\.?[0-9]+)([YZEPTGMKk_munpfazy])?\Z')
_NumWithExpAndLeadingUnits = \
    RE.compile(r'\A(\$)([-+]?[0-9]*\.?[0-9]+[eE][-+]?[0-9]+)\Z')
_NanWithTrailingUnits = \
    RE.compile(r'\A([-+]?(inf|nan))\b ?([a-zA-Z_]*)\Z', RE.IGNORECASE)
_NanWithLeadingUnits = \
    RE.compile(r'\A(\$)([-+]?(inf|nan))\Z', RE.IGNORECASE)

_ScaleFactors = {
    'Y' : (1e24,  'e24')
  , 'Z' : (1e21,  'e21')
  , 'E' : (1e18,  'e18')
  , 'P' : (1e15,  'e15')
  , 'T' : (1e12,  'e12')
  , 'G' : (1e9,   'e9')
  , 'M' : (1e6,   'e6')
  , 'K' : (1e3,   'e3')
  , 'k' : (1e3,   'e3')
  , '_' : (1,     '')
  , ''  : (1,     '')
  , 'm' : (1e-3,  'e-3')
  , 'u' : (1e-6,  'e-6')
  , 'n' : (1e-9,  'e-9')
  , 'p' : (1e-12, 'e-12')
  , 'f' : (1e-15, 'e-15')
  , 'a' : (1e-18, 'e-18')
  , 'z' : (1e-21, 'e-21')
  , 'y' : (1e-24, 'e-24')
}

_DefaultPrecision = 4
def setDefaultPrecision(prec):
    """Set the default precision.
       Precision is given in digits and must be positive.  A precision of zero
       corresponds to one significant figure.
    """
    global _DefaultPrecision
    _DefaultPrecision = prec

_Spacer = ''
def setSpacer(char=''):
    """Set the spacer character for toEngFmt().
       Can make this a space if you prefer a space between number and
       scalefactor/units, but if you add the space, the numbers you generate
       using toEngFmt() will not be recognized by fromEngFmt().
    """
    global _Spacer
    _Spacer = char

def isNaN(val):
    """Tests for not a number."""
    # math.isnan() is available from Python 2.6 on, this is only needed in
    # earlier versions.
    return str(val) == str(float('nan'))


def toEngFmt(num, units="", prec=-1):
    """Converts real numbers with units into easily readable form.

       Converts a number and optional units into a string.  For those numbers in
       range of the SI scale factors, the exponent is stripped off and replaced
       with a standard SI scale factor.
    """

    # precision must be non-negative
    if prec < 0:
        global _DefaultPrecision
        prec = _DefaultPrecision
    assert (prec >= 0)

    # check for infinities or NaN
    if num == float('inf') or num == float('-inf') or isNaN(num):
        if units:
            if units == "$":
                return units + str(num)
            return str(num) + ' ' + units # cannot use spacer here, because we cannot afford it to be empty
        else:
            return str(num)

    # convert into scientific notation with proper precision
    sNum = "%.*e" % (prec, num)
    sMant, sExp = sNum.split("e")
    exp = atoi(sExp)

    # define scale factors (eliminate the ones nobody recognizes)
    big = "KMGT"     #big = "KMGTPEZY"
    small = "munpfa" #small = "munpfazy"

    # find scale factor
    index = exp / 3
    shift = exp % 3
    sf = "e%d" % (exp - shift)
    if index == 0:
        sf = ""
    elif (index > 0):
        if index <= len(big):
            sf = big[index-1]
    else:
        index = -index
        if index <= len(small):
            sf = small[index-1]

    # move decimal point as needed
    if shift == 0:
        num = atof(sMant)
    elif (shift == 1):
        num = 10*atof(sMant)
    else:
        num = 100*atof(sMant)
    sMant = "%.*f" % (prec-shift, num)

    #remove trailing zeros (except if sMant does not contain a .)
    if sMant.find('.') >= 0:
        sMant = sMant.rstrip("0")  # pragma: no cover

    #remove trailing decimal point
    sMant = sMant.rstrip(".")

    if units == "$":
        return units + sMant + sf
    elif not units or units == "":
        return sMant + sf
    else:
        if len(sf) <= 1:
            return sMant + _Spacer + sf + units
        else:
            return sMant + sf + _Spacer + units

def toNumber(str):
    """Converts strings in engineering format into a real number and units.

       The real number and units are returned as a tuple.  If the argument is
       not recognized as a number, None is returned.
    """
    # with scale factor and trailing units
    match = _NumWithScaleFactorAndTrailingUnits.match(str)
    if match:
        number, scaleFactorAndUnits, scaleFactor, units = match.groups()
        if scaleFactor:
            number = float(number)*_ScaleFactors[scaleFactor][0]
        else:
            number = float(number)
        if units == None:
            units = ''
        return number, units
    # with exponent and trailing units
    match = _NumWithExpAndTrailingUnits.match(str)
    if match:
        number, units = match.groups()
        if units == None:
            units = ''
        return float(number), units
    # with scale factor and leading units ($)
    match = _NumWithScaleFactorAndLeadingUnits.match(str)
    if match:
        units, number, scaleFactor = match.groups()
        if scaleFactor:
            number = float(number)*_ScaleFactors[scaleFactor][0]
        else:
            number = float(number)
        if units == None:
            units = ''
        return number, units
    # with exponent and leading units ($)
    match = _NumWithExpAndLeadingUnits.match(str)
    if match:
        units, number = match.groups()
        if units == None:
            units = ''
        return float(number), units
    match = _NanWithTrailingUnits.match(str)
    if match:
        number, ignore, units = match.groups()
        if units == None:
            units = ''
        return float(number), units
    match = _NanWithLeadingUnits.match(str)
    if match:
        units, number, ignore = match.groups()
        if units == None:
            units = ''
        return float(number), units
    return None

def fromEngFmt(str, stripUnits = True):
    """Converts a string that contains a number in engineering format
       into a string that contains the same number formatted traditionally (the
       number returned has all the precision of the one provided, the scale
       factor is just converted to 'E' notation.  If stripUnits is true, a
       simple string is returned.  Otherwise, a tuple is return that contains
       (number, units).
    """
    # with scale factor and trailing units
    match = _NumWithScaleFactorAndTrailingUnits.match(str)
    if match:
        trailingUnits = True
        number, scaleFactorAndUnits, scaleFactor, units = match.groups()
        if scaleFactor:
            number = number+_ScaleFactors[scaleFactor][1]
    else:
        # with exponent and trailing units
        match = _NumWithExpAndTrailingUnits.match(str)
        if match:
            trailingUnits = True
            number, units = match.groups()
        else:
            # with scale factor and leading units ($)
            match = _NumWithScaleFactorAndLeadingUnits.match(str)
            if match:
                trailingUnits = False
                units, number, scaleFactor = match.groups()
                if scaleFactor:
                    number = number+_ScaleFactors[scaleFactor][1]
            else:
                # with exponent and leading units ($)
                match = _NumWithExpAndLeadingUnits.match(str)
                if match:
                    trailingUnits = False
                    units, number = match.groups()
                else:
                    match = _NanWithTrailingUnits.match(str)
                    if match:
                        trailingUnits = True
                        number, ignore, units = match.groups()
                    else:
                        match = _NanWithLeadingUnits.match(str)
                        if match:
                            trailingUnits = False
                            units, number, ignore = match.groups()
                        else:
                            return None

    if stripUnits:
        return number
    else:
        return (number, units)

def isNumber(str):
    """Tests whether string is a number in either traditional or engineering formats."""
    if _NumWithScaleFactorAndTrailingUnits.match(str):
        return True
    if _NumWithExpAndTrailingUnits.match(str):
        return True
    if _NumWithScaleFactorAndLeadingUnits.match(str):
        return True
    if _NumWithExpAndLeadingUnits.match(str):
        return True
    if _NanWithTrailingUnits.match(str):
        return True
    if _NanWithLeadingUnits.match(str):
        return True
    return False

def stripUnits(str):
    """Returns the number as given except any units are removed."""
    match = _NumWithScaleFactorAndTrailingUnits.match(str)
    if match:
        number, scaleFactorAndUnits, scaleFactor, units = match.groups()
        if scaleFactor and scaleFactor != '_':
            return number+scaleFactor
        else:
            return number
    match = _NumWithExpAndTrailingUnits.match(str)
    if match:
        number, units = match.groups()
        return number
    match = _NumWithScaleFactorAndLeadingUnits.match(str)
    if match:
        units, number, scaleFactor = match.groups()
        if scaleFactor and scaleFactor != '_':
            return number+scaleFactor
        else:
            return number
    match = _NumWithExpAndLeadingUnits.match(str)
    if match:
        units, number = match.groups()
        return number
    match = _NanWithTrailingUnits.match(str)
    if match:
        number, ignore, units = match.groups()
        return number
    match = _NanWithLeadingUnits.match(str)
    if match:
        units, number, ignore = match.groups()
        return number
    return None

#
# The following two functions are used to convert numbers found in
# heterogeneous strings (strings that contain numbers within a larger block of
# text).  Previous functions that translate numbers assume that the string
# contains only a number and no other text.
#
# This is a challenging problem and my solution is somewhat dubious.  I
# really struggled with something like +1.034e-029Hz because it can either be
# treated as 1.034e-029 with units of Hz, or as 1.034 - 29 where 1.034 has
# units of e.  I tried to overcome the problem by writing
# _EmbeddedNumberWithScaleFactor such that it requires a scale factor but will
# accurately identify such a number within text.  It is used in allFromEngFmt
# where it is not necessary to match a number without scale factors because we
# only map the ones with scale factors.

#_EmbeddedNumberWithScaleFactor = RE.compile(r'([-+]?[0-9]*\.?[0-9]+)([YZEPTGMKk_munpfazy])([a-zA-Z_]*)([^-+0-9a-zA-Z.]|\Z)')
_EmbeddedNumberWithScaleFactor = RE.compile(r'([-+]?[0-9]*\.?[0-9]+)([YZEPTGMKk_munpfazy])([a-zA-Z_]*)([^-+0-9]|\Z)')
    # I replaced the first version of numberWithScaleFactor4 because it did not
    # recognize "1mA." (1mA at the end of a sentence).  I did not really
    # understand why letters, and periods could not follow a number, so I
    # removed them, but it is clear the [-+0-9] must remain to avoid matches
    # with 1E2, 1E-2, 1E+2.
_EmbeddedNumberWithoutScaleFactor = RE.compile(r'(?:\A|(?<=[^a-zA-Z.0-9]))(([0-9]*\.?[0-9]+)[eE][-+]?[0-9]+)([a-zA-Z_]*)\b')

def allToEngFmt(str):
    """Replace all occurrences of numbers found in a string into engineering
       format.
    """
    out = ''
    prevEnd = 0
    for match in _EmbeddedNumberWithoutScaleFactor.finditer(str):
        beginMatch = match.start(1)
        number, mantissa, units = match.groups()
        #digits = len(mantissa)-2
        try:
            newNumber = toEngFmt(float(number), units)
        except ValueError:
            newNumber = number + units
            # something unexpected went wrong, but this is unessential, so
            # recover and move on.
            if __debug__:
                print "EXCEPTION: mis-translation of number"
        out += str[prevEnd:beginMatch] + newNumber
        prevEnd = match.end(3)
    out += str[prevEnd:]
    return out

def allFromEngFmt(str):
    """Replace all occurrences of numbers found in a string into traditional
       format.
    """
    out = ''
    prevEnd = 0
    for match in _EmbeddedNumberWithScaleFactor.finditer(str):
        beginMatch = match.start(1)
        mantissa, scaleFactor, units, discard = match.groups()
        if float(mantissa) == 0:
            number = '0'
        else:
            number = mantissa + _ScaleFactors[scaleFactor][1]
        out += str[prevEnd:beginMatch] + number + units
        prevEnd = match.end(3)
    out += str[prevEnd:]
    #print "Out: '%s" % out
    return out
