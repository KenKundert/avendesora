.. index::
    single: secrets

Secrets
=======

Secrets can either by obscured or generated.

.. index::
    single: obscured secrets

Obscured Secrets
----------------

Obscured secrets are secrets that are those that are given to Avendesora
to securely hold. The may be things like account numbers or existing
passwords.  There are several ways for Avendesora to hold a secret,
presented in order of increasing security.

.. index::
    single: Hide

Hide
""""

This marks a value as being confidential, meaning that it will be
protected when shown to the user, but value is not encoded or encrypted
in any way.  Rather, it accounts on the protections afforded the
accounts file to protect its secret.

 |  Hide(plaintext, secure=True)

 |  plaintext (str):
 |      The secret in plain text.
 |  secure (bool):
 |      Indicates that this secret should only be contained in an
 |      encrypted accounts file. Default is True.

Example::

    account = Hide('9646-3440')


.. index::
    single: Hidden

Hidden
""""""

This obscures but does not encrypt the text. It can protect the secret from
observers that get a quick glance of the encoded text, but if they are able to
capture it they can easily decode it.

 |  Hidden(encoded_text, secure=True, encoding=None)

 |  encoded_text (str):
 |      The secret encoded in base64.
 |  secure (bool):
 |      Indicates that this secret should only be contained in an
 |      encrypted accounts file. Default is True.
 |  encoding (str):
 |      The encoding to use for the deciphered text.

Example::

    account = Hidden('NTIwNi03ODQ0')

To generate the encoded text, use::

    > avendesora conceal


.. index::
    single: GPG

GPG
"""

The secret is fully encrypted with GPG. Both symmetric encryption and
key-based encryption are supported.  This can be used to protect a
secret held in an unencrypted account file, in which case encrypting
with your key is generally preferred. It can also be used to further
protect a extremely valuable secret, in which case symmetric encryption
is generally used.

 |  GPG(ciphertext, encoding=None)

 |  ciphertext (str):
 |      The secret encrypted and armored by GPG.
 |  encoding (str):
 |      The encoding to use for the deciphered text.

Example::

    secret = GPG('''
        -----BEGIN PGP MESSAGE-----
        Version: GnuPG v2.0.22 (GNU/Linux)

        jA0ECQMCwG/vVambFjfX0kkBMfXYyKvAuCbT3IrEuEKD//yuEMCikciteWjrFlYD
        ntosdZ4WcPrFrV2VzcIIcEtU7+t1Ay+bWotPX9pgBQcdnSBQwr34PuZi
        =4on3
        -----END PGP MESSAGE-----
    ''')

To generate the cipher text, use::

    > avendesora conceal -e gpg

The benefit of using symmetric GPG encryption on a secret that is
contained in an encrypted account file is that the passphrase will
generally not be found in the GPG agent, in which case someone could not
walk up to your computer while your screen is unlocked and successfully
request the secret.  However, the GPG agent does retain the password for
a while after you decrypt the secret. If you are concerned about that,
you should follow your use of *Avendesora* with the following command,
which clears the GPG agent:

    > killall gpg-agent


.. index::
    single: Scrypt

Scrypt
""""""

The secret is fully encrypted with Scrypt. You personal Avendesora
encryption key is used (contained in ~/.config/avendesora/.key.gpg). As
such, these secrets cannot be shared. This encryption method is only
available if you have installed scrypt on your system (pip3 install
--user scrypt). Since the Scrypt class only exists if you have installed
scrypt, it is not imported into your accounts file. You would need to
import it yourself before using it.

 |  Script(ciphertext, encoding=None)

 |  ciphertext (str):
 |      The secret encrypted by scrypt.
 |  encoding (str):
 |      The encoding to use for the deciphered text.

Example::

    from avendesora import Scrypt
    ...
    secret = Scrypt(
        'c2NyeXB0ABAAAAAIAAAAASfBZvtYnHvgdts2jrz5RfbYlFYj/EQgiM1IYTnX'
        'KHhMkleZceDg0yUaOWa9PzmZueppNIzVdawAOd9eSVgGeZAIh4ulPHPBGAzX'
        'GyLKc/vo8Fe24JnLr/RQBlTjM9+r6vbhi6HFUHD11M6Ume8/0UGDkZ0='
    )

To generate the cipher text, use::

    > avendesora conceal -e scrypt


.. index::
    single: generated secrets

Generated Secrets
-----------------

Generated secrets are secrets for which the actual value is arbitrary,
but it must be quite unpredictable. Generated secrets are generally used
for passwords and pass phrases, but it can also be used for things like
personal information requested by institutions that they have no need to
know. For example, a website might request your birth date to assure
that you are an adult, but then also use it as a piece of identifying
information if you ever call and request support.  In this case they do
not need your actual birth date, they just need you to give the same
date every time you call in.


.. index::
    single: Password

Password
""""""""

