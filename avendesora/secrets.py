# Secrets
#
# GeneratedSecret is a base class that can be used to easily generate various
# types of secretes. Basically, it gathers together a collection of strings (the
# arguments of the constructor and the generate function) that are joined
# together and hashed. The 512 bit hash is then used to generate passwords,
# passphrases, and other secrets.
#

# Ignore {{{1
"""
The following code should be ignored. It is defined here for the use of the
doctests::

    >>> from avendesora.secrets import *
    >>> from avendesora.charsets import *
    >>> class Account(object):
    ...     def get_scalar(self, name, default=None):
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
# Copyright (C) 2016-2024 Kenneth S. Kundert
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
    ALPHANUMERIC, DIGITS, DISTINGUISHABLE, LOWERCASE, SYMBOLS, UPPERCASE, SHIFTED
)
from .config import get_setting
from .error import PasswordError
from .dictionary import Dictionary
from .obscure import ObscuredSecret
from inform import Error, conjoin, cull, log, output, terminate, warn, is_str
import math
import hashlib
import getpass
import re


# Exceptions {{{1
class SecretExhausted(PasswordError):
    """Secret exhausted.

    This generally results if the length of the requested secret is too long.

    This exception subclasses :exc:`avendesora.PasswordError`.
    """
    def __init__(self, **kwargs):
        self.args = ['entropy exhausted.']
        self.kwargs = kwargs


# Utilities {{{1
def shift_sort_join(chars, sep=''):
    # This sorts the characters so that all characters that require the shift
    # key to type are bundled together so that the passcode is easier to type
    return sep.join(sorted(chars, key=lambda x: x in SHIFTED))


def simple_join(chars, sep=''):
    return sep.join(chars)

def as_string(value, name):
    if value is None:
        return value
    if not is_str(value):
        raise PasswordError('expected a string.', skip_tb_lvls=3, culprit=name)
    return value

def as_integer(value, name):
    if value is None:
        return value
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise PasswordError('expected an integer.', skip_tb_lvls=3, culprit=name)
    return value

def as_int_or_str(value, name):
    if value is None:
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        pass
    if not is_str(value):
        raise PasswordError('expected an integer or a string.', skip_tb_lvls=3, culprit=name)
    return value

# GeneratedSecret {{{1
class GeneratedSecret(object):
    """Base class for generated secrets"""

    def __new__(cls, *args, **kwargs):
        self = super(GeneratedSecret, cls).__new__(cls)
        self.reset()
        self.is_secret = True
        return self

    def __init__(self):
        """Constructor

        This base class should not be instantiated. A constructor is only
        provided to so the doctests work on the helper methods.
        """
        self.master = self.version = None

    def get_key_seed(self, default=None):
        """Get key seed.

        The default behavior is to pass the key in as the argument, and then
        simply use it as the return value so it will be used as a seed.  However,
        the subclasses can override this method and provide an alternative seed.
        This is used by Question. It returns the question so that it used rather
        than the index.
        """
        return default

    def get_description(self):
        """Get description.

        Returns description of the secret.
        This is used by Question. It returns the question as the description.
        """
        return None

    def initialize(self, account, field_name, field_key=None):
        if self.secret:
            return
        account_name = account.get_name()
        account_seed = account.get_seed()
        if self.master is None:
            master_seed = account.get_scalar('master_seed', default=None)
            master_source = account.get_scalar('_master_source_', default=None)
        else:
            master_seed = self.master
            master_source = 'secret'
        if not master_seed:
            master_seed = get_setting('user_key')
            master_source = 'user_key'
        if not master_seed:
            try:
                try:
                    master_seed = getpass.getpass('master seed: ')
                    master_source = 'user'
                except EOFError:
                    output()
                if not master_seed:
                    warn("master seed is empty.")
            except (EOFError, KeyboardInterrupt):
                terminate()
        if self.version:
            version = self.version
        else:
            version = account.get_scalar('version', default='')

        log(
            'Generating secret ',
            '.'.join([str(n) for n in cull([account_name, field_name, field_key, version], remove=(None, ''))]),
            ', source of master seed: ',
            master_source,
            sep=''
        )
        field_key = self.get_key_seed(field_key)

        request_seed = account.request_seed()
        interactive_seed = ''
        if request_seed is True:
            try:
                interactive_seed = getpass.getpass('seed: ')
            except (EOFError, KeyboardInterrupt):
                terminate()
        elif callable(request_seed):
            interactive_seed = request_seed()
        elif is_str(request_seed):
            interactive_seed = request_seed
        elif request_seed:
            warn("invalid seed.")
        if request_seed and not interactive_seed:
            warn("seed is empty.")

        seeds = [
            master_seed,
            account_seed,
            field_name,
            field_key,
            version,
            interactive_seed
        ]
        self.set_seeds(seeds)
        assert self.pool

    def set_seeds(self, seeds):
        # Convert the seeds into 512 bit number
        key = ' '.join([str(seed) for seed in seeds])
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
        self.entropy = 0

    def reset(self):
        """
        A secret once generated will remember its value. With stealth secrets
        this is undesired because it prevents a new secret from being generated
        when account name changes. Calling this function causes the secret to
        forget its previously saved value, which requires generate to be
        called again.
        """
        self.secret = None
        self.pool = None

    def _partition(self, radix, num_partitions):
        """
        An iterator that returns a sequence of numbers. The length of the
        sequence is *num_partitions* and each number falls in the range
        [0:radix). The sequence of numbers seems random, but it is determined by
        the components that are passed into the constructor.

        >>> secret = GeneratedSecret()
        >>> secret.initialize(account, 'dux')
        >>> ' '.join([str(i) for i in secret._partition(100, 10)])
        '89 80 17 20 34 40 79 1 93 42'

        """
        assert self.pool, 'initialize() must be called first'
        max_index = radix - 1
        bits_per_chunk = (max_index).bit_length()
        self.entropy += num_partitions * math.log(radix, 2)

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

        >>> secret = GeneratedSecret()
        >>> secret.initialize(account, 'dux')
        >>> ' '.join(secret._symbols([str(i) for i in range(100)], 10))
        '89 80 17 20 34 40 79 1 93 42'

        This function can be used to generate a password as follows:
        >>> import string
        >>> alphabet = alphabet = string.ascii_letters + string.digits
        >>> ''.join(secret._symbols(alphabet, 16))
        'O7Dm0vMjJSMX2w30'

        This function can be used to generate a passphrase as follows:
        >>> dictionary = ['eeny', 'meeny', 'miny', 'moe']
        >>> ' '.join(secret._symbols(dictionary, 4))
        'eeny eeny moe miny'

        """
        assert self.pool, 'initialize() must be called first'
        if callable(alphabet):
            # Dictionary is passed as a function. That allows us to defer
            # reading the dictionary until we know it is really going to be
            # used as it is a slow operation.
            alphabet = alphabet()
        radix = len(alphabet)
        max_index = radix - 1
        bits_per_chunk = (max_index).bit_length()
        self.entropy += num_symbols * math.log(len(alphabet), 2)

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

        >>> secret = GeneratedSecret()
        >>> secret.initialize(account, 'dux')
        >>> ' '.join([str(secret._get_index(100)) for i in range(10)])
        '89 80 17 20 34 40 79 1 93 42'

        """
        assert self.pool, 'initialize() must be called first'
        max_index = radix - 1
        self.entropy += math.log(radix, 2)

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

        >>> secret = GeneratedSecret()
        >>> secret.initialize(account, 'dux')
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
        assert self.pool, 'initialize() must be called first'
        radix = len(alphabet)
        max_index = radix - 1
        self.entropy += math.log(len(alphabet), 2)

        if self.pool < max_index:
            raise SecretExhausted()

        index = self.pool % radix

        bits_per_chunk = (max_index).bit_length()
        self.pool = self.pool >> bits_per_chunk

        return alphabet[index]

    # __repr__() {{{2
    def __repr__(self):
        secret = ObscuredSecret.hide(str(self))
        if self.is_secret:
            return "Hidden('{}')".format(secret)
        else:
            return "Hidden('{}', is_secret=False)".format(secret)

    # __str__() {{{2
    def __str__(self):
        return self.render()


# Password {{{1
class Password(GeneratedSecret):
    """Generate password.

    Generates an arbitrary password by selecting symbols from the given
    alphabet at random. The entropy of the generated password is
    length*log2(len(alphabet)).

    Args:
        length (int):
            The number of items to draw from the alphabet when creating the
            password.
        alphabet (collection of symbols):
            The reservoir of legal symbols to use when creating the password. By
            default the set of easily distinguished alphanumeric characters are
            used (:attr:`avendesora.DISTINGUISHABLE`). Typically you would use
            the pre-imported character sets to construct the alphabet. For
            example, you might pass: :attr:`avendesora.ALPHANUMERIC` + '+=_&%#@'
        master (str):
            Overrides the master seed that is used when generating the password.
            Generally, there is one master seed shared by all accounts contained
            in an account file.  This argument overrides that behavior and
            instead explicitly specifies the master seed for this secret.
        version (str):
            An optional seed. Changing this value will change the generated
            password.
        shift_sort (bool):
            If true, the characters in the password will be sorted so that the
            characters that require the shift key when typing are placed last.
            This make the password easier to type.
        sep (str):
            A string that is placed between each symbol in the generated
            password.
        prefix (str):
            A string added to the front of the generated password.
        suffix (str):
            A string added to the end of the generated password.
        is_secret (bool):
            Should value be hidden from user unless explicitly requested.

    Raises:
        :exc:`avendesora.SecretExhausted`:
            The available entropy has been exhausted.
            This occurs when the requested length is too long.

    Examples::

        >>> secret = Password()
        >>> secret.initialize(account, 'dux')
        >>> str(secret)
        'tvA8mewbbig3'

        >>> secret = Password(shift_sort=True)
        >>> secret.initialize(account, 'flux')
        >>> str(secret)
        'wrncpipvtNPF'

    """
    # A relatively high level subclass of GeneratedSecret that is used to generate
    # passwords and passphrases. For passwords, pass in a string containing all
    # the characters available to the passwords as the alphabet and make *sep* an
    # empty string.  For passphrases, pass in a list of words as the alphabet and
    # make *sep* a space::

    def __init__(self,
        length = 12,
        *,
        alphabet = DISTINGUISHABLE,
        master = None,
        version = None,
        shift_sort = False,
        sep = '',
        prefix = '',
        suffix = '',
        is_secret = True,
    ):
        self.length = as_integer(length, 'length')
        self.alphabet = alphabet
        self.master = as_string(master, 'master')
        self.version = as_int_or_str(version, 'version')

        self.shift_sort = shift_sort
        self.sep = as_string(sep, 'sep')
        self.prefix = as_string(prefix, 'prefix')
        self.suffix = as_string(suffix, 'suffix')
        self.is_secret = is_secret

    def render(self):
        if self.secret:
            # it is important that this be called only once, because the secret
            # changes each time it is called
            return self.secret

        join = shift_sort_join if self.shift_sort else simple_join
        secret = self.secret = (
            self.prefix +
            join(self._symbols(self.alphabet, self.length), self.sep) +
            self.suffix
        )
        return secret


# Passphrase {{{1
class Passphrase(Password):
    """Generate passphrase.

    Similar to Password in that it generates an arbitrary passphrase by
    selecting symbols from the given alphabet at random, but in this case
    the default alphabet is a dictionary containing about 10,000 words.

    Args:
        length (int):
            The number of items to draw from the alphabet when creating the
            password.
        dictionary (str, [str], or callable):
            The reservoir of legal symbols to use when creating the
            password. If not given, or if 'default' is given, this is a
            predefined list of 10,000 words. If given as 'bip39' or
            'mnemonic', this is a predefined list of the 2048 bitcoin BIP-39
            seed words.  Any other string is treated as a path to a file
            that would contain the words. A list is taken as is. Finally,
            you can pass a function that returns the list of words, in which
            case the calling of the function is deferred until the words are
            needed, which is helpful if creating the list is slow.
        master (str):
            Overrides the master seed that is used when generating the password.
            Generally, there is one master seed shared by all accounts contained
            in an account file.  This argument overrides that behavior and
            instead explicitly specifies the master seed for this secret.
        version (str):
            An optional seed. Changing this value will change the generated
            password.
        sep (str):
            A string that is placed between each symbol in the generated
            password.
        prefix (str):
            A string added to the front of the generated password.
        suffix (str):
            A string added to the end of the generated password.
        is_secret (bool):
            Should value be hidden from user unless explicitly requested.

    Raises:
        :exc:`avendesora.SecretExhausted`:
            The available entropy has been exhausted.
            This occurs when the requested length is too long.

    Example::

        >>> secret = Passphrase()
        >>> secret.initialize(account, 'dux')
        >>> str(secret)
        'graveyard cockle intone provider'

    """

    def __init__(self,
        length = 4,
        *,
        dictionary = None,
        master = None,
        version = None,
        sep = ' ',
        prefix = '',
        suffix = '',
        is_secret = True,
    ):
        self.length = as_integer(length, 'length')
        if not dictionary or is_str(dictionary):
            self.alphabet = Dictionary(dictionary).get_words
        else:
            self.alphabet = dictionary
        self.master = as_string(master, 'master')
        self.version = as_int_or_str(version, 'version')
        self.shift_sort = False
        self.sep = as_string(sep, 'sep')
        self.prefix = as_string(prefix, 'prefix')
        self.suffix = as_string(suffix, 'suffix')
        self.is_secret = is_secret


# PIN {{{1
class PIN(Password):
    """Generate PIN.

    Similar to Password in that it generates an arbitrary PIN by
    selecting symbols from the given alphabet at random, but in this case
    the default alphabet is the set of digits (0-9).

    Args:
        length (int):
            The number of items to draw from the alphabet when creating the
            password.
        alphabet (collection of symbols):
            The reservoir of legal symbols to use when creating the password.
            By default the alphabet is :attr:`avendesora.DIGITS`.
        master (str):
            Overrides the master seed that is used when generating the password.
            Generally, there is one master seed shared by all accounts contained
            in an account file.  This argument overrides that behavior and
            instead explicitly specifies the master seed for this secret.
        version (str):
            An optional seed. Changing this value will change the generated
            password.
        sep (str):
            A string that is placed between each symbol in the generated
            password.
        prefix (str):
            A string added to the front of the generated password.
        suffix (str):
            A string added to the end of the generated password.
        is_secret (bool):
            Should value be hidden from user unless explicitly requested.

    Raises:
        :exc:`avendesora.SecretExhausted`:
            The available entropy has been exhausted.
            This occurs when the requested length is too long.

    Example::

        >>> secret = PIN()
        >>> secret.initialize(account, 'dux')
        >>> str(secret)
        '9301'

    """
    def __init__(self,
        length = 4,
        *,
        alphabet = DIGITS,
        master = None,
        version = None,
        is_secret = True,
    ):
        self.length = as_integer(length, 'length')
        self.alphabet = alphabet
        self.master = as_string(master, 'master')
        self.version = as_int_or_str(version, 'version')
        self.shift_sort = False
        self.sep = ''
        self.prefix = ''
        self.suffix = ''
        self.is_secret = is_secret


# Question {{{1
class Question(Passphrase):
    """Generate arbitrary answer to a given question.

    Similar to Passphrase() except a question must be specified when created
    and it is taken to be the security question. The question is used as a seed
    rather than the field name when generating the secret.

    Args:
        question (str):
            The question to be answered. Be careful. Changing the question in
            any way will change the resulting answer.
        length (int):
            The number of items to draw from the alphabet when creating the
            answer.
        dictionary (str, [str], or callable):
            The reservoir of legal symbols to use when creating the
            password. If not given, or if 'default' is given, this is a
            predefined list of 10,000 words. If given as 'bip39' or
            'mnemonic', this is a predefined list of the 2048 bitcoin BIP-39
            seed words.  Any other string is treated as a path to a file
            that would contain the words. A list is taken as is. Finally,
            you can pass a function that returns the list of words, in which
            case the calling of the function is deferred until the words are
            needed, which is helpful if creating the list is slow.
        master (str):
            Overrides the master seed that is used when generating the password.
            Generally, there is one master seed shared by all accounts contained
            in an account file.  This argument overrides that behavior and
            instead explicitly specifies the master seed for this secret.
        version (str):
            An optional seed. Changing this value will change the generated
            password.
        sep (str):
            A string that is placed between each symbol in the generated
            password.
        prefix (str):
            A string added to the front of the generated password.
        suffix (str):
            A string added to the end of the generated password.
        answer (str):
            The answer. If provided, this would override the generated answer.
            May be a string, or it may be an Obscured object.
        is_secret (bool):
            Should value be hidden from user unless explicitly requested.

    Raises:
        :exc:`avendesora.SecretExhausted`:
            The available entropy has been exhausted.
            This occurs when the requested length is too long.

    Example:

        >>> secret = Question('What city were you born in?')
        >>> secret.initialize(account, 'dux')
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
        length = 3,
        *,
        answer = None,
        dictionary = None,
        master = None,
        version = None,
        sep = ' ',
        prefix = '',
        suffix = '',
        is_secret = True,
    ):
        self.question = as_string(question, 'question')
        self.length = as_integer(length, 'length')
        if not dictionary or is_str(dictionary):
            self.alphabet = Dictionary(dictionary).get_words
        else:
            self.alphabet = dictionary
        self.master = as_string(master, 'master')
        self.version = as_int_or_str(version, 'version')
        self.shift_sort = False
        self.sep = as_string(sep, 'sep')
        self.prefix = as_string(prefix, 'prefix')
        self.suffix = as_string(suffix, 'suffix')
        self.is_secret = is_secret
        if answer:
            # answer allows the user to override the generator and simply
            # specify the answer. This is also used when producing the archive.
            self.secret = str(answer)

    # get_key_seed() {{{2
    def get_key_seed(self, default=None):
        return self.question

    # get_description() {{{2
    def get_description(self):
        return self.get_key_seed(None)

    # __repr__() {{{2
    def __repr__(self):
        return "Question(%r, answer=Hidden(%r))" % (
            self.question, ObscuredSecret.hide(str(self))
        )


