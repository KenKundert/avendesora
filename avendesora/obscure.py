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
from inform import Error, error, log, output, terminate, warn
from binascii import a2b_base64, b2a_base64, Error as BinasciiError
from textwrap import dedent
import hashlib
import getpass
import gnupg

# Obscure {{{1
class Obscure:
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
    def hide(cls, text, encoding=None):
        encoding = encoding.lower() if encoding else 'base64'
        for obscurer in cls.obscurers():
            if encoding == obscurer.get_name():
                return obscurer.conceal(text)
        raise Error('not found.', culprit=encoding)

    # show() {{{2
    @classmethod
    def show(cls, text, encoding='base64'):
        encoding = encoding.lower() if encoding else 'base64'
        for obscurer in cls.obscurers():
            if encoding == obscurer.get_name():
                return obscurer.reveal(text)
        error('not found.', culprit=encoding)

    # encodings() {{{2
    @classmethod
    def encodings(cls):
        return [c.get_name() for c in cls.obscurers()]

    # __repr__() {{{2
    def __repr__(self):
        return "Hidden('%s')" % (Obscure.hide(self.plaintext, 'base64'))

# Hidden {{{1
class Hidden(Obscure):
    NAME = 'base64'
    # This decodes a string that is encoded in base64 to hide it from a casual
    # observer. But it is not encrypted. The original value can be trivially
    # recovered from the encoded version.
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
    def conceal(value, encoding=None):
        encoding = encoding if encoding else get_setting('encoding')
        if not value:
            try:
                value = getpass.getpass('text to hide: ')
            except EOFError:
                value = ''
        value = value.encode(encoding)
        return b2a_base64(value).rstrip().decode('ascii')

    @staticmethod
    def reveal(value, encoding=None):
        encoding = encoding if encoding else get_setting('encoding')
        if not value:
            try:
                value = getpass.getpass('text to hide: ')
            except EOFError:
                value = ''
        value = a2b_base64(value.encode('ascii'))
        return value.decode(encoding)

# GPG {{{1
class GPG(Obscure, GnuPG):
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
        #gpg_path = get_setting('gpg_path')
        #gpg_home = get_setting('gpg_home')
        #gpg_args = {}
        #if gpg_path:
        #    gpg_args.update({'gpgbinary': str(gpg_path)})
        #if gpg_home:
        #    gpg_args.update({'gnupghome': str(gpg_home)})
        #self.gpg = gnupg.GPG(**gpg_args)


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
        pass

    def __str__(self):
        return str(self.plaintext)


