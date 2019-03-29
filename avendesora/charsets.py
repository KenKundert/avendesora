"""Character Sets

Defines strings of characters and an exclude function that can be used either as
the alphabets for you character-base passwords or as building blocks used to
construct a new alphabet for you passwords.

Example:
To create an alphabet with all characters except tabs use either:
    'alphabet': exclude(PRINTABLE, '\t')
or:
    'alphabet': ALPHANUMERIC + PUNCTUATION + ' '
"""


# Exclude function
def exclude(chars, exclusions):
    """Exclude Characters

    Use this to remove characters from a character set.

    :arg str chars:
        Character set to strip.

    :arg str exclusions:
        Characters to remove from character set.

    Example::

        >>> exclude('ABCDEF', 'AEF')
        'BCD'

    """
    try:
        # this version is compatible with python3
        return chars.translate(str.maketrans('', '', exclusions))
    except AttributeError:
        # this version is compatible with python2
        return chars.translate(None, exclusions)


# Character sets
# Use these to construct alphabets by summing together the ones you want.

# Lower case ASCII letters.
LOWERCASE = "abcdefghijklmnopqrstuvwxyz"

# Upper case ASCII letters.
UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Upper and lower case ASCII letters.
LETTERS = LOWERCASE + UPPERCASE

# ASCII digits.
DIGITS = "0123456789"

# ASCII letters and digits.
ALPHANUMERIC = LETTERS + DIGITS

# Hexidecimal digits.
HEXDIGITS = "0123456789abcdef"

# ASCII punctuation characters.
PUNCTUATION = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""

# ASCII punctuation characters excluding ', ", `, and \.
SYMBOLS = exclude(PUNCTUATION, """'"`\\""")

# ASCII white space characters (excluding newlines).
WHITESPACE = " \t"

# All ASCII printable characters (letters, digits, punctuation, whitespace).
PRINTABLE = ALPHANUMERIC + PUNCTUATION + WHITESPACE

# ASCII letters and digits with easily confused characters removed).
DISTINGUISHABLE = exclude(ALPHANUMERIC, 'Il1O0')

# ASCII characters that are typed using the shift key.
SHIFTED = UPPERCASE + '~!@#$%^&*()_+{}|:"<>?'