# MixedPassword {{{1
class MixedPassword(GeneratedSecret):
    """Generate mixed password.

    A relatively low level method that is used to generate passwords from
    a heterogeneous collection of alphabets. This is used to satisfy the
    character type count requirements of many websites.  It is recommended that
    user use :class:`avendesora.PasswordRecipe` rather than directly use this class.

    Args:
        length (int):
            The number of items to draw from the various alphabets when creating
            the password.
        def_alphabet (collection of symbols):
            The alphabet to use when filling up the password after all the
            constraints are satisfied.
        requirements (list of tuples):
            Each tuple has two members, the first is a string or list that is
            used as an alphabet, and the second is a number that indicates how
            many symbols should be drawn from that alphabet.
        master (str):
            Overrides the master seed that is used when generating the password.
            Generally, there is one master seed shared by all accounts contained
            in an account file.  This argument overrides that behavior and
            instead explicitly specifies the master seed for this secret.
        version (str):
            An optional seed. Changing this value will change the generated
            answer.
        shift_sort (bool):
            If true, the characters in the password will be sorted so that the
            characters that require the shift key when typing are placed last.
            This make the password easier to type.
        is_secret (bool):
            Should value be hidden from user unless explicitly requested.

    Raises:
        :exc:`avendesora.SecretExhausted`:
            The available entropy has been exhausted.
            This occurs when the requested length is too long.

    Example::

        >>> secret = MixedPassword(
        ...     12, ALPHANUMERIC, [(LOWERCASE, 2), (UPPERCASE, 2), (DIGITS, 2)]
        ... )
        >>> secret.initialize(account, 'dux')
        >>> str(secret)
        'ZyW62fvxX0Fg'

    """
    def __init__(
        self,
        length,
        def_alphabet,
        requirements,
        *,
        master = None,
        version = None,
        shift_sort = False,
        is_secret = True,
    ):
        self.length = as_integer(length, 'length')
        self.def_alphabet = def_alphabet
        self.requirements = requirements
        self.master = as_string(master, 'master')
        self.version = as_int_or_str(version, 'version')
        self.shift_sort = shift_sort
        self.is_secret = is_secret

    def render(self):
        if self.secret:
            # It is important that this be called only once, because the secret
            # changes each time it is called.
            return self.secret

        # Choose the symbols used to create the password by drawing from the
        # various alphabets in order.
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
        join = shift_sort_join if self.shift_sort else simple_join
        secret = join(password)
        self.secret = secret
        return secret