Generates an arbitrary password by selecting symbols from the given
alphabet at random. The entropy of the generated password is
length*log2(len(alphabet)).

 |  Password(
 |      length=12, alphabet=DISTINGUISHABLE, master=None, version=None,
 |      sep='', prefix='', suffix=''
 |  )

 |  length (int):
 |      The number of items to draw from the alphabet when creating the
 |      password.  When using the default alphabet, this will be the
 |      number of characters in the password.
 |  alphabet (str):
 |      The reservoir of legal symbols to use when creating the
 |      password. By default the set of easily distinguished
 |      alphanumeric characters are used. Typically you would use the
 |      pre-imported character sets to construct the alphabet. For
 |      example, you might pass:
 |          ALPHANUMERIC + '+=_&%#@'
 |  master (str):
 |      Overrides the master seed that is used when generating the
 |      password.  Generally, there is one master seed shared by all
 |      accounts contained in an account file.  This argument overrides
 |      that behavior and instead explicitly specifies the master seed
 |      for this secret.
 |  version (str):
 |      An optional seed. Changing this value will change the generated
 |      password.
 |  shift_sort(bool):
 |      If true, the characters in the password will be sorted so that
 |      the characters that require the shift key when typing are placed
 |      last, making it easier to type. Use this option if you expect to
 |      be typing the password by hand.
 |  sep (str):
 |      A string that is placed between each symbol in the generated
 |      password.
 |  prefix (str):
 |      A string added to the front of the generated password.
 |  suffix (str):
 |      A string added to the end of the generated password.

Example::

    passcode = Password(10)


.. index::
    single: Passphrase

Passphrase
""""""""""

Similar to Password in that it generates an arbitrary pass phrase by
selecting symbols from the given alphabet at random, but in this case
the default alphabet is a dictionary containing about 10,000 words.

 |  Passphrase(
 |      length=4, alphabet=None, master=None, version=None, sep=' ', prefix='',
 |      suffix=''
 |  )

 |  length (int):
 |      The number of items to draw from the alphabet when creating the
 |      password.  When using the default alphabet, this will be the
 |      number of words in the passphrase.
 |  alphabet (str):
 |      The reservoir of legal symbols to use when creating the
 |      password. By default, this is a predefined list of 10,000 words.
 |  master (str):
 |      Overrides the master seed that is used when generating the
 |      password.  Generally, there is one master seed shared by all
 |      accounts contained in an account file.  This argument overrides
 |      that behavior and instead explicitly specifies the master seed
 |      for this secret.
 |  version (str):
 |      An optional seed. Changing this value will change the generated
 |      pass phrase.
 |  sep (str):
 |      A string that is placed between each symbol in the generated
 |      password.
 |  prefix (str):
 |      A string added to the front of the generated password.
 |  suffix (str):
 |      A string added to the end of the generated password.

Example::

    passcode = Passphrase()
    verbal = Passphrase(2)


.. index::
    single: PIN

PIN
"""

Similar to Password in that it generates an arbitrary PIN by selecting
symbols from the given alphabet at random, but in this case the default
alphabet is the set of digits (0-9).

 |  PIN(length=4, alphabet=DIGITS, master=None, version=None)

 |  length (int):
 |      The number of items to draw from the alphabet when creating the
 |      password.  When using the default alphabet, this will be the
 |      number of digits in the PIN.
 |  alphabet (str):
 |      The reservoir of legal symbols to use when creating the
 |      password. By default the digits (0-9) are used.
 |  master (str):
 |      Overrides the master seed that is used when generating the
 |      password.  Generally, there is one master seed shared by all
 |      accounts contained in an account file.  This argument overrides
 |      that behavior and instead explicitly specifies the master seed
 |      for this secret.
 |  version (str):
 |      An optional seed. Changing this value will change the generated
 |      PIN.

Example::

    pin = PIN(6)


.. index::
    single: Question

Question
""""""""

Generates an arbitrary answer to a given question. Used for website
security questions. When asked one of these security questions it can be
better to use an arbitrary answer. Doing so protects you against people
who know your past well and might be able to answer the questions.

Similar to Passphrase() except a question must be specified when created
and it is taken to be the security question. The question is used rather
than the field name when generating the secret.

 |  Question(
 |      question, length=3, alphabet=None, master=None, version=None,
 |      sep=' ', prefix='', suffix='', answer=None
 |  )

 |  question (str):
 |      The question to be answered. Be careful. Changing the question
 |      in any way will change the resulting answer.
 |  length (int):
 |      The number of items to draw from the alphabet when creating the
 |      password. When using the default alphabet, this will be the
 |      number of words in the answer.
 |  alphabet (list of strs):
 |      The reservoir of legal symbols to use when creating the
 |      password. By default, this is a predefined list of 10,000 words.
 |  master (str):
 |      Overrides the master seed that is used when generating the
 |      password.  Generally, there is one master seed shared by all
 |      accounts contained in an account file.  This argument overrides
 |      that behavior and instead explicitly specifies the master seed
 |      for this secret.
 |  version (str):
 |      An optional seed. Changing this value will change the generated
 |      answer.
 |  sep (str):
 |      A string that is placed between each symbol in the generated
 |      password.
 |  prefix (str):
 |      A string added to the front of the generated password.
 |  suffix (str):
 |      A string added to the end of the generated password.
 |  answer:
 |      The answer. If provided, this would override the generated
 |      answer.  May be a string, or it may be an Obscured object.

