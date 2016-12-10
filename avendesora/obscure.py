# Obscure Information
#
# Defines classes used to conceal or encrypt information found in the accounts
# file.

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
from .gpg import GnuPG
from .utilities import error_source
from inform import (
    debug, Error, log, indent, is_str, output, terminate, warn, full_stop
)
from binascii import a2b_base64, b2a_base64, Error as BinasciiError
from textwrap import dedent
import re

# Utilities {{{1
def chunk(string, length):
    return (
        string[0+i:length+i] for i in range(0, len(string), length)
    )

def decorate_concealed(name, encoded):
    return '%s(%s)' % (
        name,
        '\n    "' + '"\n    "'.join(chunk(encoded, 60)) + '"\n'
    )

def group(pattern):
    return '(?:%s)' % pattern

STRING1 = group('"[^"]+"')
STRING2 = group("'[^']+'")
STRING3 = group("'''.+'''")
STRING4 = group('""".+"""')
SMPL_STRING = group('{s1}|{s2}'.format(s1=STRING1, s2=STRING2))
ML_STRING = group('{s3}|{s4}'.format(s3=STRING3, s4=STRING4))
ID = r"\w+"
DECORATED_LIST = re.compile(
    # Matches:
    #     Scrypt(
    #         "..."
    #         "..."
    #     )
    r"\s*({id})\s*\(\s*((?:{s}\s*)*)\s*\)\s*".format(id=ID, s=SMPL_STRING)
)
DECORATED_TEXT = re.compile(
    # Matches:
    #     GPG("""
    #         ...
    #         ...
    #     """)
    r"\s*({id})\s*\(\s*({s})\s*\)\s*".format(id=ID, s=ML_STRING),
    re.DOTALL,
)

# Obscure {{{1
class Obscure(object):
    # obscurers() {{{2
    @classmethod
    def obscurers(cls):
        for sub in cls.__subclasses__():
            if hasattr(sub, 'conceal') and hasattr(sub, 'reveal'):
                yield sub
                for each in sub.obscurers():
                    if hasattr(each, 'conceal') and hasattr(each, 'reveal'):
                        yield each

    # get_name() {{{2
    @classmethod
    def get_name(cls):
        try:
            return cls.NAME.lower()
        except AttributeError:
            # consider converting lower to upper case transitions in __name__ to
            # dashes.
            return cls.__name__.lower()

    # hide() {{{2
    @classmethod
    def hide(cls, text, encoding=None, decorate=False, symmetric=False):
        encoding = encoding.lower() if encoding else 'base64'
        for obscurer in cls.obscurers():
            if encoding == obscurer.get_name():
                return obscurer.conceal(text, decorate, symmetric=symmetric)
        raise Error('not found.', culprit=encoding)

    # show() {{{2
    @classmethod
    def show(cls, text):
        match = DECORATED_LIST.match(text)
        if match:
            name = match.group(1)
            value = ''.join([s.strip('"' "'") for s in match.group(2).split()])

            for obscurer in cls.obscurers():
                if name == obscurer.__name__:
                    return obscurer.reveal(value)
            raise Error('not found.', culprit=name)

        match = DECORATED_TEXT.match(text)
        if match:
            name = match.group(1)
            value = match.group(2)

            for obscurer in cls.obscurers():
                if name == obscurer.__name__:
                    return obscurer.reveal(value.strip('"' "'"))
            raise Error('not found.', culprit=name)

        return Hidden.reveal(text)

    # encodings() {{{2
    @classmethod
    def encodings(cls):
        for c in cls.obscurers():
            yield c.get_name(), dedent(getattr(c, 'DESC', '')).strip()

    # default encoding() {{{2
    @classmethod
    def default_encoding(cls):
        return Hidden.NAME

    # __repr__() {{{2
    def __repr__(self):
        return "Hidden('%s')" % (Obscure.hide(self.plaintext, 'base64'))

# Hidden {{{1
class Hidden(Obscure):
    # This decodes a string that is encoded in base64 to hide it from a casual
    # observer. But it is not encrypted. The original value can be trivially
    # recovered from the encoded version.
    NAME = 'base64'
    DESC = '''
        This encoding obscures but does not encrypt the text. It can
        protect text from observers that get a quick glance of the
        encoded text, but if they are able to capture it they can easily
        decode it.
    '''
    def __init__(self, ciphertext, secure=True, encoding='utf8'):
        self.ciphertext = ciphertext
        try:
            self.plaintext = a2b_base64(ciphertext).decode(encoding)
            self.secure = secure
        except BinasciiError as err:
            raise Error(
                'invalid value specified to Hidden(): %s.' % str(err),
                culprit=error_source()
            )

    def generate(self, field_name, field_key, account):
        # we don't need to do anything, but having this method marks this value
        # as being confidential
        pass

    def is_secure(self):
        return self.secure

    def __str__(self):
        return self.plaintext

    @staticmethod
    def conceal(plaintext, decorate=False, encoding=None, symmetric=False):
        encoding = encoding if encoding else get_setting('encoding')
        plaintext = str(plaintext).encode(encoding)
        encoded = b2a_base64(plaintext).rstrip().decode('ascii')
        if decorate:
            return decorate_concealed('Hidden', encoded)
        else:
            return encoded

    @staticmethod
    def reveal(value, encoding=None):
        encoding = encoding if encoding else get_setting('encoding')
        try:
            value = a2b_base64(value.encode('ascii'))
            return value.decode(encoding)
        except BinasciiError as err:
            raise Error('Unable to decode base64 string: %s.' % str(err))
        except UnicodeDecodeError:
            raise Error('Unable to decode base64 string.')

