#!/usr/bin/env python
"""
Secrets

Secret is a base class that can be used to easily generate various types of 
secretes. Basically, it gathers together a collection of strings (the arguments 
of the constructor and the _initiate function) that are joined together and 
hashed. The 512 bit hash is then used to generate passwords, passphrases, and 
other secrets.

The following code should be ignored. It is defined here for the use of the 
doctests::

>>> from avendesora.secrets import *
>>> class Account:
...     def get_value(self, name):
...          if name == 'master':
...              return 'fux'
...          else:
...              return None
...     def get_name(self):
...          return 'pux'
>>> account = Account()

"""

from .charsets import DIGITS, DISTINGUISHABLE
from .dictionary import DICTIONARY
from inform import Error
import hashlib

# Exceptions {{{1
class SecretExhausted(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "secret exhausted"

# Secret {{{1
class Secret():
    """Base class for secrets"""

    def __init__(self):
        """Constructor

        This base class should not be instantiated. A constructor is only provided 
        to so the doctests work on the helper methods.
        """
        self.name = self.master = self.version = None

    def get_name(self):
        return self.name

    def _initiate(self, name, account):
        master = self.master if self.master else account.get_value('master')
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
        >>> secret._initiate('dux', account)
        >>> ' '.join([str(i) for i in secret._partition(100, 10)])
        '90 89 14 76 51 70 83 23 91 47'

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
        >>> secret._initiate('dux', account)
        >>> ' '.join(secret._symbols([str(i) for i in range(100)], 10))
        '90 89 14 76 51 70 83 23 91 47'

        This function can be used to generate a password as follows:
        >>> import string
        >>> alphabet =  alphabet = string.ascii_letters + string.digits
        >>> ''.join(secret._symbols(alphabet, 16))
        'ZU2pnw6Ag04Adn0Y'

        This function can be used to generate a passphrase as follows:
        >>> dictionary = ['eeny', 'meeny', 'miny', 'moe']
        >>> ' '.join(secret._symbols(dictionary, 4))
        'moe moe meeny miny'

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
        >>> secret._initiate('dux', account)
        >>> ' '.join([str(secret._get_index(100)) for i in range(10)])
        '90 89 14 76 51 70 83 23 91 47'

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
        >>> secret._initiate('dux', account)
        >>> ' '.join([str(secret._get_symbol(range(100))) for i in range(10)])
        '90 89 14 76 51 70 83 23 91 47'

        This function can be used to generate a birth date using:
        >>> def birthdate(secret, year, min_age=18, max_age=80):
        ...     return "%02d/%02d/%4d" % (
        ...         secret._get_symbol(range(12)) + 1,
        ...         secret._get_symbol(range(28)) + 1,
        ...         secret._get_symbol(range(year-max_age, year-min_age))
        ...     )
        >>> birthdate(secret, 2014)
        '06/14/1994'

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
    >>> secret._initiate('dux', account)
    >>> str(secret)
    'uv5X8p9RpgWc'

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
    >>> secret._initiate('dux', account)
    >>> str(secret)
    'terrorize mourner molar combo'

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
    >>> secret._initiate('dux', account)
    >>> str(secret)
    '0849'

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


# SecurityQuestion {{{1
class SecurityQuestion(Passphrase):
    """
    Identical to Passphrase() except the name must be specified when created 
    and is taken to be the security question.

    >>> import string
    >>> secret = SecurityQuestion('What city were you born in?')
    >>> secret._initiate('dux', account)
    >>> str(secret)
    'vandalize mausoleum canteen'

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
    >>> secret._initiate('dux', account)
    >>> str(secret)
    'p32Ao6jvVTRK'

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
    >>> secret._initiate('dux', account)
    >>> str(secret)
    '1963-08-04'

    For year, enter the year the entry that contains BirthDate was created.  
    Doing so anchors the age range. In this example, the creation date is 2015,
    the minimum age is 18 and the maximum age is 65, meaning that a birthdate
    will be chosen such that in 2015 the birth date could correspond to someone
    that is between 18 and 65 years old.

    You can use the fmt argument to change the way in which the date is 
    formatted::

    >>> secret = BirthDate(2015, 18, 65, fmt="M/D/YY")
    >>> secret._initiate('dux', account)
    >>> str(secret)
    '8/4/63'

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
