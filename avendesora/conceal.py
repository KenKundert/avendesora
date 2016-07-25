# Conceal Information
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
from .gpg import GnuPG
from .dictionary import DICTIONARY
from inform import Error, error, fatal, log, output, terminate, warn
from binascii import a2b_base64, b2a_base64, Error as BinasciiError
from textwrap import dedent
import hashlib
import getpass
import gnupg
import sys

# Conceal {{{1
class Conceal:
    # concealers() {{{2
    @classmethod
    def concealers(cls):
        for sub in cls.__subclasses__():
            if hasattr(sub, 'conceal') and hasattr(sub, 'reveal'):
                yield sub
                for each in sub.concealers():
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
        for concealer in cls.concealers():
            if encoding == concealer.get_name():
                return concealer.conceal(text)
        error('not found.', culprit=encoding)

    # show() {{{2
    @classmethod
    def show(cls, text, encoding='base64'):
        encoding = encoding.lower() if encoding else 'base64'
        for concealer in cls.concealers():
            if encoding == concealer.get_name():
                return concealer.reveal(text)
        error('not found.', culprit=encoding)

    # encodings() {{{2
    @classmethod
    def encodings(cls):
        return [c.get_name() for c in cls.concealers()]


# Hidden {{{1
class Hidden(Conceal):
    NAME = 'base64'
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
    def conceal(value, encoding='utf8'):
        if not value:
            value = getpass.getpass('text to hide: ')
        value = value.encode(encoding)
        return b2a_base64(value).rstrip().decode('ascii')

    @staticmethod
    def reveal(value, encoding='utf8'):
        if not value:
            value = getpass.getpass('text to show: ')
        value = a2b_base64(value.encode('ascii'))
        return value.decode(encoding)

# GPG {{{1
class GPG(Conceal, GnuPG):
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
        #gpg_path = get_setting('gpg_path')
        #gpg_home = get_setting('gpg_home')
        #gpg_args = {}
        #if gpg_path:
        #    gpg_args.update({'gpgbinary': str(gpg_path)})
        #if gpg_home:
        #    gpg_args.update({'gnupghome': str(gpg_home)})
        #print('#####', gpg_args)
        #self.gpg = gnupg.GPG(**gpg_args)


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


