.. _helpers:

Account Helpers
===============

Account helpers are are classes and character sets that are used in your account 
attributes. They provide advanced capabilities such as holding secrets, 
generating secrets, and recognizing accounts.


Generated Secret Classes
------------------------

Sublasses of :class:`avendesora.GeneratedSecret`.

These classes are used when creating account secrets (see :ref:`accounts`).

Every class starts with a pool of 512 bits of entropy. Each symbol generated 
consumes some of that entropy, the amount of which is determine by the number of 
symbols that are available in the alphabet. For example, passphrases pull words 
from a dictionary containing 10,000 words. As such, each word in the passphrase 
consumes 14 bits of entropy (ceil(log2(10000))). If too many words are 
requested, :exc:`avendesora.SecretExhausted` is raised.

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

These are useful when constructing generated secrets. They are used to build the 
alphabet used by the generator. For example, you can specify that passwords 
should be constructed from 12 lower case letters and digits with:

.. code-block:: python

    Password(length=12, alphabet=LOWERCASE+DIGITS)

Or here is an example that starts with the alphanumeric and punctuation 
characters, and removes those that require the shift key to type:

.. code-block:: python

    Password(length=12, alphabet=exclude(ALPHANUMERIC+PUNCTUATION, SHIFTED))


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

These classes are used when creating account secrets (see :ref:`accounts`).

.. autoclass:: avendesora.Hide

.. autoclass:: avendesora.Hidden

.. autoclass:: avendesora.GPG

.. autoclass:: avendesora.Scrypt


Recognizer Classes
------------------

These classes are used in :ref:`account discovery <discovery>`.

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

These classes are used as account values, (see :ref:`scripts`).

.. autoclass:: avendesora.Script
