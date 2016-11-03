# Secrets
#
# Secret is a base class that can be used to easily generate various types of 
# secretes. Basically, it gathers together a collection of strings (the arguments 
# of the constructor and the generate function) that are joined together and 
# hashed. The 512 bit hash is then used to generate passwords, passphrases, and 
# other secrets.
#

# Ignore {{{1
"""
The following code should be ignored. It is defined here for the use of the 
doctests::

>>> from avendesora.secrets import *
>>> class Account(object):
...     def get_field(self, name, default=None):
...          if name == 'master':
...              return 'fux'
...          else:
...              return None
...     def get_name(self):
...          return 'pux'
...     def get_seed(self):
...          return 'pux'
...     def request_seed(self):
...          return False
>>> account = Account()

"""


# License {{{1
# Copyright (C) 2016 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/.


# Imports {{{1
from .charsets import (
    ALPHANUMERIC, DIGITS, DISTINGUISHABLE, LOWERCASE, SYMBOLS, UPPERCASE,
)
from .config import get_setting, override_setting
from .dictionary import DICTIONARY
from .obscure import Obscure
from .utilities import error_source
from inform import Error, terminate, log, warn, output
from binascii import a2b_base64, b2a_base64, Error as BinasciiError
from textwrap import dedent
import hashlib
import getpass
import re
import gnupg
import sys

