# Utilities

# License {{{1
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

# Imports {{{1
from .config import get_setting
from .dictionary import DICTIONARY
from .preferences import (
    SECRETS_MD5, CHARSETS_MD5, SETTINGS_DIR, CONFIG_FILENAME
)
from shlib import Run, to_path
from inform import codicil, error, os_error, warn
from textwrap import dedent, wrap
import hashlib

# gethostname {{{1
# returns short version of the hostname (the hostname without any domain name)
import socket
def gethostname():
    return socket.gethostname().split('.')[0]

# getusername {{{1
import getpass
def getusername():
    return getpass.getuser()

# generate_random_string {{{1
def generate_random_string(length=64):
    # Generate a random long string to act as the default password

    from string import ascii_letters, digits, punctuation
    import random
    rand = random.SystemRandom()

    # Create alphabet from letters, digits, and punctuation, but 
    # replace double quote with a space so password can be safely 
    # represented as a double-quoted string.
    alphabet = (ascii_letters + digits + punctuation).replace('"', ' ')

    password = ''
    for i in range(length):
        password += rand.choice(alphabet)
    return password


# validate_componenets {{{1
def validate_componenets():
    # Check that dictionary has not changed.
    # If the master password file exists, then self.data['dict_hash'] will 
    # exist, and we will compare the current hash for the dictionary 
    # against that stored in the master password file, otherwise we will 
    # compare against the one present when the program was configured.
    DICTIONARY.validate(get_setting('dict_hash'))

    # Check that secrets.py and charset.py have not changed
    for each, md5 in [
        ('secrets', SECRETS_MD5),
        ('charsets', CHARSETS_MD5)
    ]:
        src_dir = to_path(__file__).parent
        path = to_path(src_dir, each + '.py')
        try:
            contents = path.read_text()
        except IOError as err:
            path = to_path(src_dir, '..', each + '.py')
            try:
                contents = path.read_text()
            except IOError as err:
                error('%s: %s.' % (err.filename, err.strerror))
        hash = hashlib.md5(contents.encode('utf-8')).hexdigest()
        # Check that file has not changed.
        # If the master password file exists, then self.data['%s_hash'] 
        # will exist, and we will compare the current hash for the file 
        # against that stored in the master password file, otherwise we 
        # will compare against the one present when the program was 
        # configured.
        if hash != get_setting('%s_hash' % each, md5):
            warn("file contents have changed.", culprit=path)
            codicil(
                *wrap(dedent("""\
                    This results in passwords that are inconsistent with those
                    created in the past.  Change {settings}/{config} to contain
                    "{kind}_hash = '{hash}'".  Then use 'avendesora
                    changed' to assure that nothing has changed.
                """.format(
                    kind=each, settings=SETTINGS_DIR, config=CONFIG_FILENAME,
                    hash=hash
                ))),
                sep = '\n'
            )
