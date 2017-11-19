Account Helpers
===============

Generated Secret Classes
------------------------

.. autoclass:: avendesora.Password

.. autoclass:: avendesora.Passphrase

.. autoclass:: avendesora.PIN

.. autoclass:: avendesora.Question

.. autoclass:: avendesora.MixedPassword

.. autoclass:: avendesora.PasswordRecipe

.. autoclass:: avendesora.BirthDate


Character Sets
--------------

These are useful when constructing generated secrets.

.. autofunction:: avendesora.exclude

avendesora.LOWERCASE = "abcdefghijklmnopqrstuvwxyz":
    Lower case ASCII letters.

avendesora.UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    Upper case ASCII letters.

avendesora.LETTERS = LOWERCASE + UPPERCASE:
    Upper and lower case ASCII letters.

avendesora.DIGITS = "0123456789":
    ASCII digits.

avendesora.ALPHANUMERIC = LETTERS + DIGITS
    ASCII letters and digits.

avendesora.HEXDIGITS = "0123456789abcdef":
    Hexidecimal digits.

avendesora.PUNCTUATION = "!"#$%&'()\*+,-./:;<=>?@[\\]^_`{|}~":
    ASCII punctuation characters.

avendesora.SYMBOLS = exclude(PUNCTUATION, "'"\`\\"):
    ASCII punctuation characters excluding ', ", \`, and \\.

avendesora.WHITESPACE = " \\t":
    ASCII white space characters (excluding newlines).

avendesora.PRINTABLE = ALPHANUMERIC + PUNCTUATION + WHITESPACE:
    All ASCII printable characters (letters, digits, punctuation, whitespace).

avendesora.DISTINGUISHABLE = exclude(ALPHANUMERIC, 'Il1O0'):
    ASCII letters and digits with easily confused characters removed).

avendesora.SHIFTED = UPPERCASE + '~!@#$%^&*()_+{}|:"<>?':
    # ASCII characters that are typed using the shift key.




Obscured Secret Classes
-----------------------

.. autoclass:: avendesora.Hide

.. autoclass:: avendesora.Hidden

.. autoclass:: avendesora.GPG

.. autoclass:: avendesora.Scrypt


Recognizer Classes
------------------

.. autoclass:: avendesora.RecognizeAll

.. autoclass:: avendesora.RecognizeAny

.. autoclass:: avendesora.RecognizeTitle

.. autoclass:: avendesora.RecognizeURL

.. autoclass:: avendesora.RecognizeCWD

.. autoclass:: avendesora.RecognizeHost

.. autoclass:: avendesora.RecognizeUser

.. autoclass:: avendesora.RecognizeEnvVar

.. autoclass:: avendesora.RecognizeNetwork

.. autoclass:: avendesora.RecognizeFile


Utility Classes
---------------

.. autoclass:: avendesora.Script
