# Utilities

# License {{{1
# Copyright (C) 2016-18 Kenneth S. Kundert
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
from .shlib import Run
from inform import Error, output, is_str, indent, Color
from textwrap import dedent
import os
import sys

# Globals {{{1
HighlightColor = Color(
    color=get_setting('highlight_color'),
    scheme=get_setting('color_scheme'),
    enable=Color.isTTY()
)

# OSErrors {{{1
# Define OSError to include IOError with Python2 for backward compatibility
if sys.version_info.major < 3:
    OSErrors = (OSError, IOError)
else:
    OSErrors = (OSError,)


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


# pager {{{1
def pager(text):
    program = get_setting('use_pager')
    if not is_str(program):
        program = os.environ.get('PAGER', 'less')
    if program:
        try:
            Run([program], stdin=text, modes='WoEs')
            return
        except Error as e:
            e.report(culprit=program)
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
    msg = HighlightColor(msg)
    try:
        if sys.version_info.major < 3:
            return raw_input(msg + ' ').strip()
        else:
            return input(msg + ' ').strip()
    except EOFError:
        output()


# name_completion {{{1
def name_completion(prompt, choices):

    def complete(entered, state):
        for name in choices:
            if name.startswith(entered):
                if not state:
                    return name
                else:
                    state -= 1

    import readline
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)

    try:
        given = query_user(prompt)
    except EOFError:
        output()
    readline.set_completer(None)
    return given.strip() if given else given


# invert dictionary {{{1
def invert_dict(d, initial_keys=None):
    """Invert a dictionary

    Given a dictionary, return another where the values of the first are the
    keys of the second, and the values of the second are the set of keys from
    the first that contain that value.
    You can specify an minimum set of keys by providing *initial_keys*.
    """
    new = dict((k, set()) for k in initial_keys) if initial_keys else {}
    for k, v in d.items():
        new.setdefault(v, set())
        new[v].add(k)
    return new


# timer {{{1
start_time = 0
last_time = 0

def timer(label=None):
    from quantiphy import Quantity
    from time import time
    global start_time, last_time
    t = time()
    if label:
        print('{label}: delta = {delta}, cumulative = {elapsed}'.format(
            label,
            elapsed = Quantity(t - start_time, 's'),
            delta = Quantity(t - last_time, 's'),
        ))
    else:
        start_time = t
    last_time = t
