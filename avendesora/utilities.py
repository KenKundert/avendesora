# Utilities

# License {{{1
# Copyright (C) 2016-2024 Kenneth S. Kundert
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
from .shlib import Run
from inform import Error, output, is_str, indent
from textwrap import dedent
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
def error_source(src):
    """Source of error

    src (int, Exception):
        If src is an exception is it assumed that a exception was caught and the
        source of the error should be determined from the exception.  In this
        case the traceback will be mined for the source of the error.  If the
        exception contains the attribute 'skip_tb_lvls' it is expected to be an
        integer and it is taken to be the depth of the traceback where the
        exception is expected to have originated.  If not found, 1 is assumed.

        If src is assumed that no exception has occurred yet, though the
        return value if this function will be used in a new exception that
        is in the process of being created.
        In this case, src must be an integer represents the stack level where
        the error has occurred. N represents N levels deep.
    """
    import traceback

    if isinstance(src, Exception):
        skip_lvls = getattr(src, 'skip_tb_lvls', None)
        tb = src.__traceback__
        trace = traceback.extract_tb(tb)
    else:
        skip_lvls = src
        trace = traceback.extract_stack()
    if skip_lvls:
        frame = trace[-skip_lvls]
    else:
        frame = trace[-1]
    return frame.filename, frame.name, f'line {frame.lineno}'

# query_user {{{1
def query_user(msg):
    highlight_color = get_setting('_highlight_color')
    msg = highlight_color(msg)

    try:
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
    readline.parse_and_bind("set editing-mode vi")
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
            label = label,
            elapsed = Quantity(t - start_time, 's'),
            delta = Quantity(t - last_time, 's'),
        ))
    else:
        start_time = t
    last_time = t