# PasswordRecipe{{{1
class PasswordRecipe(MixedPassword):
    """Generate password from recipe.

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

    Args:
        recipe (str):
            A string that describes how the password should be constructed.
        def_alphabet (collection of symbols):
            The alphabet to use when filling up the password after all the
            constraints are satisfied.
        master (str):
            Overrides the master seed that is used when generating the password.
            Generally, there is one master seed shared by all accounts contained
            in an account file.  This argument overrides that behavior and
            instead explicitly specifies the master seed for this secret.
        version (str):
            An optional seed. Changing this value will change the generated
            answer.
        shift_sort (bool):
            If true, the characters in the password will be sorted so that the
            characters that require the shift key when typing are placed last.
            This make the password easier to type.
        is_secret (bool):
            Should value be hidden from user unless explicitly requested.

    Raises:
        :exc:`avendesora.SecretExhausted`:
            The available entropy has been exhausted.
            This occurs when the requested length is too long.

    Example::

        >>> secret = PasswordRecipe('12 2u 2d 2s')
        >>> secret.initialize(account, 'pux')
        >>> str(secret)
        '*m7Aqj=XBAs7'

    The c class is special in that it allow you to explicitly specify the
    characters to use. For example, '12 2c!@#$%^&=' directs that a 12 character
    password be generated, 2 of which are taken from the set !@#$%^&=::

        >>> secret = PasswordRecipe('12 2u 2d 2c!@#$%^&*')
        >>> secret.initialize(account, 'bux')
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
        *,
        def_alphabet = ALPHANUMERIC,
        master = None,
        version = None,
        shift_sort = False,
        is_secret = True,
    ):
        requirements = []
        try:
            parts = recipe.split()
        except (ValueError, AttributeError):
            raise PasswordError(
                f'recipe must be a string, found {recipe}.',
                skip_tb_lvls = 3
            )
        try:
            each = parts[0]
            length = int(each)
            for each in parts[1:]:
                num, kind, alphabet = self.PATTERN.match(each).groups()
                if self.ALPHABETS[kind]:
                    alphabet = self.ALPHABETS[kind]
                requirements += [(alphabet, int('0' + num))]
        except (ValueError, AttributeError):
            raise PasswordError(
                each, recipe, conjoin(self.ALPHABETS.keys(), conj=' or '),
                template="{0}: invalid term in recipe '{1}'. Choose from {2}.",
                skip_tb_lvls = 3
            )

        self.length = length
        self.def_alphabet = def_alphabet
        self.requirements = requirements
        self.master = as_string(master, 'master')
        self.version = as_int_or_str(version, 'version')
        self.shift_sort = shift_sort
        self.is_secret = is_secret


# BirthDate {{{1
class BirthDate(GeneratedSecret):
    """Generates an arbitrary birthdate for someone in a specified age range.

    This function can be used to generate an arbitrary date using::

        >>> secret = BirthDate(2015, 18, 65)
        >>> secret.initialize(account, 'dux')
        >>> str(secret)
        '1970-03-22'

    For year, enter the year the account that contains BirthDate was created.
    Doing so anchors the age range. In this example, the creation date is 2015,
    the minimum age is 18 and the maximum age is 65, meaning that a birthdate
    will be chosen such that in 2015 the birth date could correspond to someone
    that is between 18 and 65 years old.

    You can use the fmt argument to change the way in which the date is
    formatted::

        >>> secret = BirthDate(2015, 18, 65, fmt="M/D/YY")
        >>> secret.initialize(account, 'dux')
        >>> str(secret)
        '3/22/70'

    Args:
        year (int):
            The year the age range was established.
        min_age (int):
            The lower bound of the age range.
        max_age (int):
            The upper bound of the age range.
        fmt (str):
            Specifies the way the date is formatted. Consider an example date of
            6 July 1969. YY and YYYY are replaced by the year (69 or 1969). M,
            MM, MMM, and MMMM are replaced by the month (7, 07, Jul, or July). D
            and DD are replaced by the day (6 or 06).
        master (str):
            Overrides the master seed that is used when generating the password.
            Generally, there is one master seed shared by all accounts contained
            in an account file.  This argument overrides that behavior and
            instead explicitly specifies the master seed for this secret.
        version (str):
            An optional seed. Changing this value will change the generated
            answer.
        is_secret (bool):
            Should value be hidden from user unless explicitly requested.

    Raises:
        :exc:`avendesora.SecretExhausted`:
            The available entropy has been exhausted.
            This occurs when the requested length is too long.
    """
    def __init__(
        self,
        year,
        min_age = 18,
        max_age = 65,
        fmt = 'YYYY-MM-DD',
        *,
        master = None,
        version = None,
        is_secret = True,
    ):
        self.fmt = fmt
        self.last_year = year - min_age
        self.first_year = year - max_age
        self.master = as_string(master, 'master')
        self.version = as_int_or_str(version, 'version')
        self.is_secret = is_secret

    def render(self):
        if self.secret:
            # It is important that this be called only once, because the secret
            # changes each time it is called.
            return self.secret

        import arrow
        year = self._get_symbol(range(self.first_year, self.last_year))
        jan1 = arrow.get(year, 1, 1)
        dec31 = arrow.get(year, 12, 31)
        days_in_year = (dec31 - jan1).days
        day = self._get_symbol(range(days_in_year))
        birthdate = jan1.shift(days=day)
        secret = birthdate.format(self.fmt)
        self.secret = secret
        return secret


# Base58 {{{1
class Base58(GeneratedSecret):
    """Generates an arbitrary binary number encoded in base 58.

        >>> secret = Base58(bytes=32)
        >>> secret.initialize(account, 'nutz')
        >>> str(secret)
        '4BccsYuQp2r8B3An4NArYNXwCj9t5FqbYZrcsa4UVqD6'

    Args:
        bytes (int):
            The number of bytes of entropy encodede in the generated result.
        master (str):
            Overrides the master seed that is used when generating the password.
            Generally, there is one master seed shared by all accounts contained
            in an account file.  This argument overrides that behavior and
            instead explicitly specifies the master seed for this secret.
        version (str):
            An optional seed. Changing this value will change the generated
            result.
        is_secret (bool):
            Should value be hidden from user unless explicitly requested.

    Raises:
        :exc:`avendesora.SecretExhausted`:
            The available entropy has been exhausted.
            This occurs when the requested length is too long.
    """
    def __init__(
        self,
        bytes = 4,
        *,
        master = None,
        version = None,
        is_secret = True,
    ):
        self.bytes = bytes
        self.master = as_string(master, 'master')
        self.version = as_int_or_str(version, 'version')
        self.is_secret = is_secret

    def render(self):
        if self.secret:
            # It is important that this be called only once, because the secret
            # changes each time it is called.
            return self.secret

        from base58 import b58encode

        symbols = []
        for i in range(self.bytes):
            symbols.append(self._get_index(256))
        secret = b58encode(bytes(symbols)).decode('ascii')
        self.secret = secret
        return secret


if __name__ == "__main__":
    import doctest
    fail, total = doctest.testmod()
    output("{} failures out of {} tests".format(fail, total))
