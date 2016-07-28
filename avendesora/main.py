#!/usr/bin/env python3
# Usage {{{1
"""
Avendesora Collaborative Password Generator

Generates passwords and pass phrases based on stored account information.

Usage:
    avendesora [options] <command> [<args>...]
    avendesora [options]

Options:
    -h, --help              Output basic usage information.

Commands:
{commands}

Use 'avendesora help <command>' for information on a specific command.
Use 'avendesora help' for list of available help topics.
"""
#    avendesora [options] [--stdout | --clipboard] [<account> [<field>]]

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
from .command import Command
from .config import read_config, get_setting
from .preferences import INDENT
from .gpg import GnuPG, BufferedFile
from inform import Inform, Error, fatal, output, terminate, debug
from shlib import to_path
from docopt import docopt
import sys


# Main {{{1
def main():
    # read config file
    read_config()

    # create summary of commands
    def summarize(cmd):
        names = ', '.join(cmd.NAMES)
        desc = cmd.DESC
        width = 16
        if len(names) > width:
            return '%s%s\n%s%s%s' % (INDENT, names, INDENT, '  '+width*' ', desc)
        else:
            return '%s%-*s  %s' % (INDENT, width, names, desc)
    commands = '\n'.join(summarize(c) for c in Command.commands_sorted())

    # read command line
    cmdline = docopt(__doc__.format(commands=commands), options_first=True)

    # initilize GPG
    GnuPG.initialize()

    # start logging
    logfile=BufferedFile(get_setting('log_file'))
    try:
        with Inform(logfile=logfile, hanging_indent=False):
            Command.execute(cmdline['<command>'], cmdline['<args>'])

    except KeyboardInterrupt:
        output('Terminated by user.')
    except Error as err:
        err.terminate()
    except OSError as err:
        fatal(os_error(err))

    terminate()