Example::

    questions = [
        Question('Favorite foreign city'),
        Question('Favorite breed of dog'),
    ]


.. index::
    single: PasswordRecipe

PasswordRecipe
""""""""""""""

Generates passwords that can conform to the restrictive requirements
imposed by websites. Allows you to specify the length of your password,
and how many characters should be of each type of character using a
recipe. The recipe takes the form of a string that gives the total
number of characters that should be generated, and then the number of
characters that should be taken from particular character sets. The
available character sets are:

 | l - lower case letters (a-z)
 | u - upper case letters (A-Z)
 | d - digits (0-9)
 | s - punctuation symbols
 | c - explicitly given set of characters

For example, '12 2u 2d 2s' is a recipe that would generate a
12-character password where two characters would be chosen from the
upper case letters, two would be digits, two would be punctuation
symbols, and the rest would be alphanumeric characters. It might
generate something like: @m7Aqj=XBAs7

Using '12 2u 2d 2c!@#$%^&*' is similar, except the punctuation symbols
are constrained to be taken from the given set that includes !@#$%^&*.
It might generate something like: YO8K^68J9oC!

 |  PasswordRecipe(
 |      recipe, def_alphabet=ALPHANUMERIC, master=None, version=None,
 |  )

 |  recipe (str):
 |      A string that describes how the password should be constructed.
 |  def_alphabet (list of strs):
 |      The alphabet to use when filling up the password after all the
 |      constraints are satisfied.
 |  master (str):
 |      Overrides the master seed that is used when generating the
 |      password.  Generally, there is one master seed shared by all
 |      accounts contained in an account file.  This argument overrides
 |      that behavior and instead explicitly specifies the master seed
 |      for this secret.
 |  version (str):
 |      An optional seed. Changing this value will change the generated
 |      answer.
 |  shift_sort(bool):
 |      If true, the characters in the password will be sorted so that
 |      the characters that require the shift key when typing are placed
 |      last, making it easier to type. Use this option if you expect to
 |      be typing the password by hand.

Example:

    passcode = PasswordRecipe('12 2u 2d 2c!@#$%^&*')


.. index::
    single: BirthDate

BirthDate
"""""""""

Generates an arbitrary birth date for someone in a specified age range.


 |  BirthDate(
 |      year, min_age=18, max_age=65, fmt='YYYY-MM-DD',
 |      master=None, version=None,
 |  )

 |  year (int):
 |      The year the age range was established.
 |  min_age (int):
 |      The lower bound of the age range.
 |  max_age (int):
 |      The upper bound of the age range.
 |  fmt (str):
 |      Specifies the way the date is formatted. Consider an example
 |      date of 6 July 1969. YY and YYYY are replaced by the year (69 or
 |      1969). M, MM, MMM, and MMMM are replaced by the month (7, 07,
 |      Jul, or July). D and DD are replaced by the day (6 or 06).
 |  master (str):
 |      Overrides the master seed that is used when generating the
 |      password.  Generally, there is one master seed shared by all
 |      accounts contained in an account file.  This argument overrides
 |      that behavior and instead explicitly specifies the master seed
 |      for this secret.
 |  version (str):
 |      An optional seed. Changing this value will change the generated
 |      answer.

Example::

    birthdate = BirthDate(2015, 21, 55)


.. index::
    single: OTB

OTP
"""

Generates a secret that changes once per minute that generally is used
as a second factor when authenticating.  It can act as a replacement
for, and is fully compatible with, Google Authenticator.  You would
provide the text version of the shared secret (the backup code) that is
presented to you when first configuring your second factor authentication.

 |  OTP(shared_secret, interval=30, digits=6)

 |  shared_secret (base32 string):
 |      The shared secret, it will be provided by the account provider.
 |  interval (int):
 |      Update interval in seconds.
 |  max_age (int):
 |      The number of digits to output.

Example::

    otp = OTP('JBSWY3DPEHPK3PXP')


.. index::
    single: versioning a secret
    single: updating a secret

Changing a Generated Secret
"""""""""""""""""""""""""""

It is sometimes necessary to change a generated secret. Perhaps because
it was inadvertently exposed, or perhaps because the account provider
requires you change your secret periodically.  To do so, you would
simply add the *version* argument to the secret and then update its
value.  *version* may be a number or a string. You should choose a way
of versioning that is simple, easy to guess and would not
repeat. For example, if you expect that updating the version would be
extremely rare, you can simply number them sequentially. Or, if you you
need to update them every month or every quarter, you can name them
after the month or quarter (ex: jan19 or 19q1).

Examples::

    passcode = PasswordRecipe('16 1d', version=2)
    passcode = PasswordRecipe('16 1d', version='19q2')
