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

    Use this to strip characters from a character set.
    """
    try:
        # this version is compatible with python3
        return chars.translate(str.maketrans('', '', exclusions))
    except AttributeError:
        # this version is compatible with python2
        return chars.translate(None, exclusions)

# Character sets
# Use these to construct alphabets by summing together the ones you want.
LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LETTERS = LOWERCASE + UPPERCASE
DIGITS = "0123456789"
ALPHANUMERIC = LETTERS + DIGITS
HEXDIGITS = "0123456789abcdef"
PUNCTUATION = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
SYMBOLS = exclude(PUNCTUATION, r"""'"`\\""")
WHITESPACE = " \t"
PRINTABLE = ALPHANUMERIC + PUNCTUATION + WHITESPACE
DISTINGUISHABLE = exclude(ALPHANUMERIC, 'Il1O0')
