# Script

# License {{{1
# Copyright (C) 2016-18 Kenneth S. Kundert
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
from .dialog import show_list_dialog
from .error import PasswordError
from textwrap import dedent
import re


# Script class {{{1
class Script:
    """Script

    Takes a string that contains attributes. Those attributes are expanded
    before being output. For example::

        Script('username: {username}, password: {passcode}')

    In this case, *{username}* and *{passcode}* are replaced by with the value
    of the corresponding account attribute. In addition to the account
    attributes, *{tab}* and *{return}* are replaced by a tab or carriage return
    character.

    Args:
        script (str):  The script.
    """
    SPLITTER = re.compile(r'({[\w. ]+})')

    def __init__(self, script='username: {username}, password: {passcode}'):
        self.script = script
        self.account = None
        self.rendered = None
        self.is_secret = None

    def initialize(self, account, field_name=None, field_key=None):
        self.account = account

    def __str__(self):
        if self.rendered is not None:
            return self.rendered
        self.is_secret = False
        components = []
        for cmd, val in self.components():
            components.append(val)
            if cmd == 'secret':
                self.is_secret = True
        return ''.join(components)

    def components(self, ask=False):
        """Iterates through the script.

        Yields a tuple for each component of a script. The tuple consists of the
        type of the component and the value of the component.  The type may be
        'tab' (a tab character), 'return' (a return character), 'text' (raw
        text), 'value' (the value of a field that is not a secret), 'sleep N' (a
        request to sleep N seconds), 'rate N' (set the autotype to 1 keystroke
        every N milliseconds), and finally a field name (the value of a
        field that is secret)..

        Args:
            ask (bool):
                Determines what happens when a composite field is encountered.
                If ask is true a dialog window is opened that that allows the
                user to select the desired member of the collection. If false, a
                PasswordError is raised.

        Raises:
            :exc:`avendesora.PasswordError`: attribute not found.
        """
        account = self.account
        for term in self.SPLITTER.split(self.script):
            if term and term[0] == '{' and term[-1] == '}':
                # we have found a command
                cmd = term[1:-1].lower()

                if cmd == 'tab':
                    val = '\t'
                elif cmd == 'return':
                    val = '\n'
                elif cmd.startswith('sleep '):
                    val = ''
                elif cmd.startswith('rate '):
                    val = ''
                elif cmd.startswith('remind '):
                    val = ''
                else:
                    name, key = account.split_field(cmd)
                    try:
                        value = account.get_scalar(name, key)
                    except PasswordError as e:
                        if ask and e.is_collection and len(e.collection):
                            # is composite value, ask user which one is desired
                            choices = e.collection
                            if len(choices) == 1:
                                choice = choices.keys()[0]
                            else:
                                choice = show_list_dialog(
                                    'Choose from %s' % name,
                                    sorted(choices.keys())
                                )
                                if choice is None:
                                    raise PasswordError(
                                        'user abort.',
                                        culprit = (
                                            account.get_name(),
                                            account.combine_field(name, key)
                                        )
                                    )
                            key = choices[choice]
                            value = account.get_scalar(name, key)
                        else:
                            raise
                    val = dedent(str(value)).strip()
                    if account.is_secret(name, key):
                        cmd = 'secret'
                    else:
                        cmd = 'value'
            else:
                cmd = 'text'
                val = term
                if not term:
                    continue
            yield cmd, val

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.script)
