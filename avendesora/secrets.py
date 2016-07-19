# Secrets
#
# Secret is a base class that can be used to easily generate various types of 
# secretes. Basically, it gathers together a collection of strings (the arguments 
# of the constructor and the generate function) that are joined together and 
# hashed. The 512 bit hash is then used to generate passwords, passphrases, and 
# other secrets.
#
# The following code should be ignored. It is defined here for the use of the 
# doctests::
#
# >>> from avendesora.secrets import *
# >>> class Account:
# ...     def get_value(self, name, default=None):
# ...          if name == 'master':
# ...              return 'fux'
# ...          else:
# ...              return None
# ...     def get_name(self):
# ...          return 'pux'
# >>> account = Account()

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
from .charsets import DIGITS, DISTINGUISHABLE
from .config import get_setting, override_setting
from .dictionary import DICTIONARY
from inform import Error, error, fatal, log, output, terminate, warn
from binascii import a2b_base64, b2a_base64, Error as BinasciiError
from textwrap import dedent
import hashlib
import getpass
import gnupg
import sys

# Exceptions {{{1
class SecretExhausted(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "secret exhausted"

# Hidden {{{1
class Hidden():
    # This does a simple base64 encoding on the string to hide it from a casual
    # observer. But it is not encrypted. The original value can be trivially
    # recovered from the encoded version.
    def __init__(self, value, secure=True, encoding='utf8'):
        try:
            value = a2b_base64(value)
            self.value = value.decode(encoding)
            self.secure = secure
        except BinasciiError as err:
            import traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            filename, lineno = traceback.extract_stack()[-2][:2]
                # context and content are also available, but in this case
                # Hidden is generally instantiated from top-level so the 
                # context is not interesting and the content (the actual line 
                # of code) shown in this case is gibberish (encrypted).
            fatal(
                'invalid value specified to Hidden().',
                culprit=(filename, lineno)
            )

    def generate(self, name, account):
        # we don't need to do anything, but having this method marks this value
        # as being confidential
        pass

    def is_secure(self):
        return self.secure

    def __str__(self):
        return self.value

    @staticmethod
    def hide(value, encoding='utf8'):
        value = value.encode(encoding)
        return b2a_base64(value).rstrip().decode('ascii')

    @staticmethod
    def reveal(value, encoding='utf8'):
        value = a2b_base64(value.encode('ascii'))
        return value.decode(encoding)
# GPG {{{1
class GPG():
    # This does a full GPG decryption.
    # To generate an entry for the GPG argument, you can use ...
    #     gpg -a -c filename
    # It will create filename.asc. Copy the contents of that file into the
    # argument.
    # This uses symmetric encryption to add an additional layer of protection.
    # Generally one would use their private key to protect the gpg file, and
    # then use a symmetric key, or perhaps a separate private key, to protect an
    # individual piece of data, like a master password.
    def __init__(self, value, secure=True, encoding='utf8'):
        self.value = value
        gpg_path = get_setting('gpg_path')
        gpg_home = get_setting('gpg_home')
        gpg_args = {}
        if gpg_path:
            gpg_args.update({'gpgbinary': str(gpg_path)})
        if gpg_home:
            gpg_args.update({'gnupghome': str(gpg_home)})
        self.gpg = gnupg.GPG(**gpg_args)


    def generate(self, name, account):
        # must do this here in generate rather than in constructor to avoid
        # decrypting this, and perhaps asking for a passcode,  every time
        # Advendesora is run.
        decrypted = self.gpg.decrypt(dedent(self.value))
        if not decrypted.ok:
            import traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            filename, lineno = traceback.extract_stack()[-2][:2]
                # context and content are also available, but in this case
                # GPG is generally instantiated from top-level so the 
                # context is not interesting and the content (the actual line 
                # of code) shown in this case is gibberish (encrypted).
            msg = 'unable to decrypt argument to GPG()'
            try:
                msg = '%s: %s' % (msg, decrypted.stderr)
            except AttributeError:
                msg += '.'
            fatal(msg, culprit=(filename, lineno))
        self.decrypted = decrypted
        pass

    def __str__(self):
        return str(self.decrypted)


# Secret {{{1
class Secret():
    """Base class for generated secrets"""

    def __init__(self):
        """Constructor

        This base class should not be instantiated. A constructor is only provided 
        to so the doctests work on the helper methods.
        """
        self.name = self.master = self.version = None

    def get_name(self):
        return self.name

    def generate(self, name, account):
        if self.master is None:
            master = account.get_value('master', default=None)
        else:
            master = self.master
        if not master:
            try:
                master = getpass.getpass(
                    'master password for %s: ' % account.get_name()
                )
                if not master:
                    warn("master password is empty.")
            except (EOFError, KeyboardInterrupt):
                terminate()
        name = self.name if self.name else name
        if self.version:
            version = self.version
        else:
            try:
                version = account.get_value('version')
            except Error:
                version = ''
        account_name = account.get_name()

        key = ''.join([str(e) for e in [name, account_name, master, version]])

        # Convert the key into 512 bit number
        digest = hashlib.sha512((key).encode('utf-8')).digest()
        bits_per_byte = 8
        radix = 1 << bits_per_byte
        bits = 0
        try:
            # in python3, digest is a byte array
            for byte in digest:
                bits = radix * bits + byte
        except TypeError:
            # in python2, digest is a string
            for char in digest:
                bits = radix * bits + ord(char)
        self.pool = bits

    def _partition(self, radix, num_partitions):
        """
        An iterator that returns a sequence of numbers. The length of the 
        sequence is *num_partitions* and each number falls in the range 
        [0:radix). The sequence of numbers seems random, but it is determined by 
        the components that are passed into the constructor.

        >>> secret = Secret()
        >>> secret.generate('dux', account)
        >>> ' '.join([str(i) for i in secret._partition(100, 10)])
        '39 0 91 10 32 51 0 39 28 72'

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
        >>> secret.generate('dux', account)
        >>> ' '.join(secret._symbols([str(i) for i in range(100)], 10))
        '39 0 91 10 32 51 0 39 28 72'

        This function can be used to generate a password as follows:
        >>> import string
        >>> alphabet =  alphabet = string.ascii_letters + string.digits
        >>> ''.join(secret._symbols(alphabet, 16))
        'RwKKxLKUMoRlf3nm'

        This function can be used to generate a passphrase as follows:
        >>> dictionary = ['eeny', 'meeny', 'miny', 'moe']
        >>> ' '.join(secret._symbols(dictionary, 4))
        'eeny meeny meeny moe'

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
        >>> secret.generate('dux', account)
        >>> ' '.join([str(secret._get_index(100)) for i in range(10)])
        '39 0 91 10 32 51 0 39 28 72'

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
        >>> secret.generate('dux', account)
        >>> ' '.join([str(secret._get_symbol(range(100))) for i in range(10)])
        '39 0 91 10 32 51 0 39 28 72'

        This function can be used to generate a birth date using:
        >>> def birthdate(secret, year, min_age=18, max_age=80):
        ...     return "%02d/%02d/%4d" % (
        ...         secret._get_symbol(range(12)) + 1,
        ...         secret._get_symbol(range(28)) + 1,
        ...         secret._get_symbol(range(year-max_age, year-min_age))
        ...     )
        >>> birthdate(secret, 2014)
        '06/04/1975'

        """
        radix = len(alphabet)
        max_index = radix-1
        if self.pool < max_index:
            raise SecretExhausted()

        index = self.pool % radix

        bits_per_chunk = (max_index).bit_length()
        self.pool = self.pool >> bits_per_chunk

        return alphabet[index]


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
    >>> secret.generate('dux', account)
    >>> str(secret)
    'zSxJKBTryBHD'

    """
    def __init__(self,
        length=12,
        alphabet=DISTINGUISHABLE,
        master=None,
        version=None,
        sep=''
    ):
        self.name = None
        self.length = length
        self.alphabet = alphabet
        self.master = master
        self.version = version
        self.sep = sep

    def __str__(self):
        return self.sep.join(self._symbols(self.alphabet, self.length))


# Passphrase {{{1
class Passphrase(Password):
    """
    Identical to Password() except with different default values that will by 
    generate pass phrases rather than passwords.

    >>> import string
    >>> secret = Passphrase()
    >>> secret.generate('dux', account)
    >>> str(secret)
    'condition proxy broom customize'

    """
    def __init__(self,
        length=4,
        alphabet=None,
        master=None,
        version=None,
        sep=' '
    ):
        self.name = None
        self.length = length
        self.alphabet = alphabet if alphabet else DICTIONARY.words
        self.master = master
        self.version = version
        self.sep = sep


# PIN {{{1
class PIN(Password):
    """
    Identical to Password() except with different default values that will by 
    default generate pass PINs rather than passwords.

    >>> import string
    >>> alphabet = string.ascii_letters + string.digits
    >>> secret = PIN()
    >>> secret.generate('dux', account)
    >>> str(secret)
    '9205'

    """
    def __init__(self,
        length=4,
        alphabet=DIGITS,
        master=None,
        version=None,
    ):
        self.name = None
        self.length = length
        self.alphabet = alphabet
        self.master = master
        self.version = version
        self.sep = ''


# Question {{{1
class Question(Passphrase):
    """
    Identical to Passphrase() except the name must be specified when created 
    and is taken to be the security question.

    >>> import string
    >>> secret = Question('What city were you born in?')
    >>> secret.generate('dux', account)
    >>> str(secret)
    'trapeze ditch arrange'

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
    def __init__(self,
        question,
        length=3,
        alphabet=None,
        master=None,
        version=None,
        sep=' '
    ):
        self.name = question
        self.question = None
        self.length = length
        self.alphabet = alphabet if alphabet else DICTIONARY.words
        self.master = master
        self.version = version
        self.sep = sep


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
    >>> secret.generate('dux', account)
    >>> str(secret)
    'C2Frf0j3Q4AY'

    """
    def __init__(
        self,
        length,
        def_alphabet,
        requirements,
        master=None,
        version=None,
    ):
        self.name = None
        self.length = length
        self.def_alphabet = def_alphabet
        self.requirements = requirements
        self.master = master
        self.version = version

    def __str__(self):
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
        while (self.length > 0):
            i = self._get_index(self.length)
            password.append(symbols.pop(i))
            self.length -= 1
        return ''.join(password)


# BirthDate {{{1
class BirthDate(Secret):
    """
    This function can be used to generate a birth date using::

    >>> secret = BirthDate(2015, 18, 65)
    >>> secret.generate('dux', account)
    >>> str(secret)
    '1963-11-17'

    For year, enter the year the entry that contains BirthDate was created.  
    Doing so anchors the age range. In this example, the creation date is 2015,
    the minimum age is 18 and the maximum age is 65, meaning that a birthdate
    will be chosen such that in 2015 the birth date could correspond to someone
    that is between 18 and 65 years old.

    You can use the fmt argument to change the way in which the date is 
    formatted::

    >>> secret = BirthDate(2015, 18, 65, fmt="M/D/YY")
    >>> secret.generate('dux', account)
    >>> str(secret)
    '11/17/63'

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
        self.name = None
        self.fmt = fmt
        self.last_year = year-min_age
        self.first_year = year-max_age
        self.master = master
        self.version = version

    def __str__(self):
        import arrow
        year = self._get_symbol(range(self.first_year, self.last_year))
        jan1 = arrow.get(year, 1, 1)
        dec31 = arrow.get(year, 12, 31)
        days_in_year = (dec31 - jan1).days
        day = self._get_symbol(range(days_in_year))
        birthdate = jan1.replace(days=day)
        return birthdate.format(self.fmt)

if __name__ == "__main__":
    import doctest
    fail, total = doctest.testmod()
    print("{} failures out of {} tests".format(fail, total))