# GPG {{{1
class GPG(Obscure, GnuPG):
    DESC = '''
        This encoding fully encrypts/decrypts the text with GPG key.
        By default your GPG key is used, but you can specify symmetric
        encryption, in which case a passphrase is used.
    '''
    # This does a full GPG decryption.
    # To generate an entry for the GPG argument, you can use ...
    #     gpg -a -c filename
    # It will create filename.asc. Copy the contents of that file into the
    # argument.
    # This uses symmetric encryption to add an additional layer of protection.
    # Generally one would use their private key to protect the gpg file, and
    # then use a symmetric key, or perhaps a separate private key, to protect an
    # individual piece of data, like a master password.
    def __init__(self, ciphertext, secure=True, encoding='utf8'):
        self.ciphertext = ciphertext

    def generate(self, field_name, field_key, account):
        # must do this here in generate rather than in constructor to avoid
        # decrypting this, and perhaps asking for a passcode,  every time
        # Advendesora is run.
        plaintext = self.gpg.decrypt(dedent(self.ciphertext))
        if not plaintext.ok:
            msg = 'unable to decrypt argument to GPG()'
            try:
                msg = '%s: %s' % (msg, plaintext.stderr)
            except AttributeError:
                msg += '.'
            raise Error(msg, culprit=error_source())
        self.plaintext = plaintext

    def __str__(self):
        return str(self.plaintext)

    @classmethod
    def conceal(cls, plaintext, decorate=False, encoding=None, symmetric=False):
        encoding = encoding if encoding else get_setting('encoding')
        plaintext = str(plaintext).encode(encoding)
        gpg_ids = get_setting('gpg_ids', [])
        if is_str(gpg_ids):
            gpg_ids = gpg_ids.split()

        encrypted = cls.gpg.encrypt(
            plaintext, gpg_ids, armor=True, symmetric=bool(symmetric)
        )
        if not encrypted.ok:
            msg = ' '.join(cull([
                'unable to encrypt.',
                getattr(encrypted, 'stderr', None)
            ]))
            raise Error(msg)
        ciphertext = str(encrypted)
        if decorate:
            return 'GPG("""\n%s""")' % indent(ciphertext)
        else:
            return ciphertext

    @classmethod
    def reveal(cls, ciphertext, encoding=None):
        decrypted = cls.gpg.decrypt(dedent(ciphertext))
        if not decrypted.ok:
            msg = 'unable to decrypt argument to GPG()'
            try:
                msg = '%s: %s' % (msg, decrypted.stderr)
            except AttributeError:
                pass
            raise Error(full_stop(msg))
        plaintext = str(decrypted)
        return plaintext

# Scrypt {{{1
try:
    import scrypt
    class Scrypt(Obscure):
        # This encrypts/decrypts a string with scrypt. The user's key is used as the
        # passcode for this symmetric encryption.
        DESC = '''
            This encoding fully encrypts the text with your user key. Only
            you can decrypt it, secrets encoded with scrypt cannot be
            shared.
        '''
        def __init__(self, ciphertext, secure=True, encoding='utf8'):
            self.ciphertext = ciphertext
            self.encoding = encoding

        def generate(self, field_name, field_key, account):
            encrypted = a2b_base64(self.ciphertext.encode(self.encoding))
            self.plaintext = scrypt.decrypt(encrypted, get_setting('user_key'))

        def is_secure(self):
            return False

        def __str__(self):
            return str(self.plaintext).strip()

        @staticmethod
        def conceal(plaintext, decorate=False, encoding=None, symmetric=False):
            encoding = encoding if encoding else get_setting('encoding')
            plaintext = str(plaintext).encode(encoding)
            encrypted = scrypt.encrypt(
                plaintext, get_setting('user_key'), maxtime=0.25
            )
            encoded = b2a_base64(encrypted).rstrip().decode('ascii')
            if decorate:
                return decorate_concealed('Scrypt', encoded)
            else:
                return encoded

        @staticmethod
        def reveal(ciphertext, encoding=None):
            encrypted = a2b_base64(ciphertext)
            return scrypt.decrypt(encrypted, get_setting('user_key'))

except ImportError:
    pass