# Exceptions {{{1
class SecretExhausted(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "secret exhausted"

# Secret {{{1
class Secret(object):
    """Base class for generated secrets"""

    def __init__(self):
        """Constructor

        This base class should not be instantiated. A constructor is only provided 
        to so the doctests work on the helper methods.
        """
        self.master = self.version = None

    def get_key(self, default=None):
        return default

    def generate(self, field_name, field_key, account):
        try:
            if self.secret:
                return
        except AttributeError:
            pass
        account_name = account.get_name()
        account_seed = account.get_seed()
        if self.master is None:
            master = account.get_field('master', default=None)
            master_source = account.get_field('_master_source', default=None)
        else:
            master = self.master
            master_source = 'secret'
        if not master:
            master = get_setting('user_key')
            master_source = 'user_key'
        if not master:
            try:
                try:
                    master = getpass.getpass(
                        'master password for %s: ' % account_name
                    )
                    master_source = 'user'
                except EOFError:
                    output()
                if not master:
                    warn("master password is empty.")
            except (EOFError, KeyboardInterrupt):
                terminate()
        log('Generating secret, source of master seed:', master_source)
        field_key = self.get_key(field_key)
        if self.version:
            version = self.version
        else:
            version = account.get_field('version', default='')

        if account.request_seed():
            try:
                try:
                    interactive_seed = getpass.getpass(
                        'seed for %s: ' % account_name
                    )
                except EOFError:
                    output()
                if not interactive_seed:
                    warn("seed is empty.")
            except (EOFError, KeyboardInterrupt):
                terminate()
        else:
            interactive_seed = ''

        seeds = [
            master,
            account_seed,
            field_name,
            field_key,
            version,
            interactive_seed
        ]
        key = ' '.join([str(seed) for seed in seeds])

        # Convert the key into 512 bit number
        digest = hashlib.sha512((key).encode('utf-8')).digest()
        try:
            # convert from string to list of integers if this is python2
            digest = [ord(c) for c in digest]
        except TypeError:
            pass
        bits_per_byte = 8
        radix = 1 << bits_per_byte
        bits = 0
        for byte in digest:
            bits = radix * bits + byte
        self.pool = bits

    def _partition(self, radix, num_partitions):
        """
        An iterator that returns a sequence of numbers. The length of the 
        sequence is *num_partitions* and each number falls in the range 
        [0:radix). The sequence of numbers seems random, but it is determined by 
        the components that are passed into the constructor.

        >>> secret = Secret()
        >>> secret.generate('dux', None, account)
        >>> ' '.join([str(i) for i in secret._partition(100, 10)])
        '89 80 17 20 34 40 79 1 93 42'

        """
        max_index = radix-1
        bits_per_chunk = (max_index).bit_length()

        for i in range(num_partitions):
            if self.pool < max_index:
                raise SecretExhausted()
            yield self.pool % radix
            self.pool = self.pool >> bits_per_chunk

    def _symbols(self, alphabet, num_symbols):
        """
        An iterator that returns a sequence of symbols. The length of the 
        sequence is *num_symbols* and each symbol is chosen uniformly from the 
        alphabet.

        >>> secret = Secret()
        >>> secret.generate('dux', None, account)
        >>> ' '.join(secret._symbols([str(i) for i in range(100)], 10))
        '89 80 17 20 34 40 79 1 93 42'

        This function can be used to generate a password as follows:
        >>> import string
        >>> alphabet =  alphabet = string.ascii_letters + string.digits
        >>> ''.join(secret._symbols(alphabet, 16))
        'O7Dm0vMjJSMX2w30'

        This function can be used to generate a passphrase as follows:
        >>> dictionary = ['eeny', 'meeny', 'miny', 'moe']
        >>> ' '.join(secret._symbols(dictionary, 4))
        'eeny eeny moe miny'

        """
        radix = len(alphabet)
        max_index = radix-1
        bits_per_chunk = (max_index).bit_length()

        for i in range(num_symbols):
            if self.pool < max_index:
                raise SecretExhausted()
            yield alphabet[self.pool % radix]
            self.pool = self.pool >> bits_per_chunk

    def _get_index(self, radix):
        """
        Returns an index that falls in the range [0:radix).
        Can be called repeatedly with different values for the radix until the 
        secret is exhausted.

        >>> secret = Secret()
        >>> secret.generate('dux', None, account)
        >>> ' '.join([str(secret._get_index(100)) for i in range(10)])
        '89 80 17 20 34 40 79 1 93 42'

        """
        max_index = radix-1
        if self.pool < max_index:
            raise SecretExhausted()

        index = self.pool % radix

        bits_per_chunk = (max_index).bit_length()
        self.pool = self.pool >> bits_per_chunk
        return index

    def _get_symbol(self, alphabet):
        """
        Returns a symbol pulled from the alphabet.
        Can be called repeatedly with different values for the radix until the 
        secret is exhausted.

        >>> secret = Secret()
        >>> secret.generate('dux', None, account)
        >>> ' '.join([str(secret._get_symbol(range(100))) for i in range(10)])
        '89 80 17 20 34 40 79 1 93 42'

        This function can be used to generate a birth date using:
        >>> def birthdate(secret, year, min_age=18, max_age=80):
        ...     return "%02d/%02d/%4d" % (
        ...         secret._get_symbol(range(12)) + 1,
        ...         secret._get_symbol(range(28)) + 1,
        ...         secret._get_symbol(range(year-max_age, year-min_age))
        ...     )
        >>> birthdate(secret, 2014)
        '11/19/1980'

        """
        radix = len(alphabet)
        max_index = radix-1
        if self.pool < max_index:
            raise SecretExhausted()

        index = self.pool % radix

        bits_per_chunk = (max_index).bit_length()
        self.pool = self.pool >> bits_per_chunk

        return alphabet[index]

    # __repr__() {{{2
    def __repr__(self):
        return "Hidden('%s')" % Obscure.hide(str(self))

# Password {{{1
class Password(Secret):
    """
    A relatively high level subclass of Secret that is used to generate 
    passwords and passphrases. For passwords, pass in a string containing all 
    the characters available to the passwords as the alphabet and make sep an 
    empty string.  For passphrases, pass in a list of words as the alphabet and 
    make sep a space.

    >>> import string
    >>> alphabet = string.ascii_letters + string.digits
    >>> secret = Password()
    >>> secret.generate('dux', None, account)
    >>> str(secret)
    'tvA8mewbbig3'

    """
    def __init__(self,
        length=12,
        alphabet=DISTINGUISHABLE,
        master=None,
        version=None,
        sep='',
        prefix='',
        suffix='',
    ):
        try:
            self.length = int(length)
        except ValueError:
            raise Error(
                'expecting an integer for length.', culprit=error_source()
            )
        self.alphabet = alphabet
        self.master = master
        self.version = version
        self.sep = sep
        self.prefix = prefix
        self.suffix = suffix

    def __str__(self):
        try:
            secret = self.secret
        except AttributeError:
            # it is important that this be called only once, because the secret
            # changes each time it is called
            secret = self.secret = (
                self.prefix
              + self.sep.join(self._symbols(self.alphabet, self.length))
              + self.suffix
            )
        return secret


# Passphrase {{{1
class Passphrase(Password):
    """
    Identical to Password() except with different default values that will by 
    generate pass phrases rather than passwords.

    >>> import string
    >>> secret = Passphrase()
    >>> secret.generate('dux', None, account)
    >>> str(secret)
    'graveyard cockle intone provider'

    """
    def __init__(self,
        length=4,
        alphabet=None,
        master=None,
        version=None,
        sep=' ',
        prefix='',
        suffix='',
    ):
        try:
            self.length = int(length)
        except ValueError:
            raise Error(
                'expecting an integer for length.', culprit=error_source()
            )
        self.alphabet = alphabet if alphabet else DICTIONARY.words
        self.master = master
        self.version = version
        self.sep = sep
        self.prefix = prefix
        self.suffix = suffix


# PIN {{{1
class PIN(Password):
    """
    Identical to Password() except with different default values that will by 
    default generate pass PINs rather than passwords.

    >>> import string
    >>> alphabet = string.ascii_letters + string.digits
    >>> secret = PIN()
    >>> secret.generate('dux', None, account)
    >>> str(secret)
    '9301'

    """
    def __init__(self,
        length=4,
        alphabet=DIGITS,
        master=None,
        version=None,
    ):
        try:
            self.length = int(length)
        except ValueError:
            raise Error(
                'expecting an integer for length.', culprit=error_source()
            )
        self.alphabet = alphabet
        self.master = master
        self.version = version
        self.sep = ''
        self.prefix = ''
        self.suffix = ''


# Question {{{1
class Question(Passphrase):
    """
    Identical to Passphrase() except a question must be specified when
    created and is taken to be the security question. The question is used
    rather than the field name when generating the secret.

    >>> import string
    >>> secret = Question('What city were you born in?')
    >>> secret.generate('dux', None, account)
    >>> str(secret)
    'dustcart olive label'

    """
    # Generally the user will want to give several security questions, which
    # they would do as an array. It might be tempting to use a dictionary, but
    # that would be undesirable because ...
    # 1. they would have to give the key twice (it is needed as a seed)
    #    actually this is not necessary, could count on order to distinguish
    #    questions, in this way the questions themselves become purely
    #    descriptive, and the answers would change if you changed their order.
    # 2. they would lose the index and any sense of order, so when they wanted
    #    secret, they would have to identify it by typing in the entire question
    #    exactly.
    # constructor {{{2
    def __init__(self,
        question,
        length=3,
        alphabet=None,
        master=None,
        version=None,
        sep=' ',
        prefix='',
        suffix='',
        answer=None,
    ):
        self.question = question
        try:
            self.length = int(length)
        except ValueError:
            raise Error(
                'expecting an integer for length.', culprit=error_source()
            )
        self.alphabet = alphabet if alphabet else DICTIONARY.words
        self.master = master
        self.version = version
        self.sep = sep
        self.prefix = prefix
        self.suffix = suffix
        if answer:
            self.secret = str(answer)
            # answer allows the user to override the generator and simply
            # specify the answer. This is also used when producing the archive.

    # get_key() {{{2
    def get_key(self, default=None):
        return self.question

    # __repr__() {{{2
    def __repr__(self):
        return "Question(%r, answer=Hidden(%r))" % (
            self.question, Obscure.hide(str(self))
        )

# MixedPassword {{{1
class MixedPassword(Secret):
    """
    A relatively high level method that is used to generate passwords from 
    a heterogeneous collection of alphabets. This is used to satisfy the 
    character type count requirements of many websites.  *requirements* is 
    a list of pairs. Each pair consists of an alphabet and the number of 
    characters required from that alphabet. All other characters are chosen 
    from the default alphabet (*def_alphabet*) until the password has the 
    required number of characters (*num_symbols*).

    >>> import string
    >>> lowercase = string.ascii_lowercase
    >>> uppercase = string.ascii_uppercase
    >>> digits = string.digits
    >>> punctuation = string.punctuation
    >>> base = lowercase + uppercase + digits
    >>> secret = MixedPassword(
    ...     12, base, [(lowercase, 2), (uppercase, 2), (digits, 2)]
    ... )
    >>> secret.generate('dux', None, account)
    >>> str(secret)
    'ZyW62fvxX0Fg'

    """
    def __init__(
        self,
        length,
        def_alphabet,
        requirements,
        master=None,
        version=None,
    ):
        try:
            self.length = int(length)
        except ValueError:
            raise Error(
                'expecting an integer for length.', culprit=error_source()
            )
        self.def_alphabet = def_alphabet
        self.requirements = requirements
        self.master = master
        self.version = version

    def __str__(self):
        try:
            secret = self.secret
        except AttributeError:
            # It is important that this be called only once, because the secret
            # changes each time it is called.

            # Choose the symbols we will used to create the password by drawing from 
            # the various alphabets in order.
            num_required = 0
            symbols = []
            for alphabet, count in self.requirements:
                for i in range(count):
                    symbols.append(self._get_symbol(alphabet))
                    num_required += 1
            for i in range(self.length - num_required):
                symbols.append(self._get_symbol(self.def_alphabet))

            # Now, randomize the symbols to produce the password.
            password = []
            length = self.length
            while (length > 0):
                i = self._get_index(length)
                password.append(symbols.pop(i))
                length -= 1
            secret = ''.join(password)
        self.secret = secret
        return secret

# PasswordRecipe{{{1
class PasswordRecipe(MixedPassword):
    """
    A version of MixedPassword where the requirements are specified with a short
    string rather than using the more flexible but more cumbersome method of
    MixedPassword. The string consists of a series of terms separated by white
    space. The first term is a number that specifies the total number of
    characters in the password. The remaining terms specify the number of
    characters that should be pulled from a particular class of characters. The
    classes are u (upper case letters), l (lower case letters), d (digits), s
    (punctuation), and c (an explicitly specified set of characters). For
    example, '12 2u 2d 2s' indicates that a 12 character password should be
    generated that includes 2 upper case letters, 2 digits, and 2 symbols. The
    remaining characters will be chosen from the base character set, which by
    default is the set of alphanumeric characters.

    The c class is special in that it allow you to explicitly specify the
    characters to use. For example, '12 2c!@#$%^&=' directs that a 12 character
    password be generated, 2 of which are taken from the set !@#$%^&=.

    >>> secret = PasswordRecipe('12 2u 2d 2s')
    >>> secret.generate('pux', None, account)
    >>> str(secret)
    '*m7Aqj=XBAs7'

    >>> secret = PasswordRecipe('12 2u 2d 2c!@#$%^&*')
    >>> secret.generate('bux', None, account)
    >>> str(secret)
    'YO8K^68J9oC!'

    """

    ALPHABETS = {
        'l': LOWERCASE,
        'u': UPPERCASE,
        'd': DIGITS,
        's': SYMBOLS,
        'c': None,
    }
    PATTERN = re.compile(r'(\d*)([%s])(.*)' % ''.join(ALPHABETS.keys()))

    def __init__(
        self,
        recipe,
        def_alphabet=ALPHANUMERIC,
        master=None,
        version=None,
    ):
        requirements = []
        try:
            parts = recipe.split()
        except (ValueError, AttributeError) as err:
            raise Error(
                'recipe must be a string, found %s.' % recipe,
                culprit=error_source()
            )
        try:
            each = parts[0]
            length = int(each)
            for each in parts[1:]:
                num, kind, alphabet = self.PATTERN.match(each).groups()
                if self.ALPHABETS[kind]:
                    alphabet = self.ALPHABETS[kind]
                requirements += [(alphabet, int('0' + num))]
        except (ValueError, AttributeError) as err:
            raise Error(
                "%s: invalid term in recipe '%s'." % (each, recipe),
                culprit=error_source()
            )

        self.length = length
        self.def_alphabet = def_alphabet
        self.requirements = requirements
        self.master = master
        self.version = version


# BirthDate {{{1
class BirthDate(Secret):
    """
    This function can be used to generate a birth date using::

    >>> secret = BirthDate(2015, 18, 65)
    >>> secret.generate('dux', None, account)
    >>> str(secret)
    '1970-03-22'

    For year, enter the year the entry that contains BirthDate was created.  
    Doing so anchors the age range. In this example, the creation date is 2015,
    the minimum age is 18 and the maximum age is 65, meaning that a birthdate
    will be chosen such that in 2015 the birth date could correspond to someone
    that is between 18 and 65 years old.

    You can use the fmt argument to change the way in which the date is 
    formatted::

    >>> secret = BirthDate(2015, 18, 65, fmt="M/D/YY")
    >>> secret.generate('dux', None, account)
    >>> str(secret)
    '3/22/70'

    """
    def __init__(
        self,
        year,
        min_age=18,
        max_age=65,
        fmt='YYYY-MM-DD',
        master=None,
        version=None,
    ):
        self.fmt = fmt
        self.last_year = year-min_age
        self.first_year = year-max_age
        self.master = master
        self.version = version

    def __str__(self):
        try:
            secret = self.secret
        except AttributeError:
            # It is important that this be called only once, because the secret
            # changes each time it is called.
            import arrow
            year = self._get_symbol(range(self.first_year, self.last_year))
            jan1 = arrow.get(year, 1, 1)
            dec31 = arrow.get(year, 12, 31)
            days_in_year = (dec31 - jan1).days
            day = self._get_symbol(range(days_in_year))
            birthdate = jan1.replace(days=day)
            secret = birthdate.format(self.fmt)
        self.secret = secret
        return secret

if __name__ == "__main__":
    import doctest
    fail, total = doctest.testmod()
    print("{} failures out of {} tests".format(fail, total))
