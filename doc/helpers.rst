.. _helpers:

Account Helpers
===============

Generated Secret Classes
------------------------

Sublasses of :class:`avendesora.GeneratedSecret`.

.. autoclass:: avendesora.Password

.. autoclass:: avendesora.Passphrase

.. autoclass:: avendesora.PIN

.. autoclass:: avendesora.Question

.. autoclass:: avendesora.MixedPassword

.. autoclass:: avendesora.PasswordRecipe

.. autoclass:: avendesora.BirthDate

.. autoclass:: avendesora.OTP

.. autoexception:: avendesora.SecretExhausted
    :members: report, terminate


Character Sets
--------------

These are useful when constructing generated secrets.

.. autofunction:: avendesora.exclude

.. attribute:: avendesora.LOWERCASE

    Lower case ASCII letters:
    :attr:`avendesora.LOWERCASE` = "abcdefghijklmnopqrstuvwxyz"


.. attribute:: avendesora.UPPERCASE

    Upper case ASCII letters:
    :attr:`avendesora.UPPERCASE` = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


.. attribute:: avendesora.LETTERS

    Upper and lower case ASCII letters:
    :attr:`avendesora.LETTERS` = :attr:`avendesora.LOWERCASE` + :attr:`avendesora.UPPERCASE`


.. attribute:: avendesora.DIGITS

    ASCII digits:
    :attr:`avendesora.DIGITS` = "0123456789"


.. attribute:: avendesora.ALPHANUMERIC

    ASCII letters and digits:
    :attr:`avendesora.ALPHANUMERIC` = :attr:`avendesora.LETTERS` + :attr:`avendesora.DIGITS`


.. attribute:: avendesora.HEXDIGITS

    Hexidecimal digits:
    :attr:`avendesora.HEXDIGITS` = "0123456789abcdef"


.. attribute:: avendesora.PUNCTUATION

    ASCII punctuation characters:
    :attr:`avendesora.PUNCTUATION` = "!"#$%&'()\*+,-./:;<=>?@[\\]^_`{|}~"


.. attribute:: avendesora.SYMBOLS

    ASCII punctuation characters excluding ', ", \`, and \\:
    :attr:`avendesora.SYMBOLS` = exclude(avendesora.PUNCTUATION, "'"\`\\")


.. attribute:: avendesora.WHITESPACE

    ASCII white space characters (excluding newlines):
    :attr:`avendesora.WHITESPACE` = " \\t"


.. attribute:: avendesora.PRINTABLE

    All ASCII printable characters (letters, digits, punctuation, whitespace):
    :attr:`avendesora.PRINTABLE` = :attr:`avendesora.ALPHANUMERIC` + :attr:`avendesora.PUNCTUATION` + :attr:`avendesora.WHITESPACE`


.. attribute:: avendesora.DISTINGUISHABLE

    ASCII letters and digits with easily confused characters removed:
    :attr:`avendesora.DISTINGUISHABLE` = exclude(:attr:`avendesora.ALPHANUMERIC`, 'Il1O0')


.. attribute:: avendesora.SHIFTED

    ASCII characters that are typed using the shift key:
    :attr:`avendesora.SHIFTED` = :attr:`avendesora.UPPERCASE` + '~!@#$%^&*()_+{}|:"<>?'


Obscured Secret Classes
-----------------------

Sublasses of :class:`avendesora.ObscuredSecret`.

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
