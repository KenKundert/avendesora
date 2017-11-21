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

.. autoexception:: avendesora.SecretExhausted
    :members: report, terminate


Character Sets
--------------

These are useful when constructing generated secrets.

.. autofunction:: avendesora.exclude

.. attribute:: avendesora.LOWERCASE = "abcdefghijklmnopqrstuvwxyz"

    Lower case ASCII letters.

.. attribute:: avendesora.UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    Upper case ASCII letters.

.. attribute:: avendesora.LETTERS = avendesora.LOWERCASE  + avendesora.UPPERCASE

    Upper and lower case ASCII letters.

.. attribute:: avendesora.DIGITS = "0123456789"

    ASCII digits.

.. attribute:: avendesora.ALPHANUMERIC = avendesora.LETTERS + avendesora.DIGITS

    ASCII letters and digits.

.. attribute:: avendesora.HEXDIGITS = "0123456789abcdef"

    Hexidecimal digits.

.. attribute:: avendesora.PUNCTUATION = "!"#$%&'()\*+,-./:;<=>?@[\\]^_`{|}~"

    ASCII punctuation characters.

.. attribute:: avendesora.SYMBOLS = exclude(avendesora.PUNCTUATION, "'"\`\\")

    ASCII punctuation characters excluding ', ", \`, and \\.

.. attribute:: avendesora.WHITESPACE = " \\t"

    ASCII white space characters (excluding newlines).

.. attribute:: avendesora.PRINTABLE = avendesora.ALPHANUMERIC + avendesora.PUNCTUATION + avendesora.WHITESPACE

    All ASCII printable characters (letters, digits, punctuation, whitespace).

.. attribute:: avendesora.DISTINGUISHABLE = exclude(avendesora.ALPHANUMERIC, 'Il1O0')

    ASCII letters and digits with easily confused characters removed).

.. attribute:: avendesora.SHIFTED = UPPERCASE + '~!@#$%^&*()_+{}|:"<>?'

    ASCII characters that are typed using the shift key.


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
