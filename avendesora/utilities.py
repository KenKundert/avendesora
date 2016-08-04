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
from shlib import Run, to_path
from inform import codicil, error, fatal, os_error, warn, is_str
from textwrap import dedent, wrap, indent
from pkg_resources import resource_filename
import hashlib
import os

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

    # find dictionary file
    dict_path = get_setting('dictionary_file')
    if not dict_path.is_file():
        # user did not provide a dictionary, so use the internal one
        dict_path = to_path(resource_filename(__name__, 'words'))

    # Check that files that are critical to the integrity of the generated
    # secrets have not changed
    for path, kind in [
        (to_path(resource_filename(__name__,  'secrets.py')), 'secrets_hash'),
        (to_path(resource_filename(__name__,  'charsets.py')), 'charsets_hash'),
        (dict_path, 'dict_hash'),
    ]:
        try:
            contents = path.read_text()
        except OSError as err:
            fatal(os_error(err))
        md5 = hashlib.md5(contents.encode('utf-8')).hexdigest()
        # Check that file has not changed.
        if md5 != get_setting(kind):
            warn("file contents have changed.", culprit=path)
            codicil(
                *wrap(dedent("""\
                    This results in passwords that are inconsistent with those
                    created in the past.  Change {hashes} to contain
                    "{kind} = '{md5}'".  Then use 'avendesora changed'
                    to assure that nothing has changed.
                """.format(
                    kind=kind, md5=md5,
                    hashes=get_setting('hashes_file'),
                ))),
                sep = '\n'
            )
# pager {{{1
def pager(text):
    program = os.environ.get('PAGER', 'less')
    Run([program], stdin=text, modes='Woes')

# two_columns {{{1
def two_columns(col1, col2, width=16, indent=True):
    indent = get_setting('indent') if indent else ''
    if len(col1) > width:
        return '%s%s\n%s%s%s' % (
            indent, col1, indent, '  '+width*' ', col2
        )
    else:
        return '%s%-*s  %s' % (indent, width, col1, col2) 

# to_python {{{1
def to_python(obj, _level=0):
    """Recursively convert object to string with reasonable formatting"""
    def leader(relative_level=0):
        return (_level+relative_level)*'    '
    output = []
    if type(obj) == dict:
        output += ['{']
        for key in sorted(obj.keys()):
            value = obj[key]
            output += ['%s%r: %s,' % (
                leader(1), key, to_python(value, _level+1)
            )]
        output += ['%s}' % (leader(0))]
    elif type(obj) == list:
        output += ['[']
        for each in obj:
            output += ['%s%s,' % (
                leader(1), to_python(each, _level+1)
            )]
        output += ['%s]' % (leader(0))]
    elif type(obj) == tuple:
        output += ['(']
        for each in obj:
            output += ['%s%s,' % (
                leader(1), to_python(each, _level+1)
            )]
        output += ['%s)' % (leader(0))]
    elif type(obj) == set:
        output += ['set([']
        for each in sorted(obj):
            output += ['%s%s,' % (
                leader(1), to_python(each, _level+1)
            )]
        output += ['%s])' % (leader(0))]
    elif is_str(obj) and '\n' in obj:
        output += ['"""' + indent(dedent(obj), leader(1)) + leader(0) + '"""']
    else:
        output += [obj.__repr__()]
    return '\n'.join(output)

