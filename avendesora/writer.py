# Abraxas Password Writers
#
# Given a secret (password or passphrase) the writer is responsible for getting 
# it to the user in a reasonably secure manner.
#
# Copyright (C) 2016 Kenneth S. Kundert and Kale Kundert

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
from . import cursor
from .preferences import (
    INDENT, LABEL_COLOR, XDOTOOL, XSEL, ALL_FIELDS, INITIAL_AUTOTYPE_DELAY,
    DEFAULT_DISPLAY_TIME
)
from shlib import Run
from inform import fatal, Error, log, Color
from time import sleep
from textwrap import indent, dedent
import re

# Globals {{{1
LabelColor = Color(LABEL_COLOR, enable=Color.isTTY())

# Writer selection {{{1
def get_writer(display=True, clipboard=False, stdout=False):
    if not display:
        return KeyboardWriter()
    elif clipboard:
        return ClipboardWriter()
    elif stdout:
        return StdoutWriter()
    return TTY_Writer()

# Writer base class {{{1
class Writer:
    pass


# TTY_Writer class {{{1
class TTY_Writer(Writer):
    """Writes output to the user's TTY."""

    def display_field(self, account, field):
        name, key = account.split_name(field)
        is_secret = account.is_secret(name, key)
        try:
            value = str(account.get_value(name, key))
        except Error as err:
            err.terminate()
        sep = ' '
        if '\n' in value:
            if is_secret:
                warn(
                    'secret contains newlines, will not be fully concealed.',
                    culprit=key
                )
            else:
                value = indent(dedent(value), INDENT).strip('\n')
                sep = '\n'
        text = LabelColor(name + ':') + sep + str(value)

        log('Writing to TTY.')
        if is_secret:
            try:
                cursor.write(text + ' ')
                sleep(DEFAULT_DISPLAY_TIME)
                cursor.clear()
            except KeyboardInterrupt:
                cursor.clear()
        else:
            output(text)


# ClipboardWriter class {{{1
class ClipboardWriter(Writer):
    """Writes output to the system clipboard."""

    def display_field(self, account, field):
        name, key = account.split_name(field)
        is_secret = account.is_secret(name, key)
        try:
            value = str(account.get_value(name, key))
        except Error as err:
            err.terminate()

        # Use 'xsel' to put the information on the clipboard.
        # This represents a vulnerability, if someone were to replace xsel they
        # could steal my passwords. This is why I use an absolute path. I tried
        # to access the clipboard directly using GTK but I cannot get the code
        # to work.

        log('Writing to clipboard.')
        try:
            Run([XSEL, '-b', '-i'], 'soew', stdin=value)
        except Error as err:
            err.terminate()

        if is_secret:
            # produce count down
            try:
                for t in range(DEFAULT_DISPLAY_TIME, -1, -1):
                    cursor.write(str(t))
                    sleep(1)
                    cursor.clear()
            except KeyboardInterrupt:
                cursor.clear()

            # clear the clipboard
            try:
                Run([XSEL, '-b', '-c'], 'soew')
            except Error as err:
                err.terminate()

        # Use Gobject Introspection (GTK) to put the information on the
        # clipboard (for some reason I cannot get this to work).
        #try:
        #    from gi.repository import Gtk, Gdk
        #
        #    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        #    clipboard.set_text(text, len(text))
        #    clipboard.store()
        #    sleep(self.wait)
        #    clipboard.clear()
        #except ImportError:
        #    error('Clipboard is not supported.')


# StdoutWriter class {{{1
class StdoutWriter(Writer):
    """Writes to the standard output."""

    def display_field(self, account, field):
        name, key = account.split_name(field)
        try:
            print(str(account.get_value(name, key)))
        except Error as err:
            err.terminate()
# KeyboardWriter class {{{1
class KeyboardWriter(Writer):
    """Writes output via pseudo-keyboard."""

    def run_script(self, account, script):

        def run_xdotool(args, text=None):
            try:
                if args:
                    Run([XDOTOOL, 'getactivewindow'] + args, 'soeW')
                if text:
                    Run([XDOTOOL, '-'], 'soeW',
                        stdin="getactivewindow type '%s'" % text
                    )
            except OSError as err:
                fatal(os_error(err))

        def autotype(text):
            # Use 'xdotool' to mimic the keyboard.
            # A dollar sign in the argument to xdotool's type command is treated
            # as an environment variable, so it must also be separated out and
            # sent as a explicit 'key' stroke.
            #
            # 'type' must be the last action on a xdotool command line, so
            # special characters (dollar sign) following text demand another 
            # invocation of xdotool.
            #
            # It is desirable to pump the actions into standard input rather
            # than place them on the command line so no part of the password is 
            # visible using ps, however this mode seems flaky in xdotool. So 
            # I have compromised and only send the individual 'key' strokes on 
            # the command line and send the 'type' text through stdin. Still 
            # seems flaky though, especially with Firefox.

            regex = re.compile(r'([\n$]+)')

            def add_action(action, arg):
                actions.append((action, arg))

            # split string so that special characters are isolated
            actions = []
            segments = regex.split(text)
            for segment in segments:
                for char in segment:
                    if char == '\n':
                        add_action('key', 'Return')
                    elif char == '$':
                        add_action('key', 'dollar')
                    else:
                        add_action('type', segment)
                        break

            # Gather keys until 'type' is found, and then output gathered keys 
            # and type string all at once; this minimizes the number of times 
            # xdotool must be called.
            args = []
            for action, arg in actions:
                if action == 'type':
                    run_xdotool(args, arg)
                    args = []
                else:
                    args += [action, arg]
            run_xdotool(args)

        # Run the script
        regex = re.compile(r'({\w+})')
        out = []
        scrubbed = []
        for term in regex.split(script):
            if term and term[0] == '{' and term[-1] == '}':
                # we have found a command
                cmd = term[1:-1].lower()
                if cmd == 'tab':
                    out.append('\t')
                    scrubbed.append('\t')
                elif cmd == 'return':
                    out.append('\n')
                    scrubbed.append('\n')
                elif cmd.startswith('sleep '):
                    cmd = cmd.split()
                    try:
                        assert cmd[0] == 'sleep'
                        assert len(cmd) == 2
                        if out:
                            autotype(''.join(out))
                            out = []
                        sleep(cmd[1])
                        scrubbed.append('<sleep %s>' % cmd[1])
                    except (AssertionError, TypeError):
                        fatal('syntax error in keyboard script.', culprit=term)
                else:
                    name, key = account.split_name(cmd)
                    try:
                        value = str(account.get_value(name, key))
                        out.append(value)
                        if account.is_secret(name, key):
                            scrubbed.append('<%s>' % cmd)
                        else:
                            scrubbed.append('%s' % value)
                    except Error as err:
                        err.terminate()
            else:
                out.append(term)
        log('Autotyping "%s".' % ''.join(scrubbed))
        autotype(''.join(out))


