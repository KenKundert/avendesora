# Concealers
#
# Classes that are used to conceal the value of a string.

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
from inform import fatal
from binascii import a2b_base64, b2a_base64, Error as BinasciiError
import sys

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

    def _initiate(self, name, account):
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
