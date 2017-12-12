# Utilities

# License {{{1
# Copyright (C) 2016-17 Kenneth S. Kundert
#
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
from .error import PasswordError
from shlib import Run, to_path
from inform import codicil, os_error, output, warn, is_str, indent
from textwrap import dedent, wrap
from pkg_resources import resource_filename
from stat import ST_MODE
import hashlib
import os
import sys


# gethostname {{{1
# returns short version of the hostname (the hostname without any domain name)
def gethostname():
    import socket
    return socket.gethostname().split('.')[0]


# getusername {{{1
def getusername():
    import getpass
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


# validate_components {{{1
def validate_components():
    # check permissions on the settings directory
    path = get_setting('settings_dir')
    mask = get_setting('config_dir_mask')
    try:
        permissions = os.stat(path)[ST_MODE]
    except FileNotFoundError:
        raise Error('missing, must run initialize.', culprit=path)
    violation = permissions & mask
    recommended = permissions & ~mask & 0o777
    if violation:
        warn(
            "directory permissions are too loose.",
            "Recommend running 'chmod {:o} {}'.".format(recommended, path),
            culprit=path
        )

    # find dictionary file
    dict_path = get_setting('dictionary_file')
    if not dict_path.is_file():
        # user did not provide a dictionary, so use the internal one
        dict_path = to_path(resource_filename(__name__, 'words'))

    # Check that files that are critical to the integrity of the generated
    # secrets have not changed
    for path, kind in [
        (to_path(resource_filename(__name__, 'secrets.py')), 'secrets_hash'),
        (to_path(resource_filename(__name__, 'charsets.py')), 'charsets_hash'),
        (dict_path, 'dict_hash'),
    ]:
        try:
            contents = path.read_text()
        except OSError as e:
            raise PasswordError(os_error(e))
        md5 = hashlib.md5(contents.encode('utf-8')).hexdigest()
        # Check that file has not changed.
        if md5 != get_setting(kind):
            warn("file contents have changed.", culprit=path)
            lines = wrap(dedent("""\
                    This could result in passwords that are inconsistent with
                    those created in the past.  Use 'avendesora changed' to
                    assure that nothing has changed. Then, to suppress this
                    message, change {hashes} to contain:
                """.format(hashes=get_setting('hashes_file'))
            ))
            lines.append("     {kind} = '{md5}'".format(kind=kind, md5=md5))
            codicil(*lines, sep='\n')


# pager {{{1
def pager(text):
    program = get_setting('use_pager')
    if not is_str(program):
        program = os.environ.get('PAGER', 'less')
    if program:
        Run([program], stdin=text, modes='Woes')
    else:
        output(text)


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
    code = []
    if type(obj) == dict:
        code += ['{']
        for key in sorted(obj.keys()):
            value = obj[key]
            code += ['%s%r: %s,' % (
                leader(1), key, to_python(value, _level+1)
            )]
        code += ['%s}' % (leader(0))]
    elif type(obj) == list:
        code += ['[']
        for each in obj:
            code += ['%s%s,' % (
                leader(1), to_python(each, _level+1)
            )]
        code += ['%s]' % (leader(0))]
    elif type(obj) == tuple:
        code += ['(']
        for each in obj:
            code += ['%s%s,' % (
                leader(1), to_python(each, _level+1)
            )]
        code += ['%s)' % (leader(0))]
    elif type(obj) == set:
        code += ['set([']
        for each in sorted(obj):
            code += ['%s%s,' % (
                leader(1), to_python(each, _level+1)
            )]
        code += ['%s])' % (leader(0))]
    elif is_str(obj) and '\n' in obj:
        code += ['"""' + indent(dedent(obj), leader(1)) + leader(0) + '"""']
    else:
        code += [repr(obj)]
    return '\n'.join(code)


# error_source {{{1
def error_source():
    """Source of error
    Reads stack trace to determine filename and line number of error.
    """
    import traceback
    try:
        # return filename and lineno
        # context and content are also available
        import sys
        exc_cls, exc, tb = sys.exc_info()
        trace = traceback.extract_tb(tb)
        filename, line, context, text = trace[-1]
    except SyntaxError:
        # extract_stack() does not work on binary encrypted files. It generates
        # a syntax error that indicates that the file encoding is missing
        # because the function tries to read the file and sees binary data.
        # This is not a problem with ascii encrypted files as we don't actually
        # show code, which is gibberish, but does not require an encoding. In
        # this case, extract the line number from the trace.
        from .gpg import get_active_python_file
        filename = get_active_python_file()
        line = tb.tb_next.tb_lineno
    except IndexError:
        return None
    return filename, 'line %s' % line


# query_user {{{1
def query_user(msg):
    if sys.version_info.major < 3:
        return raw_input(msg + ' ')
    else:
        return input(msg + ' ')
