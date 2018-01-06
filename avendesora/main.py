# Usage {{{1
"""
Avendesora Collaborative Password Generator

Generates passwords and pass phrases based on stored account information.

Usage:
    avendesora [options] <command> [<args>...]

Options:
    -h, --help        output basic usage information.

Commands:
{commands}

Use 'avendesora help <command>' for information on a specific command.
Use 'avendesora help' for list of available help topics.
"""

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
from .command import Command
from .config import read_config, get_setting
from .error import PasswordError
from .gpg import GnuPG, BufferedFile
from inform import Inform, Error, done, fatal, output, terminate, debug, os_error
from shlib import to_path
from docopt import docopt
import sys


# Main {{{1
def main():
    try:
        # read config file
        read_config()

        # read command line
        cmdline = docopt(
            __doc__.format(commands=Command.summarize()),
            options_first=True
        )

        # start logging
        logfile = BufferedFile(get_setting('log_file'), True)
        Inform(
            logfile=logfile, hanging_indent=False,
            stream_policy='header', notify_if_no_tty=True
        )

        # run the requested command
        Command.execute(cmdline['<command>'], cmdline['<args>'])
        done()
    except KeyboardInterrupt:
        output('\nTerminated by user.')
        terminate()
    except (PasswordError, Error) as e:
        e.terminate()
    except OSError as e:
        fatal(os_error(e))
    done()
